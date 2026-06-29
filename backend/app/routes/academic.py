from collections.abc import Callable

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from ..crud import academic as crud
from ..db.config import SessionDep
from ..db.dto import (
    AssignmentConflictCreate,
    AssignmentConflictRead,
    CourseEnrollmentCreate,
    CourseEnrollmentRead,
    CourseExamAssignmentCreate,
    CourseExamAssignmentResult,
    CourseSectionCreate,
    CourseSectionRead,
    CourseSectionUpdate,
    DegreeProgramCreate,
    DegreeProgramRead,
    DegreeProgramUpdate,
    ExamBlockCreate,
    ExamBlockRead,
    ExamBlockUpdate,
    ExamCreate,
    ExamRead,
    ExamUpdate,
    ExamRoomAssignmentCreate,
    ExamRoomAssignmentRead,
    ExamRoomAssignmentUpdate,
    RoomCreate,
    RoomRead,
    RoomUpdate,
    StudentCreate,
    StudentExamAssignmentCreate,
    StudentExamAssignmentRead,
    StudentExamAssignmentUpdate,
    StudentUpdate,
    StudentProgramCreate,
    StudentProgramRead,
    StudentRead,
)
from ..db.schema import (
    AssignmentConflict,
    CourseEnrollment,
    CourseSection,
    DegreeProgram,
    Exam,
    ExamBlock,
    ExamRoomAssignment,
    Room,
    Student,
    StudentExamAssignment,
    StudentProgram,
)
from ..storage.exam_pdfs import delete_exam_pdf


router = APIRouter(prefix="/api")

STUDENTS_TAG = "Students"
DEGREE_PROGRAMS_TAG = "Degree Programs"
STUDENT_PROGRAMS_TAG = "Student Programs"
COURSE_SECTIONS_TAG = "Course Sections"
COURSE_ENROLLMENTS_TAG = "Course Enrollments"
EXAM_BLOCKS_TAG = "Exam Blocks"
EXAMS_TAG = "Exams"
ROOMS_TAG = "Rooms"
EXAM_ROOM_ASSIGNMENTS_TAG = "Exam Room Assignments"
STUDENT_EXAM_ASSIGNMENTS_TAG = "Student Exam Assignments"
ASSIGNMENT_CONFLICTS_TAG = "Assignment Conflicts"


def conflict_safe(session: SessionDep, action: Callable[[], object]):
    try:
        return action()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Record violates a unique or primary key constraint") from exc


def require_exists(session: SessionDep, model: type, key: object, label: str):
    item = session.get(model, key)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return item


def require_exam_room_assignment(session: SessionDep, exam_id: int, block_id: int, room_id: str):
    exam_room_assignment = crud.get_exam_room_assignment_for_exam(session, exam_id, block_id, room_id)
    if exam_room_assignment is None:
        raise HTTPException(
            status_code=409,
            detail="The exam does not have that room enabled for that block",
        )
    return exam_room_assignment


def validate_exam_block(exam: Exam, block_id: int) -> None:
    if exam.block_id != block_id:
        raise HTTPException(
            status_code=409,
            detail="The selected block does not match the exam block",
        )


def validate_exam_block_update(block: ExamBlock, data: ExamBlockUpdate) -> None:
    try:
        ExamBlockCreate(
            block_id=block.block_id,
            exam_date=data.exam_date if data.exam_date is not None else block.exam_date,
            day_name=data.day_name if data.day_name is not None else block.day_name,
            start_time=data.start_time if data.start_time is not None else block.start_time,
            end_time=data.end_time if data.end_time is not None else block.end_time,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "validation_error",
                "message": "Exam block update is invalid",
                "errors": exc.errors(),
            },
        ) from exc


def record_assignment_conflict(
    session: SessionDep,
    *,
    student_id: str | None,
    exam_id: int,
    block_id: int,
    room_id: str,
    conflict_type: str,
    reason: str,
) -> str:
    crud.create_assignment_conflict(
        session,
        AssignmentConflictCreate(
            student_id=student_id,
            exam_id=exam_id,
            block_id=block_id,
            room_id=room_id,
            conflict_type=conflict_type,
            reason=reason,
        ),
    )
    return reason


def ensure_room_capacity(session: SessionDep, room: Room, block_id: int) -> None:
    if crud.count_room_assignments(session, block_id, room.room_id) >= room.capacity:
        raise HTTPException(status_code=409, detail="Room capacity is already full for this block")


@router.get("/students", response_model=list[StudentRead], tags=[STUDENTS_TAG])
def list_students(session: SessionDep, q: str | None = None):
    return [crud.student_to_read(student) for student in crud.list_students(session, q=q)]


@router.post("/students", response_model=StudentRead, status_code=status.HTTP_201_CREATED, tags=[STUDENTS_TAG])
def create_student(student_data: StudentCreate, session: SessionDep):
    if crud.get_student(session, student_data.student_id) is not None:
        raise HTTPException(status_code=409, detail="Student already exists")
    student = conflict_safe(session, lambda: crud.create_student(session, student_data))
    return crud.student_to_read(student)


@router.patch("/students/{student_id}", response_model=StudentRead, tags=[STUDENTS_TAG])
def update_student(student_id: str, student_data: StudentUpdate, session: SessionDep):
    student = require_exists(session, Student, student_id, "Student")
    updated = conflict_safe(session, lambda: crud.update_student(session, student, student_data))
    return crud.student_to_read(updated)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[STUDENTS_TAG])
def delete_student(student_id: str, session: SessionDep):
    student = require_exists(session, Student, student_id, "Student")
    conflict_safe(session, lambda: crud.delete_item(session, student))


@router.get("/degree-programs", response_model=list[DegreeProgramRead], tags=[DEGREE_PROGRAMS_TAG])
def list_degree_programs(session: SessionDep, q: str | None = None):
    return [crud.degree_program_to_read(program) for program in crud.list_degree_programs(session, q=q)]


@router.post(
    "/degree-programs",
    response_model=DegreeProgramRead,
    status_code=status.HTTP_201_CREATED,
    tags=[DEGREE_PROGRAMS_TAG],
)
def create_degree_program(program_data: DegreeProgramCreate, session: SessionDep):
    program = conflict_safe(session, lambda: crud.create_degree_program(session, program_data))
    return crud.degree_program_to_read(program)


@router.patch("/degree-programs/{program_id}", response_model=DegreeProgramRead, tags=[DEGREE_PROGRAMS_TAG])
def update_degree_program(program_id: int, program_data: DegreeProgramUpdate, session: SessionDep):
    program = require_exists(session, DegreeProgram, program_id, "Degree program")
    updated = conflict_safe(session, lambda: crud.update_degree_program(session, program, program_data))
    return crud.degree_program_to_read(updated)


@router.delete("/degree-programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[DEGREE_PROGRAMS_TAG])
def delete_degree_program(program_id: int, session: SessionDep):
    program = require_exists(session, DegreeProgram, program_id, "Degree program")
    conflict_safe(session, lambda: crud.delete_item(session, program))


@router.get("/student-programs", response_model=list[StudentProgramRead], tags=[STUDENT_PROGRAMS_TAG])
def list_student_programs(session: SessionDep):
    return [crud.student_program_to_read(session, item) for item in crud.list_student_programs(session)]


@router.post(
    "/student-programs",
    response_model=StudentProgramRead,
    status_code=status.HTTP_201_CREATED,
    tags=[STUDENT_PROGRAMS_TAG],
)
def create_student_program(data: StudentProgramCreate, session: SessionDep):
    require_exists(session, Student, data.student_id, "Student")
    require_exists(session, DegreeProgram, data.program_id, "Degree program")
    item = conflict_safe(session, lambda: crud.create_student_program(session, data))
    return crud.student_program_to_read(session, item)


@router.delete(
    "/student-programs/{student_id}/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[STUDENT_PROGRAMS_TAG],
)
def delete_student_program(student_id: str, program_id: int, session: SessionDep):
    item = require_exists(session, StudentProgram, (student_id, program_id), "Student program")
    conflict_safe(session, lambda: crud.delete_item(session, item))


@router.get("/course-sections", response_model=list[CourseSectionRead], tags=[COURSE_SECTIONS_TAG])
def list_course_sections(session: SessionDep, q: str | None = None):
    return [crud.course_section_to_read(section) for section in crud.list_course_sections(session, q=q)]


@router.post(
    "/course-sections",
    response_model=CourseSectionRead,
    status_code=status.HTTP_201_CREATED,
    tags=[COURSE_SECTIONS_TAG],
)
def create_course_section(section_data: CourseSectionCreate, session: SessionDep):
    section = conflict_safe(session, lambda: crud.create_course_section(session, section_data))
    return crud.course_section_to_read(section)


@router.patch("/course-sections/{course_section_id}", response_model=CourseSectionRead, tags=[COURSE_SECTIONS_TAG])
def update_course_section(course_section_id: int, section_data: CourseSectionUpdate, session: SessionDep):
    section = require_exists(session, CourseSection, course_section_id, "Course section")
    updated = conflict_safe(session, lambda: crud.update_course_section(session, section, section_data))
    return crud.course_section_to_read(updated)


@router.delete("/course-sections/{course_section_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[COURSE_SECTIONS_TAG])
def delete_course_section(course_section_id: int, session: SessionDep):
    section = require_exists(session, CourseSection, course_section_id, "Course section")
    conflict_safe(session, lambda: crud.delete_item(session, section))


@router.get("/course-enrollments", response_model=list[CourseEnrollmentRead], tags=[COURSE_ENROLLMENTS_TAG])
def list_course_enrollments(
    session: SessionDep,
    student_id: str | None = None,
    course_section_id: int | None = None,
):
    return [
        crud.course_enrollment_to_read(session, item)
        for item in crud.list_course_enrollments(
            session,
            student_id=student_id,
            course_section_id=course_section_id,
        )
    ]


@router.post(
    "/course-enrollments",
    response_model=CourseEnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    tags=[COURSE_ENROLLMENTS_TAG],
)
def create_course_enrollment(data: CourseEnrollmentCreate, session: SessionDep):
    require_exists(session, Student, data.student_id, "Student")
    require_exists(session, CourseSection, data.course_section_id, "Course section")
    item = conflict_safe(session, lambda: crud.create_course_enrollment(session, data))
    return crud.course_enrollment_to_read(session, item)


@router.delete(
    "/course-enrollments/{student_id}/{course_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[COURSE_ENROLLMENTS_TAG],
)
def delete_course_enrollment(student_id: str, course_section_id: int, session: SessionDep):
    item = require_exists(session, CourseEnrollment, (student_id, course_section_id), "Course enrollment")
    conflict_safe(session, lambda: crud.delete_item(session, item))


@router.get("/exam-blocks", response_model=list[ExamBlockRead], tags=[EXAM_BLOCKS_TAG])
def list_exam_blocks(session: SessionDep):
    return [crud.exam_block_to_read(block) for block in crud.list_exam_blocks(session)]


@router.post("/exam-blocks", response_model=ExamBlockRead, status_code=status.HTTP_201_CREATED, tags=[EXAM_BLOCKS_TAG])
def create_exam_block(block_data: ExamBlockCreate, session: SessionDep):
    block = conflict_safe(session, lambda: crud.create_exam_block(session, block_data))
    return crud.exam_block_to_read(block)


@router.patch("/exam-blocks/{block_id}", response_model=ExamBlockRead, tags=[EXAM_BLOCKS_TAG])
def update_exam_block(block_id: int, block_data: ExamBlockUpdate, session: SessionDep):
    block = require_exists(session, ExamBlock, block_id, "Exam block")
    validate_exam_block_update(block, block_data)
    updated = conflict_safe(session, lambda: crud.update_exam_block(session, block, block_data))
    return crud.exam_block_to_read(updated)


@router.delete("/exam-blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[EXAM_BLOCKS_TAG])
def delete_exam_block(block_id: int, session: SessionDep):
    block = require_exists(session, ExamBlock, block_id, "Exam block")
    conflict_safe(session, lambda: crud.delete_item(session, block))


@router.get("/exams", response_model=list[ExamRead], tags=[EXAMS_TAG])
def list_exams(
    session: SessionDep,
    q: str | None = None,
    block_id: int | None = None,
    course_section_id: int | None = None,
    has_pdf: bool | None = None,
):
    return [
        crud.exam_to_read(session, exam)
        for exam in crud.list_exams(
            session,
            q=q,
            block_id=block_id,
            course_section_id=course_section_id,
            has_pdf=has_pdf,
        )
    ]


@router.post("/exams", response_model=ExamRead, status_code=status.HTTP_201_CREATED, tags=[EXAMS_TAG])
def create_exam(exam_data: ExamCreate, session: SessionDep):
    require_exists(session, CourseSection, exam_data.course_section_id, "Course section")
    require_exists(session, ExamBlock, exam_data.block_id, "Exam block")
    exam = conflict_safe(session, lambda: crud.create_exam(session, exam_data))
    return crud.exam_to_read(session, exam)


@router.patch("/exams/{exam_id}", response_model=ExamRead, tags=[EXAMS_TAG])
def update_exam(exam_id: int, exam_data: ExamUpdate, session: SessionDep):
    exam = require_exists(session, Exam, exam_id, "Exam")
    if exam_data.course_section_id is not None:
        require_exists(session, CourseSection, exam_data.course_section_id, "Course section")
    if exam_data.block_id is not None:
        require_exists(session, ExamBlock, exam_data.block_id, "Exam block")
    updated = conflict_safe(session, lambda: crud.update_exam(session, exam, exam_data))
    return crud.exam_to_read(session, updated)


@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[EXAMS_TAG])
def delete_exam(exam_id: int, session: SessionDep):
    exam = require_exists(session, Exam, exam_id, "Exam")
    pdf_file_id = exam.pdf_file_id
    conflict_safe(session, lambda: crud.delete_item(session, exam))
    if pdf_file_id:
        try:
            delete_exam_pdf(pdf_file_id)
        except Exception:
            pass


@router.get("/rooms", response_model=list[RoomRead], tags=[ROOMS_TAG])
def list_rooms(session: SessionDep, q: str | None = None, building: str | None = None):
    return [crud.room_to_read(room) for room in crud.list_rooms(session, q=q, building=building)]


@router.post("/rooms", response_model=RoomRead, status_code=status.HTTP_201_CREATED, tags=[ROOMS_TAG])
def create_room(room_data: RoomCreate, session: SessionDep):
    room = conflict_safe(session, lambda: crud.create_room(session, room_data))
    return crud.room_to_read(room)


@router.patch("/rooms/{room_id}", response_model=RoomRead, tags=[ROOMS_TAG])
def update_room(room_id: str, room_data: RoomUpdate, session: SessionDep):
    room = require_exists(session, Room, room_id, "Room")
    if room_data.capacity is not None and room_data.capacity < crud.max_room_assignments(session, room_id):
        raise HTTPException(status_code=409, detail="Room capacity cannot be lower than existing assignments")
    updated = conflict_safe(session, lambda: crud.update_room(session, room, room_data))
    return crud.room_to_read(updated)


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[ROOMS_TAG])
def delete_room(room_id: str, session: SessionDep):
    room = require_exists(session, Room, room_id, "Room")
    conflict_safe(session, lambda: crud.delete_item(session, room))


@router.get(
    "/exam-room-assignments",
    response_model=list[ExamRoomAssignmentRead],
    tags=[EXAM_ROOM_ASSIGNMENTS_TAG],
)
def list_exam_room_assignments(
    session: SessionDep,
    exam_id: int | None = None,
    block_id: int | None = None,
    room_id: str | None = None,
):
    return [
        crud.exam_room_assignment_to_read(session, assignment)
        for assignment in crud.list_exam_room_assignments(
            session,
            exam_id=exam_id,
            block_id=block_id,
            room_id=room_id,
        )
    ]


@router.post(
    "/exam-room-assignments",
    response_model=ExamRoomAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    tags=[EXAM_ROOM_ASSIGNMENTS_TAG],
)
def create_exam_room_assignment(data: ExamRoomAssignmentCreate, session: SessionDep):
    exam = require_exists(session, Exam, data.exam_id, "Exam")
    require_exists(session, Room, data.room_id, "Room")
    require_exists(session, ExamBlock, data.block_id, "Exam block")
    validate_exam_block(exam, data.block_id)
    assignment = conflict_safe(session, lambda: crud.create_exam_room_assignment(session, data))
    return crud.exam_room_assignment_to_read(session, assignment)


@router.patch(
    "/exam-room-assignments/{block_id}/{room_id}",
    response_model=ExamRoomAssignmentRead,
    tags=[EXAM_ROOM_ASSIGNMENTS_TAG],
)
def update_exam_room_assignment(
    block_id: int,
    room_id: str,
    data: ExamRoomAssignmentUpdate,
    session: SessionDep,
):
    assignment = require_exists(session, ExamRoomAssignment, (block_id, room_id), "Exam room assignment")
    if data.exam_id is not None:
        exam = require_exists(session, Exam, data.exam_id, "Exam")
        validate_exam_block(exam, block_id)
    updated = conflict_safe(session, lambda: crud.update_exam_room_assignment(session, assignment, data))
    return crud.exam_room_assignment_to_read(session, updated)


@router.delete(
    "/exam-room-assignments/{block_id}/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[EXAM_ROOM_ASSIGNMENTS_TAG],
)
def delete_exam_room_assignment(block_id: int, room_id: str, session: SessionDep):
    assignment = require_exists(session, ExamRoomAssignment, (block_id, room_id), "Exam room assignment")
    conflict_safe(session, lambda: crud.delete_item(session, assignment))


@router.get(
    "/student-exam-assignments",
    response_model=list[StudentExamAssignmentRead],
    tags=[STUDENT_EXAM_ASSIGNMENTS_TAG],
)
def list_student_exam_assignments(
    session: SessionDep,
    student_id: str | None = None,
    exam_id: int | None = None,
    block_id: int | None = None,
):
    return [
        crud.student_exam_assignment_to_read(session, assignment)
        for assignment in crud.list_student_exam_assignments(
            session,
            student_id=student_id,
            exam_id=exam_id,
            block_id=block_id,
        )
    ]


@router.post(
    "/student-exam-assignments",
    response_model=StudentExamAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    tags=[STUDENT_EXAM_ASSIGNMENTS_TAG],
)
def create_student_exam_assignment(data: StudentExamAssignmentCreate, session: SessionDep):
    require_exists(session, Student, data.student_id, "Student")
    exam = require_exists(session, Exam, data.exam_id, "Exam")
    room = require_exists(session, Room, data.room_id, "Room")
    require_exists(session, ExamBlock, data.block_id, "Exam block")
    validate_exam_block(exam, data.block_id)

    if not crud.student_is_enrolled_in_section(session, data.student_id, exam.course_section_id):
        record_assignment_conflict(
            session,
            student_id=data.student_id,
            exam_id=data.exam_id,
            block_id=data.block_id,
            room_id=data.room_id,
            conflict_type="not_enrolled",
            reason="The student is not enrolled in the course section associated with this exam",
        )
        raise HTTPException(
            status_code=409,
            detail="The student is not enrolled in the course section associated with this exam",
        )

    if crud.get_student_exam_assignment(session, data.student_id, data.block_id) is not None:
        reason = f"{data.student_id}: already has an exam assigned in block {data.block_id}"
        record_assignment_conflict(
            session,
            student_id=data.student_id,
            exam_id=data.exam_id,
            block_id=data.block_id,
            room_id=data.room_id,
            conflict_type="block_overlap",
            reason=reason,
        )
        raise HTTPException(status_code=409, detail=reason)

    if crud.get_student_exam_assignment_by_student_exam(session, data.student_id, data.exam_id) is not None:
        reason = f"{data.student_id}: already assigned to this exam"
        record_assignment_conflict(
            session,
            student_id=data.student_id,
            exam_id=data.exam_id,
            block_id=data.block_id,
            room_id=data.room_id,
            conflict_type="duplicate_exam",
            reason=reason,
        )
        raise HTTPException(status_code=409, detail=reason)

    if crud.get_exam_room_assignment_for_exam(session, data.exam_id, data.block_id, data.room_id) is None:
        reason = "The exam does not have that room enabled for that block"
        record_assignment_conflict(
            session,
            student_id=data.student_id,
            exam_id=data.exam_id,
            block_id=data.block_id,
            room_id=data.room_id,
            conflict_type="room_not_reserved",
            reason=reason,
        )
        raise HTTPException(status_code=409, detail=reason)

    if crud.count_room_assignments(session, data.block_id, data.room_id) >= room.capacity:
        reason = f"Room {data.room_id} is full in block {data.block_id}"
        record_assignment_conflict(
            session,
            student_id=data.student_id,
            exam_id=data.exam_id,
            block_id=data.block_id,
            room_id=data.room_id,
            conflict_type="room_capacity",
            reason=reason,
        )
        raise HTTPException(status_code=409, detail=reason)

    assignment = conflict_safe(session, lambda: crud.create_student_exam_assignment(session, data))
    return crud.student_exam_assignment_to_read(session, assignment)


@router.patch(
    "/student-exam-assignments/{student_id}/{block_id}",
    response_model=StudentExamAssignmentRead,
    tags=[STUDENT_EXAM_ASSIGNMENTS_TAG],
)
def update_student_exam_assignment(
    student_id: str,
    block_id: int,
    data: StudentExamAssignmentUpdate,
    session: SessionDep,
):
    assignment = require_exists(
        session,
        StudentExamAssignment,
        (student_id, block_id),
        "Student exam assignment",
    )
    if data.status == "assigned" and assignment.status != "assigned":
        room = require_exists(session, Room, assignment.room_id, "Room")
        ensure_room_capacity(session, room, assignment.block_id)
    updated = conflict_safe(session, lambda: crud.update_student_exam_assignment(session, assignment, data))
    return crud.student_exam_assignment_to_read(session, updated)


@router.delete(
    "/student-exam-assignments/{student_id}/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[STUDENT_EXAM_ASSIGNMENTS_TAG],
)
def delete_student_exam_assignment(student_id: str, block_id: int, session: SessionDep):
    assignment = require_exists(
        session,
        StudentExamAssignment,
        (student_id, block_id),
        "Student exam assignment",
    )
    conflict_safe(session, lambda: crud.delete_item(session, assignment))


@router.post(
    "/student-exam-assignments/course",
    response_model=CourseExamAssignmentResult,
    status_code=status.HTTP_201_CREATED,
    tags=[STUDENT_EXAM_ASSIGNMENTS_TAG],
)
def create_course_exam_assignments(data: CourseExamAssignmentCreate, session: SessionDep):
    exam = require_exists(session, Exam, data.exam_id, "Exam")
    room = require_exists(session, Room, data.room_id, "Room")
    require_exists(session, ExamBlock, data.block_id, "Exam block")
    validate_exam_block(exam, data.block_id)
    require_exam_room_assignment(session, data.exam_id, data.block_id, data.room_id)

    enrollments = crud.list_course_enrollments_by_section(session, exam.course_section_id)
    conflicts = []
    assignments = []
    existing_room_assignments = crud.count_room_assignments(session, data.block_id, data.room_id)
    available_capacity = max(room.capacity - existing_room_assignments, 0)
    assigned_for_request = 0

    for enrollment in enrollments:
        student_id = enrollment.student_id
        if crud.get_student_exam_assignment(session, student_id, data.block_id) is not None:
            conflicts.append(
                record_assignment_conflict(
                    session,
                    student_id=student_id,
                    exam_id=data.exam_id,
                    block_id=data.block_id,
                    room_id=data.room_id,
                    conflict_type="block_overlap",
                    reason=f"{student_id}: already has an exam assigned in block {data.block_id}",
                )
            )
            continue

        if crud.get_student_exam_assignment_by_student_exam(session, student_id, data.exam_id) is not None:
            conflicts.append(
                record_assignment_conflict(
                    session,
                    student_id=student_id,
                    exam_id=data.exam_id,
                    block_id=data.block_id,
                    room_id=data.room_id,
                    conflict_type="duplicate_exam",
                    reason=f"{student_id}: already assigned to this exam",
                )
            )
            continue

        if assigned_for_request >= available_capacity:
            conflicts.append(
                record_assignment_conflict(
                    session,
                    student_id=student_id,
                    exam_id=data.exam_id,
                    block_id=data.block_id,
                    room_id=data.room_id,
                    conflict_type="room_capacity",
                    reason=f"{student_id}: room {data.room_id} is full in block {data.block_id}",
                )
            )
            continue

        assignment = conflict_safe(
            session,
            lambda current_student_id=student_id: crud.create_student_exam_assignment(
                session,
                StudentExamAssignmentCreate(
                    student_id=current_student_id,
                    block_id=data.block_id,
                    exam_id=data.exam_id,
                    room_id=data.room_id,
                ),
            ),
        )
        assignments.append(crud.student_exam_assignment_to_read(session, assignment))
        assigned_for_request += 1

    return CourseExamAssignmentResult(
        exam_id=data.exam_id,
        course_section_id=exam.course_section_id,
        block_id=data.block_id,
        room_id=data.room_id,
        total_enrolled=len(enrollments),
        total_assigned=len(assignments),
        total_conflicts=len(conflicts),
        assignments=assignments,
        conflicts=conflicts,
    )


@router.get("/assignment-conflicts", response_model=list[AssignmentConflictRead], tags=[ASSIGNMENT_CONFLICTS_TAG])
def list_assignment_conflicts(
    session: SessionDep,
    student_id: str | None = None,
    exam_id: int | None = None,
    block_id: int | None = None,
    room_id: str | None = None,
):
    return [
        crud.assignment_conflict_to_read(conflict)
        for conflict in crud.list_assignment_conflicts(
            session,
            student_id=student_id,
            exam_id=exam_id,
            block_id=block_id,
            room_id=room_id,
        )
    ]


@router.delete(
    "/assignment-conflicts/{conflict_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[ASSIGNMENT_CONFLICTS_TAG],
)
def delete_assignment_conflict(conflict_id: int, session: SessionDep):
    conflict = require_exists(session, AssignmentConflict, conflict_id, "Assignment conflict")
    conflict_safe(session, lambda: crud.delete_item(session, conflict))


@router.get(
    "/students/{student_id}/exam-assignments",
    response_model=list[StudentExamAssignmentRead],
    tags=[STUDENTS_TAG],
)
def list_exam_assignments_by_student(student_id: str, session: SessionDep):
    require_exists(session, Student, student_id, "Student")
    assignments = crud.list_student_exam_assignments_by_student(session, student_id)
    return [crud.student_exam_assignment_to_read(session, assignment) for assignment in assignments]
