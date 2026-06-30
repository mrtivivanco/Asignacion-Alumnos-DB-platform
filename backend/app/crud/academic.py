from sqlalchemy import or_
from sqlmodel import Session, select

from ..db.dto import (
    AssignmentConflictCreate,
    AssignmentConflictRead,
    CourseEnrollmentCreate,
    CourseEnrollmentRead,
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
    ExamRoomAssignmentCreate,
    ExamRoomAssignmentRead,
    ExamRoomAssignmentUpdate,
    ExamUpdate,
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
from ..utils.ids import require_id


def apply_updates(item, data):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    return item


def list_students(session: Session, q: str | None = None) -> list[Student]:
    statement = select(Student)
    if q:
        term = f"%{q}%"
        statement = statement.where(
            or_(
                Student.student_id.ilike(term),
                Student.first_name.ilike(term),
                Student.last_name.ilike(term),
                Student.email.ilike(term),
            )
        )
    statement = statement.order_by(Student.last_name, Student.first_name)
    return list(session.exec(statement).all())


def get_student(session: Session, student_id: str) -> Student | None:
    return session.get(Student, student_id)


def create_student(session: Session, data: StudentCreate) -> Student:
    student = Student.model_validate(data)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def update_student(session: Session, student: Student, data: StudentUpdate) -> Student:
    apply_updates(student, data)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def delete_item(session: Session, item) -> None:
    session.delete(item)
    session.commit()


def student_to_read(student: Student) -> StudentRead:
    return StudentRead.model_validate(student)


def list_degree_programs(session: Session, q: str | None = None) -> list[DegreeProgram]:
    statement = select(DegreeProgram)
    if q:
        statement = statement.where(DegreeProgram.name.ilike(f"%{q}%"))
    statement = statement.order_by(DegreeProgram.name)
    return list(session.exec(statement).all())


def get_degree_program(session: Session, program_id: int) -> DegreeProgram | None:
    return session.get(DegreeProgram, program_id)


def create_degree_program(session: Session, data: DegreeProgramCreate) -> DegreeProgram:
    degree_program = DegreeProgram.model_validate(data)
    session.add(degree_program)
    session.commit()
    session.refresh(degree_program)
    return degree_program


def update_degree_program(
    session: Session,
    degree_program: DegreeProgram,
    data: DegreeProgramUpdate,
) -> DegreeProgram:
    apply_updates(degree_program, data)
    session.add(degree_program)
    session.commit()
    session.refresh(degree_program)
    return degree_program


def degree_program_to_read(degree_program: DegreeProgram) -> DegreeProgramRead:
    return DegreeProgramRead(
        program_id=require_id(degree_program.program_id, "DegreeProgram"),
        name=degree_program.name,
    )


def list_student_programs(session: Session) -> list[StudentProgram]:
    return list(session.exec(select(StudentProgram).order_by(StudentProgram.student_id)).all())


def get_student_program(session: Session, student_id: str, program_id: int) -> StudentProgram | None:
    return session.get(StudentProgram, (student_id, program_id))


def create_student_program(session: Session, data: StudentProgramCreate) -> StudentProgram:
    item = StudentProgram.model_validate(data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def student_program_to_read(session: Session, item: StudentProgram) -> StudentProgramRead:
    student = get_required(session, Student, item.student_id, "Student")
    degree_program = get_required(session, DegreeProgram, item.program_id, "Degree program")
    return StudentProgramRead(
        student_id=item.student_id,
        program_id=item.program_id,
        student=student_to_read(student),
        degree_program=degree_program_to_read(degree_program),
    )


def list_course_sections(session: Session, q: str | None = None) -> list[CourseSection]:
    statement = select(CourseSection)
    if q:
        statement = statement.where(CourseSection.name.ilike(f"%{q}%"))
    statement = statement.order_by(CourseSection.name)
    return list(session.exec(statement).all())


def get_course_section(session: Session, course_section_id: int) -> CourseSection | None:
    return session.get(CourseSection, course_section_id)


def create_course_section(session: Session, data: CourseSectionCreate) -> CourseSection:
    course_section = CourseSection.model_validate(data)
    session.add(course_section)
    session.commit()
    session.refresh(course_section)
    return course_section


def update_course_section(
    session: Session,
    course_section: CourseSection,
    data: CourseSectionUpdate,
) -> CourseSection:
    apply_updates(course_section, data)
    session.add(course_section)
    session.commit()
    session.refresh(course_section)
    return course_section


def course_section_to_read(course_section: CourseSection) -> CourseSectionRead:
    return CourseSectionRead(
        course_section_id=require_id(course_section.course_section_id, "CourseSection"),
        name=course_section.name,
        capacity=course_section.capacity,
        created_at=course_section.created_at,
    )


def list_course_enrollments(
    session: Session,
    student_id: str | None = None,
    course_section_id: int | None = None,
) -> list[CourseEnrollment]:
    statement = select(CourseEnrollment)
    if student_id is not None:
        statement = statement.where(CourseEnrollment.student_id == student_id)
    if course_section_id is not None:
        statement = statement.where(CourseEnrollment.course_section_id == course_section_id)
    statement = statement.order_by(CourseEnrollment.student_id)
    return list(session.exec(statement).all())


def list_course_enrollments_by_section(session: Session, course_section_id: int) -> list[CourseEnrollment]:
    statement = (
        select(CourseEnrollment)
        .where(CourseEnrollment.course_section_id == course_section_id)
        .order_by(CourseEnrollment.student_id)
    )
    return list(session.exec(statement).all())


def get_course_enrollment(
    session: Session,
    student_id: str,
    course_section_id: int,
) -> CourseEnrollment | None:
    return session.get(CourseEnrollment, (student_id, course_section_id))


def student_is_enrolled_in_section(session: Session, student_id: str, course_section_id: int) -> bool:
    return get_course_enrollment(session, student_id, course_section_id) is not None


def create_course_enrollment(session: Session, data: CourseEnrollmentCreate) -> CourseEnrollment:
    course_enrollment = CourseEnrollment.model_validate(data)
    session.add(course_enrollment)
    session.commit()
    session.refresh(course_enrollment)
    return course_enrollment


def course_enrollment_to_read(session: Session, item: CourseEnrollment) -> CourseEnrollmentRead:
    student = get_required(session, Student, item.student_id, "Student")
    course_section = get_required(session, CourseSection, item.course_section_id, "Course section")
    return CourseEnrollmentRead(
        student_id=item.student_id,
        course_section_id=item.course_section_id,
        enrolled_on=item.enrolled_on,
        student=student_to_read(student),
        course_section=course_section_to_read(course_section),
    )


def list_exam_blocks(session: Session) -> list[ExamBlock]:
    return list(session.exec(select(ExamBlock).order_by(ExamBlock.block_id)).all())


def get_exam_block(session: Session, block_id: int) -> ExamBlock | None:
    return session.get(ExamBlock, block_id)


def create_exam_block(session: Session, data: ExamBlockCreate) -> ExamBlock:
    exam_block = ExamBlock.model_validate(data)
    session.add(exam_block)
    session.commit()
    session.refresh(exam_block)
    return exam_block


def update_exam_block(session: Session, exam_block: ExamBlock, data: ExamBlockUpdate) -> ExamBlock:
    apply_updates(exam_block, data)
    session.add(exam_block)
    session.commit()
    session.refresh(exam_block)
    return exam_block


def exam_block_to_read(exam_block: ExamBlock) -> ExamBlockRead:
    return ExamBlockRead.model_validate(exam_block)


def list_exams(
    session: Session,
    q: str | None = None,
    block_id: int | None = None,
    course_section_id: int | None = None,
    has_pdf: bool | None = None,
) -> list[Exam]:
    statement = select(Exam)
    if q:
        statement = statement.where(Exam.name.ilike(f"%{q}%"))
    if block_id is not None:
        statement = statement.where(Exam.block_id == block_id)
    if course_section_id is not None:
        statement = statement.where(Exam.course_section_id == course_section_id)
    if has_pdf is True:
        statement = statement.where(Exam.pdf_file_id.is_not(None))
    elif has_pdf is False:
        statement = statement.where(Exam.pdf_file_id.is_(None))
    statement = statement.order_by(Exam.name)
    return list(session.exec(statement).all())


def get_exam(session: Session, exam_id: int) -> Exam | None:
    return session.get(Exam, exam_id)


def create_exam(session: Session, data: ExamCreate) -> Exam:
    exam = Exam.model_validate(data)
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


def update_exam(session: Session, exam: Exam, data: ExamUpdate) -> Exam:
    apply_updates(exam, data)
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


def exam_to_read(session: Session, exam: Exam) -> ExamRead:
    course_section = get_required(session, CourseSection, exam.course_section_id, "Course section")
    exam_block = get_required(session, ExamBlock, exam.block_id, "Exam block") if exam.block_id is not None else None
    return ExamRead(
        exam_id=require_id(exam.exam_id, "Exam"),
        course_section_id=exam.course_section_id,
        block_id=exam.block_id,
        name=exam.name,
        exam_type=exam.exam_type,
        creation_year=exam.creation_year,
        pdf_file_id=exam.pdf_file_id,
        created_at=exam.created_at,
        course_section=course_section_to_read(course_section),
        block=exam_block_to_read(exam_block) if exam_block is not None else None,
    )


def list_rooms(session: Session, q: str | None = None, building: str | None = None) -> list[Room]:
    statement = select(Room)
    if q:
        term = f"%{q}%"
        statement = statement.where(
            or_(
                Room.room_id.ilike(term),
                Room.building.ilike(term),
            )
        )
    if building:
        statement = statement.where(Room.building == building)
    statement = statement.order_by(Room.building, Room.room_number)
    return list(session.exec(statement).all())


def get_room(session: Session, room_id: str) -> Room | None:
    return session.get(Room, room_id)


def create_room(session: Session, data: RoomCreate) -> Room:
    room = Room.model_validate(data)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def update_room(session: Session, room: Room, data: RoomUpdate) -> Room:
    apply_updates(room, data)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def room_to_read(room: Room) -> RoomRead:
    return RoomRead.model_validate(room)


def list_exam_room_assignments(
    session: Session,
    exam_id: int | None = None,
    block_id: int | None = None,
    room_id: str | None = None,
) -> list[ExamRoomAssignment]:
    statement = select(ExamRoomAssignment)
    if exam_id is not None:
        statement = statement.where(ExamRoomAssignment.exam_id == exam_id)
    if block_id is not None:
        statement = statement.where(ExamRoomAssignment.block_id == block_id)
    if room_id is not None:
        statement = statement.where(ExamRoomAssignment.room_id == room_id)
    statement = statement.order_by(ExamRoomAssignment.block_id, ExamRoomAssignment.room_id)
    return list(session.exec(statement).all())


def get_exam_room_assignment(
    session: Session,
    block_id: int,
    room_id: str,
) -> ExamRoomAssignment | None:
    return session.get(ExamRoomAssignment, (block_id, room_id))


def get_exam_room_assignment_for_exam(
    session: Session,
    exam_id: int,
    block_id: int,
    room_id: str,
) -> ExamRoomAssignment | None:
    statement = (
        select(ExamRoomAssignment)
        .where(ExamRoomAssignment.exam_id == exam_id)
        .where(ExamRoomAssignment.block_id == block_id)
        .where(ExamRoomAssignment.room_id == room_id)
    )
    return session.exec(statement).first()


def create_exam_room_assignment(session: Session, data: ExamRoomAssignmentCreate) -> ExamRoomAssignment:
    exam_room_assignment = ExamRoomAssignment.model_validate(data)
    session.add(exam_room_assignment)
    session.commit()
    session.refresh(exam_room_assignment)
    return exam_room_assignment


def update_exam_room_assignment(
    session: Session,
    exam_room_assignment: ExamRoomAssignment,
    data: ExamRoomAssignmentUpdate,
) -> ExamRoomAssignment:
    apply_updates(exam_room_assignment, data)
    session.add(exam_room_assignment)
    session.commit()
    session.refresh(exam_room_assignment)
    return exam_room_assignment


def exam_room_assignment_to_read(
    session: Session,
    exam_room_assignment: ExamRoomAssignment,
) -> ExamRoomAssignmentRead:
    exam = get_required(session, Exam, exam_room_assignment.exam_id, "Exam")
    room = get_required(session, Room, exam_room_assignment.room_id, "Room")
    exam_block = get_required(session, ExamBlock, exam_room_assignment.block_id, "Exam block")
    return ExamRoomAssignmentRead(
        exam_id=exam_room_assignment.exam_id,
        room_id=exam_room_assignment.room_id,
        block_id=exam_room_assignment.block_id,
        created_at=exam_room_assignment.created_at,
        exam=exam_to_read(session, exam),
        room=room_to_read(room),
        block=exam_block_to_read(exam_block),
    )


def list_student_exam_assignments(
    session: Session,
    student_id: str | None = None,
    exam_id: int | None = None,
    block_id: int | None = None,
) -> list[StudentExamAssignment]:
    statement = select(StudentExamAssignment)
    if student_id is not None:
        statement = statement.where(StudentExamAssignment.student_id == student_id)
    if exam_id is not None:
        statement = statement.where(StudentExamAssignment.exam_id == exam_id)
    if block_id is not None:
        statement = statement.where(StudentExamAssignment.block_id == block_id)
    statement = statement.order_by(
        StudentExamAssignment.block_id,
        StudentExamAssignment.student_id,
    )
    return list(session.exec(statement).all())


def count_room_assignments(session: Session, block_id: int, room_id: str) -> int:
    statement = (
        select(StudentExamAssignment)
        .where(StudentExamAssignment.block_id == block_id)
        .where(StudentExamAssignment.room_id == room_id)
        .where(StudentExamAssignment.status == "assigned")
    )
    return len(list(session.exec(statement).all()))


def max_room_assignments(session: Session, room_id: str) -> int:
    statement = (
        select(StudentExamAssignment)
        .where(StudentExamAssignment.room_id == room_id)
        .where(StudentExamAssignment.status == "assigned")
    )
    counts_by_block: dict[int, int] = {}
    for assignment in session.exec(statement).all():
        counts_by_block[assignment.block_id] = counts_by_block.get(assignment.block_id, 0) + 1
    return max(counts_by_block.values(), default=0)


def list_student_exam_assignments_by_student(
    session: Session,
    student_id: str,
) -> list[StudentExamAssignment]:
    statement = (
        select(StudentExamAssignment)
        .where(StudentExamAssignment.student_id == student_id)
        .order_by(StudentExamAssignment.block_id)
    )
    return list(session.exec(statement).all())


def get_student_exam_assignment(
    session: Session,
    student_id: str,
    block_id: int,
) -> StudentExamAssignment | None:
    return session.get(StudentExamAssignment, (student_id, block_id))


def get_student_exam_assignment_by_student_exam(
    session: Session,
    student_id: str,
    exam_id: int,
) -> StudentExamAssignment | None:
    statement = (
        select(StudentExamAssignment)
        .where(StudentExamAssignment.student_id == student_id)
        .where(StudentExamAssignment.exam_id == exam_id)
    )
    return session.exec(statement).first()


def create_student_exam_assignment(
    session: Session,
    data: StudentExamAssignmentCreate,
) -> StudentExamAssignment:
    student_exam_assignment = StudentExamAssignment.model_validate(data)
    session.add(student_exam_assignment)
    session.commit()
    session.refresh(student_exam_assignment)
    return student_exam_assignment


def update_student_exam_assignment(
    session: Session,
    student_exam_assignment: StudentExamAssignment,
    data: StudentExamAssignmentUpdate,
) -> StudentExamAssignment:
    apply_updates(student_exam_assignment, data)
    session.add(student_exam_assignment)
    session.commit()
    session.refresh(student_exam_assignment)
    return student_exam_assignment


def student_exam_assignment_to_read(
    session: Session,
    student_exam_assignment: StudentExamAssignment,
) -> StudentExamAssignmentRead:
    student = get_required(session, Student, student_exam_assignment.student_id, "Student")
    exam = get_required(session, Exam, student_exam_assignment.exam_id, "Exam")
    room = get_required(session, Room, student_exam_assignment.room_id, "Room")
    exam_block = get_required(session, ExamBlock, student_exam_assignment.block_id, "Exam block")
    return StudentExamAssignmentRead(
        student_id=student_exam_assignment.student_id,
        exam_id=student_exam_assignment.exam_id,
        block_id=student_exam_assignment.block_id,
        room_id=student_exam_assignment.room_id,
        status=student_exam_assignment.status,
        created_at=student_exam_assignment.created_at,
        student=student_to_read(student),
        exam=exam_to_read(session, exam),
        room=room_to_read(room),
        block=exam_block_to_read(exam_block),
    )


def list_assignment_conflicts(
    session: Session,
    student_id: str | None = None,
    exam_id: int | None = None,
    block_id: int | None = None,
    room_id: str | None = None,
) -> list[AssignmentConflict]:
    statement = select(AssignmentConflict)
    if student_id is not None:
        statement = statement.where(AssignmentConflict.student_id == student_id)
    if exam_id is not None:
        statement = statement.where(AssignmentConflict.exam_id == exam_id)
    if block_id is not None:
        statement = statement.where(AssignmentConflict.block_id == block_id)
    if room_id is not None:
        statement = statement.where(AssignmentConflict.room_id == room_id)
    statement = statement.order_by(AssignmentConflict.created_at.desc())
    return list(session.exec(statement).all())


def create_assignment_conflict(session: Session, data: AssignmentConflictCreate) -> AssignmentConflict:
    conflict = AssignmentConflict.model_validate(data)
    session.add(conflict)
    session.commit()
    session.refresh(conflict)
    return conflict


def get_assignment_conflict(session: Session, conflict_id: int) -> AssignmentConflict | None:
    return session.get(AssignmentConflict, conflict_id)


def assignment_conflict_to_read(conflict: AssignmentConflict) -> AssignmentConflictRead:
    return AssignmentConflictRead.model_validate(conflict)


def get_required(session: Session, model: type, key: object, label: str):
    item = session.get(model, key)
    if item is None:
        raise ValueError(f"{label} not found")
    return item
