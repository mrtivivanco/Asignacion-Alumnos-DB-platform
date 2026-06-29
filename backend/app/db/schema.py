from datetime import date, datetime, time

from sqlalchemy import ForeignKeyConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    __tablename__ = "students"

    student_id: str = Field(primary_key=True, max_length=12)
    first_name: str = Field(nullable=False, max_length=80)
    last_name: str = Field(nullable=False, max_length=80)
    email: str | None = Field(default=None, unique=True, max_length=160)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DegreeProgram(SQLModel, table=True):
    __tablename__ = "degree_programs"

    program_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True, index=True, max_length=120)


class StudentProgram(SQLModel, table=True):
    __tablename__ = "student_programs"

    student_id: str = Field(foreign_key="students.student_id", primary_key=True, max_length=12)
    program_id: int = Field(foreign_key="degree_programs.program_id", primary_key=True)


class CourseSection(SQLModel, table=True):
    __tablename__ = "course_sections"
    __table_args__ = (UniqueConstraint("name", "section_code"),)

    course_section_id: int | None = Field(default=None, primary_key=True)
    section_code: str = Field(nullable=False, max_length=20)
    name: str = Field(nullable=False, max_length=120)
    capacity: int = Field(nullable=False, ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CourseEnrollment(SQLModel, table=True):
    __tablename__ = "course_enrollments"

    student_id: str = Field(foreign_key="students.student_id", primary_key=True, max_length=12)
    course_section_id: int = Field(foreign_key="course_sections.course_section_id", primary_key=True)
    enrolled_on: date | None = None


class ExamBlock(SQLModel, table=True):
    __tablename__ = "exam_blocks"
    __table_args__ = (UniqueConstraint("exam_date", "start_time"),)

    block_id: int = Field(primary_key=True)
    exam_date: date = Field(nullable=False)
    day_name: str = Field(nullable=False, max_length=20)
    start_time: time = Field(nullable=False)
    end_time: time = Field(nullable=False)


class Exam(SQLModel, table=True):
    __tablename__ = "exams"
    __table_args__ = (
        UniqueConstraint("course_section_id", "name", "creation_year"),
        UniqueConstraint("exam_id", "block_id"),
    )

    exam_id: int | None = Field(default=None, primary_key=True)
    course_section_id: int = Field(foreign_key="course_sections.course_section_id", nullable=False)
    block_id: int = Field(foreign_key="exam_blocks.block_id", nullable=False)
    name: str = Field(nullable=False, max_length=140)
    exam_type: str | None = Field(default=None, max_length=60)
    creation_year: int | None = Field(default=None, ge=2000, le=2100)
    pdf_file_id: str | None = Field(default=None, unique=True, max_length=24)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Room(SQLModel, table=True):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("room_number", "building"),)

    room_id: str = Field(primary_key=True, max_length=20)
    room_number: int = Field(nullable=False)
    building: str = Field(nullable=False, max_length=80)
    capacity: int = Field(nullable=False, ge=1)


class ExamRoomAssignment(SQLModel, table=True):
    __tablename__ = "exam_room_assignments"
    __table_args__ = (
        ForeignKeyConstraint(["exam_id", "block_id"], ["exams.exam_id", "exams.block_id"]),
        UniqueConstraint("exam_id", "block_id", "room_id"),
    )

    block_id: int = Field(foreign_key="exam_blocks.block_id", primary_key=True)
    room_id: str = Field(foreign_key="rooms.room_id", primary_key=True, max_length=20)
    exam_id: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class StudentExamAssignment(SQLModel, table=True):
    __tablename__ = "student_exam_assignments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["exam_id", "block_id", "room_id"],
            [
                "exam_room_assignments.exam_id",
                "exam_room_assignments.block_id",
                "exam_room_assignments.room_id",
            ],
        ),
        UniqueConstraint("student_id", "exam_id"),
        Index("ix_student_exam_assignments_room_block", "room_id", "block_id"),
    )

    student_id: str = Field(foreign_key="students.student_id", primary_key=True, max_length=12)
    block_id: int = Field(primary_key=True)
    exam_id: int = Field(nullable=False)
    room_id: str = Field(nullable=False, max_length=20)
    status: str = Field(default="assigned", nullable=False, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AssignmentConflict(SQLModel, table=True):
    __tablename__ = "assignment_conflicts"
    __table_args__ = (
        Index("ix_assignment_conflicts_exam_block", "exam_id", "block_id"),
        Index("ix_assignment_conflicts_student", "student_id"),
    )

    conflict_id: int | None = Field(default=None, primary_key=True)
    student_id: str | None = Field(default=None, foreign_key="students.student_id", max_length=12)
    exam_id: int = Field(foreign_key="exams.exam_id", nullable=False)
    block_id: int = Field(foreign_key="exam_blocks.block_id", nullable=False)
    room_id: str = Field(foreign_key="rooms.room_id", nullable=False, max_length=20)
    conflict_type: str = Field(nullable=False, max_length=60)
    reason: str = Field(nullable=False, max_length=300)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
