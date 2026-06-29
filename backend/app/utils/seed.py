from datetime import date, time

from faker import Faker
from sqlmodel import Session, select

from ..db.schema import (
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
from ..storage.exam_pdfs import delete_exam_pdf, save_exam_pdf
from .ids import require_id
from .pdf_generation import generate_fake_exam_pdf


SEED = 2026
STUDENT_COUNT = 28
PROGRAM_COUNT = 5
COURSE_SECTION_COUNT = 8
ROOM_COUNT = 12
EXAM_COUNT = 12
MAX_ASSIGNMENTS_PER_EXAM = 6

PROGRAM_NAMES = (
    "Ingenieria Comercial",
    "Ingenieria Civil Informatica",
    "Psicologia",
    "Derecho",
    "Diseno",
    "Arquitectura",
    "Periodismo",
    "Administracion Publica",
)

COURSE_PREFIXES = (
    "Introduccion a",
    "Fundamentos de",
    "Taller de",
    "Laboratorio de",
    "Seminario de",
    "Proyecto de",
)

COURSE_TOPICS = (
    "Bases de Datos",
    "Calculo Aplicado",
    "Programacion",
    "Estadistica",
    "Macroeconomia",
    "Derecho Civil",
    "Diseno de Interfaces",
    "Arquitectura de Software",
    "Analisis de Datos",
    "Gestion de Proyectos",
    "Etica Profesional",
    "Investigacion Academica",
)

EXAM_TOPICS = (
    "Modelamiento Relacional",
    "Consultas SQL",
    "Derivadas",
    "Algebra Lineal",
    "Probabilidad",
    "Inferencia Estadistica",
    "Estructuras de Datos",
    "Politica Monetaria",
    "Obligaciones Civiles",
    "Prototipado",
    "Arquitectura Web",
    "Analisis de Casos",
)


def seed_demo_data(session: Session) -> None:
    """Insert deterministic Faker demo data once so repeated starts are safe."""
    fake = Faker("es_CL")
    fake.seed_instance(SEED)
    Faker.seed(SEED)

    if session.exec(select(Student)).first() is not None:
        seed_exam_pdfs(session, fake)
        return

    exam_blocks = build_exam_blocks()
    degree_programs = build_degree_programs(fake)
    students = build_students(fake)
    course_sections = build_course_sections(fake)
    rooms = build_rooms(fake)

    session.add_all([*degree_programs, *students, *course_sections, *exam_blocks, *rooms])
    session.commit()

    for item in [*degree_programs, *course_sections]:
        session.refresh(item)

    program_ids = [require_id(program.program_id, "DegreeProgram") for program in degree_programs]
    section_ids = [require_id(section.course_section_id, "CourseSection") for section in course_sections]

    student_programs = build_student_programs(fake, students, program_ids)
    course_enrollments = build_course_enrollments(fake, students, section_ids)
    exams = build_exams(fake, section_ids)

    session.add_all([*student_programs, *course_enrollments, *exams])
    session.commit()

    for exam in exams:
        session.refresh(exam)

    exam_room_assignments = build_exam_room_assignments(fake, exams, rooms)
    student_exam_assignments = build_student_exam_assignments(
        fake,
        exams,
        rooms,
        course_enrollments,
        exam_room_assignments,
    )

    session.add_all([*exam_room_assignments, *student_exam_assignments])
    session.commit()

    seed_exam_pdfs(session, fake)


def seed_exam_pdfs(session: Session, fake: Faker) -> None:
    exams = list(session.exec(select(Exam).order_by(Exam.exam_id)).all())
    uploaded_file_ids = []

    try:
        for index, exam in enumerate(exams):
            if index % 2 != 0 or exam.pdf_file_id:
                continue

            exam_id = require_id(exam.exam_id, "Exam")
            pdf_content = generate_fake_exam_pdf(exam_id, exam.name, fake)
            file_id = save_exam_pdf(exam_id, f"exam-{exam_id}.pdf", pdf_content)
            uploaded_file_ids.append(file_id)
            exam.pdf_file_id = file_id
            session.add(exam)

        session.commit()
    except Exception:
        session.rollback()
        for file_id in uploaded_file_ids:
            try:
                delete_exam_pdf(file_id)
            except Exception:
                pass
        raise


def build_exam_blocks() -> list[ExamBlock]:
    return [
        ExamBlock(
            block_id=1,
            exam_date=date(2026, 6, 2),
            day_name="Martes",
            start_time=time(18, 0),
            end_time=time(20, 0),
        ),
        ExamBlock(
            block_id=2,
            exam_date=date(2026, 6, 4),
            day_name="Jueves",
            start_time=time(18, 0),
            end_time=time(20, 0),
        ),
        ExamBlock(
            block_id=3,
            exam_date=date(2026, 6, 6),
            day_name="Sabado",
            start_time=time(9, 0),
            end_time=time(11, 0),
        ),
        ExamBlock(
            block_id=4,
            exam_date=date(2026, 6, 6),
            day_name="Sabado",
            start_time=time(11, 0),
            end_time=time(13, 0),
        ),
    ]


def build_degree_programs(fake: Faker) -> list[DegreeProgram]:
    names = set()
    programs = []
    while len(programs) < PROGRAM_COUNT:
        name = fake.random_element(elements=PROGRAM_NAMES)
        if name in names:
            continue
        names.add(name)
        programs.append(DegreeProgram(name=name))
    return programs


def build_students(fake: Faker) -> list[Student]:
    students = []
    for _ in range(STUDENT_COUNT):
        first_name = fake.first_name()
        last_name = fake.last_name()
        students.append(
            Student(
                student_id=fake.unique.numerify(text="########-#"),
                first_name=first_name,
                last_name=last_name,
                email=fake.unique.email(),
            )
        )
    return students


def build_course_sections(fake: Faker) -> list[CourseSection]:
    sections = []
    seen = set()
    while len(sections) < COURSE_SECTION_COUNT:
        name = f"{fake.random_element(elements=COURSE_PREFIXES)} {fake.random_element(elements=COURSE_TOPICS)}"
        section_code = fake.random_element(elements=("A", "B", "C", "D"))
        key = (name, section_code)
        if key in seen:
            continue
        seen.add(key)
        sections.append(
            CourseSection(
                name=name,
                section_code=section_code,
                capacity=fake.random_int(min=28, max=50),
            )
        )
    return sections


def build_rooms(fake: Faker) -> list[Room]:
    rooms = []
    seen = set()
    while len(rooms) < ROOM_COUNT:
        building = fake.random_element(elements=("A", "B", "C", "D", "E", "F"))
        room_number = fake.random_int(min=101, max=499)
        key = (room_number, building)
        if key in seen:
            continue
        seen.add(key)
        rooms.append(
            Room(
                room_id=f"{building}-{room_number}",
                room_number=room_number,
                building=building,
                capacity=fake.random_int(min=24, max=45),
            )
        )
    return rooms


def build_student_programs(fake: Faker, students: list[Student], program_ids: list[int]) -> list[StudentProgram]:
    return [
        StudentProgram(
            student_id=student.student_id,
            program_id=fake.random_element(elements=program_ids),
        )
        for student in students
    ]


def build_course_enrollments(
    fake: Faker,
    students: list[Student],
    section_ids: list[int],
) -> list[CourseEnrollment]:
    enrollments = []
    seen = set()

    for index, student in enumerate(students):
        guaranteed_section_id = section_ids[index % len(section_ids)]
        optional_section_id = fake.random_element(
            elements=[section_id for section_id in section_ids if section_id != guaranteed_section_id]
        )

        for section_id in (guaranteed_section_id, optional_section_id):
            key = (student.student_id, section_id)
            if key in seen:
                continue
            seen.add(key)
            enrollments.append(
                CourseEnrollment(
                    student_id=student.student_id,
                    course_section_id=section_id,
                    enrolled_on=fake.date_between(start_date=date(2026, 3, 1), end_date=date(2026, 3, 31)),
                )
            )

    return enrollments


def build_exams(fake: Faker, section_ids: list[int]) -> list[Exam]:
    exams = []
    seen = set()

    while len(exams) < EXAM_COUNT:
        section_id = section_ids[len(exams) % len(section_ids)]
        block_id = (len(exams) % 4) + 1
        name = f"Prueba de {fake.random_element(elements=EXAM_TOPICS)}"
        key = (section_id, name, 2026)
        if key in seen:
            continue
        seen.add(key)
        exams.append(
            Exam(
                course_section_id=section_id,
                block_id=block_id,
                name=name,
                exam_type=fake.random_element(elements=("ordinaria", "extraordinaria", "recuperativa")),
                creation_year=2026,
            )
        )

    return exams


def build_exam_room_assignments(
    fake: Faker,
    exams: list[Exam],
    rooms: list[Room],
) -> list[ExamRoomAssignment]:
    assignments = []
    used_rooms_by_block = set()
    rooms_by_capacity = sorted(rooms, key=lambda room: room.capacity, reverse=True)

    for exam in exams:
        exam_id = require_id(exam.exam_id, "Exam")
        available_rooms = [room for room in rooms_by_capacity if (exam.block_id, room.room_id) not in used_rooms_by_block]
        room = fake.random_element(elements=available_rooms)
        used_rooms_by_block.add((exam.block_id, room.room_id))
        assignments.append(
            ExamRoomAssignment(
                exam_id=exam_id,
                block_id=exam.block_id,
                room_id=room.room_id,
            )
        )

    return assignments


def build_student_exam_assignments(
    fake: Faker,
    exams: list[Exam],
    rooms: list[Room],
    enrollments: list[CourseEnrollment],
    exam_room_assignments: list[ExamRoomAssignment],
) -> list[StudentExamAssignment]:
    room_by_id = {room.room_id: room for room in rooms}
    enrollments_by_section = group_enrollments_by_section(enrollments)
    room_assignment_by_exam = {assignment.exam_id: assignment for assignment in exam_room_assignments}
    assigned_blocks_by_student = set()
    assignments = []

    for exam in exams:
        exam_id = require_id(exam.exam_id, "Exam")
        room_assignment = room_assignment_by_exam[exam_id]
        room = room_by_id[room_assignment.room_id]
        candidates = list(enrollments_by_section.get(exam.course_section_id, []))
        fake.random.shuffle(candidates)

        assigned_for_exam = 0
        max_for_exam = min(room.capacity, MAX_ASSIGNMENTS_PER_EXAM)

        for student_id in candidates:
            if (student_id, exam.block_id) in assigned_blocks_by_student:
                continue

            assignments.append(
                StudentExamAssignment(
                    student_id=student_id,
                    exam_id=exam_id,
                    block_id=exam.block_id,
                    room_id=room.room_id,
                )
            )
            assigned_blocks_by_student.add((student_id, exam.block_id))
            assigned_for_exam += 1

            if assigned_for_exam >= max_for_exam:
                break

    return assignments


def group_enrollments_by_section(enrollments: list[CourseEnrollment]) -> dict[int, list[str]]:
    grouped: dict[int, list[str]] = {}
    for enrollment in enrollments:
        grouped.setdefault(enrollment.course_section_id, []).append(enrollment.student_id)
    return grouped
