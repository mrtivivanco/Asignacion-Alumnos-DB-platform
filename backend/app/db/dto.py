import re
from datetime import date, datetime, time

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel


EXTRAORDINARY_SCHEDULES = {
    ("Martes", time(18, 0), time(20, 0)),
    ("Jueves", time(18, 0), time(20, 0)),
    ("Sabado", time(9, 0), time(11, 0)),
    ("Sabado", time(11, 0), time(13, 0)),
}

ASSIGNMENT_STATUSES = {"assigned", "cancelled", "absent"}

STUDENT_ID_PATTERN = re.compile(r"^\d{7,8}-[\dK]$")
DAY_NAMES_BY_WEEKDAY = {
    1: "Martes",
    3: "Jueves",
    5: "Sabado",
}


def normalize_student_id(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().upper()
    if not STUDENT_ID_PATTERN.fullmatch(normalized):
        raise ValueError("student_id must be a valid RUT formatted as 12345678-9")
    return normalized


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized == "":
        return None

    if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
        raise ValueError("email must be a valid email address")
    return normalized


def normalize_day_name(value: str) -> str:
    normalized = value.strip().capitalize()
    if normalized == "Sábado":
        return "Sabado"
    return normalized


def day_name_from_date(value: date) -> str:
    day_name = DAY_NAMES_BY_WEEKDAY.get(value.weekday())
    if day_name is None:
        raise ValueError("exam_date must be Tuesday, Thursday, or Saturday")
    return day_name


class StudentCreate(SQLModel):
    student_id: str = Field(min_length=7, max_length=12)
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    email: str | None = Field(default=None, max_length=160)

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        return normalize_student_id(value) or value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return normalize_email(value)


class StudentRead(StudentCreate):
    created_at: datetime


class StudentUpdate(SQLModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    email: str | None = Field(default=None, max_length=160)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return normalize_email(value)


class DegreeProgramCreate(SQLModel):
    name: str = Field(min_length=2, max_length=120)


class DegreeProgramRead(DegreeProgramCreate):
    program_id: int


class DegreeProgramUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)


class StudentProgramCreate(SQLModel):
    student_id: str
    program_id: int

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        return normalize_student_id(value) or value


class StudentProgramRead(StudentProgramCreate):
    student: StudentRead
    degree_program: DegreeProgramRead


class CourseSectionCreate(SQLModel):
    name: str = Field(min_length=2, max_length=120)
    capacity: int = Field(ge=1)


class CourseSectionRead(CourseSectionCreate):
    course_section_id: int
    created_at: datetime


class CourseSectionUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    capacity: int | None = Field(default=None, ge=1)


class CourseEnrollmentCreate(SQLModel):
    student_id: str
    course_section_id: int
    enrolled_on: date | None = None

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        return normalize_student_id(value) or value


class CourseEnrollmentRead(CourseEnrollmentCreate):
    student: StudentRead
    course_section: CourseSectionRead


class ExamBlockCreate(SQLModel):
    block_id: int = Field(ge=1)
    exam_date: date
    day_name: str = Field(min_length=2, max_length=20)
    start_time: time
    end_time: time

    @field_validator("day_name")
    @classmethod
    def validate_day_name(cls, value: str) -> str:
        return normalize_day_name(value)

    @model_validator(mode="after")
    def validate_extraordinary_schedule(self):
        derived_day = day_name_from_date(self.exam_date)
        if self.day_name != derived_day:
            raise ValueError("day_name must match exam_date")

        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

        schedule = (derived_day, self.start_time, self.end_time)
        if schedule not in EXTRAORDINARY_SCHEDULES:
            raise ValueError(
                "Los bloques solo pueden ser Martes 18:00-20:00, Jueves 18:00-20:00, "
                "Sabado 09:00-11:00 o Sabado 11:00-13:00"
            )
        self.day_name = derived_day
        return self


class ExamBlockRead(ExamBlockCreate):
    pass


class ExamBlockUpdate(SQLModel):
    exam_date: date | None = None
    day_name: str | None = Field(default=None, min_length=2, max_length=20)
    start_time: time | None = None
    end_time: time | None = None

    @field_validator("day_name")
    @classmethod
    def validate_day_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_day_name(value)

    @model_validator(mode="after")
    def validate_known_values(self):
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

        if self.exam_date is not None and self.day_name is not None:
            derived_day = day_name_from_date(self.exam_date)
            if self.day_name != derived_day:
                raise ValueError("day_name must match exam_date")

        if (
            self.day_name is not None
            and self.start_time is not None
            and self.end_time is not None
            and (self.day_name, self.start_time, self.end_time) not in EXTRAORDINARY_SCHEDULES
        ):
            raise ValueError(
                "Los bloques solo pueden ser Martes 18:00-20:00, Jueves 18:00-20:00, "
                "Sabado 09:00-11:00 o Sabado 11:00-13:00"
            )
        return self


class ExamCreate(SQLModel):
    course_section_id: int
    block_id: int | None = None
    name: str = Field(min_length=2, max_length=140)
    exam_type: str | None = Field(default=None, max_length=60)
    creation_year: int | None = Field(default=None, ge=2000, le=2100)


class ExamRead(ExamCreate):
    exam_id: int
    pdf_file_id: str | None = Field(default=None, min_length=24, max_length=24)
    created_at: datetime
    course_section: CourseSectionRead
    block: ExamBlockRead | None = None


class ExamUpdate(SQLModel):
    course_section_id: int | None = None
    block_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=140)
    exam_type: str | None = Field(default=None, max_length=60)
    creation_year: int | None = Field(default=None, ge=2000, le=2100)


class RoomCreate(SQLModel):
    room_id: str = Field(min_length=1, max_length=20)
    room_number: int = Field(ge=1)
    building: str = Field(min_length=1, max_length=80)
    capacity: int = Field(ge=1)


class RoomRead(RoomCreate):
    pass


class RoomUpdate(SQLModel):
    room_number: int | None = Field(default=None, ge=1)
    building: str | None = Field(default=None, min_length=1, max_length=80)
    capacity: int | None = Field(default=None, ge=1)


class ExamRoomAssignmentCreate(SQLModel):
    block_id: int
    room_id: str
    exam_id: int


class ExamRoomAssignmentRead(ExamRoomAssignmentCreate):
    created_at: datetime
    exam: ExamRead
    room: RoomRead
    block: ExamBlockRead


class ExamRoomAssignmentUpdate(SQLModel):
    exam_id: int | None = None


class StudentExamAssignmentCreate(SQLModel):
    student_id: str
    exam_id: int
    block_id: int
    room_id: str
    status: str = "assigned"

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        return normalize_student_id(value) or value

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = self.status.strip().lower()
        if normalized_status not in ASSIGNMENT_STATUSES:
            raise ValueError("Assignment status must be assigned, cancelled, or absent")
        self.status = normalized_status
        return self


class StudentExamAssignmentRead(StudentExamAssignmentCreate):
    created_at: datetime
    student: StudentRead
    exam: ExamRead
    room: RoomRead
    block: ExamBlockRead


class StudentExamAssignmentUpdate(SQLModel):
    status: str

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = self.status.strip().lower()
        if normalized_status not in ASSIGNMENT_STATUSES:
            raise ValueError("Assignment status must be assigned, cancelled, or absent")
        self.status = normalized_status
        return self


class AssignmentConflictCreate(SQLModel):
    student_id: str | None = Field(default=None, max_length=12)
    exam_id: int
    block_id: int
    room_id: str = Field(max_length=20)
    conflict_type: str = Field(min_length=2, max_length=60)
    reason: str = Field(min_length=2, max_length=300)

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str | None) -> str | None:
        return normalize_student_id(value)


class AssignmentConflictRead(AssignmentConflictCreate):
    conflict_id: int
    created_at: datetime
