from datetime import date, time, timedelta

from faker import Faker
from sqlmodel import Session, select

from ..db.schema import (
    CourseEnrollment,
    CourseSection,
    DegreeProgram,
    ExamBlock,
    Room,
    Student,
    StudentProgram,
)
from .ids import require_id

SEED = 2026
STUDENT_COUNT = 1000
EXAM_BLOCK_START_DATE = date(2026, 7, 7)
EXAM_BLOCK_END_DATE = date(2026, 12, 31)
COURSE_CAPACITY = 50

PROGRAM_NAMES = (
    "Ingenieria Comercial",
    "Ingenieria Civil",
    "Ingenieria Civil Industrial",
    "Ingenieria Civil Informatica",
    "Ingenieria Civil en Bioingenieria",
    "Ingenieria Civil en Diseno",
    "Psicologia",
    "Periodismo",
)

COURSE_NAMES = (
    "Algebra Lineal",
    "Bases de Datos",
    "Calculo Aplicado",
    "Estadistica",
)

WEEKLY_EXAM_BLOCKS = (
    (0, "Martes", time(18, 0), time(20, 0)),
    (2, "Jueves", time(18, 0), time(20, 0)),
    (4, "Sabado", time(9, 0), time(11, 0)),
    (4, "Sabado", time(11, 0), time(13, 0)),
)

ROOM_DATA = (
    ("AZ-201", 201, "A", 50),
    ("AZ-202", 202, "A", 50),
    ("AZ-203", 203, "A", 50),
    ("AZ-204", 204, "A", 50),
    ("AZ-101", 101, "A", 50),
    ("AZ-102", 102, "A", 50),
    ("AZ-103", 103, "A", 50),
    ("AZ-104", 104, "A", 50),
    ("A-101", 101, "A", 50),
    ("A-102", 102, "A", 50),
    ("A-103", 103, "A", 50),
    ("A-104", 104, "A", 50),
    ("A-105", 105, "A", 30),
    ("A-106", 106, "A", 30),
    ("A-201", 201, "A", 30),
    ("A-202", 202, "A", 30),
    ("A-203", 203, "A", 30),
    ("A-204", 204, "A", 30),
    ("A-205", 205, "A", 30),
    ("A-206", 206, "A", 30),
    ("A-207", 207, "A", 30),
    ("A-208", 208, "A", 50),
    ("A-210", 210, "A", 50),
    ("A-211", 211, "A", 50),
    ("A-301", 301, "A", 30),
    ("A-302", 302, "A", 30),
    ("A-303", 303, "A", 30),
    ("A-304", 304, "A", 30),
    ("A-305", 305, "A", 30),
    ("A-306", 306, "A", 30),
    ("BZ-201", 201, "B", 50),
    ("BZ-202", 202, "B", 50),
    ("D-206", 206, "D", 50),
    ("D-207", 207, "D", 50),
    ("D-208", 208, "D", 50),
    ("E-102", 102, "E", 50),
    ("E-103", 103, "E", 50),
    ("E-104", 104, "E", 50),
)


def seed_demo_data(session: Session) -> None:
    """Seed deterministic base data only; exams are created by users in the UI."""
    fake = Faker("es_CL")
    fake.seed_instance(SEED)
    Faker.seed(SEED)

    if session.exec(select(Student)).first() is not None:
        return

    degree_programs = build_degree_programs()
    students = build_students(fake)
    course_sections = build_course_sections()
    exam_blocks = build_exam_blocks()
    rooms = build_rooms()

    session.add_all([*degree_programs, *students, *course_sections, *exam_blocks, *rooms])
    session.commit()

    for item in [*degree_programs, *course_sections]:
        session.refresh(item)

    program_id_by_name = {
        program.name: require_id(program.program_id, "DegreeProgram")
        for program in degree_programs
    }
    course_ids_by_program = build_course_ids_by_program(course_sections)

    session.add_all(
        [
            *build_student_programs(students, program_id_by_name),
            *build_course_enrollments(students, course_ids_by_program),
        ]
    )
    session.commit()


def build_degree_programs() -> list[DegreeProgram]:
    return [DegreeProgram(name=name) for name in PROGRAM_NAMES]


def build_students(fake: Faker) -> list[Student]:
    students = []

    for index in range(STUDENT_COUNT):
        first_name = fake.first_name()
        last_name = fake.last_name()
        students.append(
            Student(
                student_id=f"{10_000_000 + index + 1}-{index % 10}",
                first_name=first_name,
                last_name=last_name,
                email=f"alumno{index + 1:04d}@example.com",
            )
        )

    return students


def build_course_sections() -> list[CourseSection]:
    return [
        CourseSection(
            name=f"{program_name} - {course_name}",
            capacity=COURSE_CAPACITY,
        )
        for program_name in PROGRAM_NAMES
        for course_name in COURSE_NAMES
    ]


def build_exam_blocks() -> list[ExamBlock]:
    blocks = []
    block_id = 1
    week_start = EXAM_BLOCK_START_DATE

    while week_start <= EXAM_BLOCK_END_DATE:
        for day_offset, day_name, start_time, end_time in WEEKLY_EXAM_BLOCKS:
            exam_date = week_start + timedelta(days=day_offset)

            if exam_date > EXAM_BLOCK_END_DATE:
                continue

            blocks.append(
                ExamBlock(
                    block_id=block_id,
                    exam_date=exam_date,
                    day_name=day_name,
                    start_time=start_time,
                    end_time=end_time,
                )
            )
            block_id += 1

        week_start += timedelta(days=7)

    return blocks


def build_rooms() -> list[Room]:
    return [
        Room(
            room_id=room_id,
            room_number=room_number,
            building=building,
            capacity=capacity,
        )
        for room_id, room_number, building, capacity in ROOM_DATA
    ]


def build_course_ids_by_program(course_sections: list[CourseSection]) -> dict[str, list[int]]:
    course_ids_by_program = {program_name: [] for program_name in PROGRAM_NAMES}

    for course_section in course_sections:
        program_name = course_section.name.split(" - ", 1)[0]
        course_ids_by_program[program_name].append(
            require_id(course_section.course_section_id, "CourseSection")
        )

    return course_ids_by_program


def build_student_programs(
    students: list[Student], program_id_by_name: dict[str, int]
) -> list[StudentProgram]:
    return [
        StudentProgram(
            student_id=student.student_id,
            program_id=program_id_by_name[PROGRAM_NAMES[index % len(PROGRAM_NAMES)]],
        )
        for index, student in enumerate(students)
    ]


def build_course_enrollments(
    students: list[Student], course_ids_by_program: dict[str, list[int]]
) -> list[CourseEnrollment]:
    enrollments = []

    for index, student in enumerate(students):
        program_name = PROGRAM_NAMES[index % len(PROGRAM_NAMES)]
        program_student_index = index // len(PROGRAM_NAMES)
        course_ids = course_ids_by_program[program_name]
        course_section_id = course_ids[program_student_index % len(course_ids)]
        enrollments.append(
            CourseEnrollment(
                student_id=student.student_id,
                course_section_id=course_section_id,
                enrolled_on=date(2026, 3, 1) + timedelta(days=index % 31),
            )
        )

    return enrollments
