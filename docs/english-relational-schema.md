# English Relational Schema

Physical relational model for assigning students to extraordinary exams.

This document translates the original Spanish schema into English names and includes a few recommended structural improvements. It is intended to be used as a reference when updating the database schema.

## Naming Decisions

| Original name | Recommended English name | Notes |
| --- | --- | --- |
| `alumnos` | `students` | Main student table. |
| `rut` | `student_id` | Stores the RUT or a synthetic student identifier. |
| `carreras` | `degree_programs` | Better than `careers` in an academic context. |
| `alumno_carreras` | `student_programs` | Many-to-many link between students and degree programs. |
| `cursos` | `course_sections` | The original table includes `seccion`, so each row is a course section. |
| `inscripciones` | `course_enrollments` | Many-to-many link between students and course sections. |
| `bloques` | `exam_blocks` | Fixed date/time blocks for exams. |
| `pruebas` | `exams` | Exams/evaluations assigned to course sections. |
| `salas` | `rooms` | Physical rooms/classrooms. |
| `uso_sala` | `exam_room_assignments` | Which room is used by which exam in a block. |
| `asignaciones` | `student_exam_assignments` | Student assignment to an exam room in a block. |

## Recommended Schema

```dbml
// Physical relational model
// Extraordinary exam student assignment system

Table students {
  student_id varchar [pk, note: 'RUT or synthetic identifier for the student']
  first_name varchar [not null]
  last_name varchar [not null]
  email varchar [unique]
  created_at timestamp
}

Table degree_programs {
  program_id integer [pk, increment]
  name varchar [not null, unique]
}

Table student_programs {
  student_id varchar [not null]
  program_id integer [not null]

  indexes {
    (student_id, program_id) [pk]
  }
}

Table course_sections {
  course_section_id integer [pk, increment]
  section_code varchar [not null]
  name varchar [not null]
  capacity integer [not null]
  created_at timestamp

  indexes {
    (name, section_code) [unique]
  }
}

Table course_enrollments {
  student_id varchar [not null]
  course_section_id integer [not null]
  enrolled_on date

  indexes {
    (student_id, course_section_id) [pk]
  }
}

Table exam_blocks {
  block_id integer [pk]
  exam_date date [not null]
  day_name varchar [not null, note: 'Tuesday, Thursday, or Saturday']
  start_time time [not null]
  end_time time [not null]

  indexes {
    (exam_date, start_time) [unique]
  }
}

Table exams {
  exam_id integer [pk, increment]
  course_section_id integer [not null]
  block_id integer [not null]
  name varchar [not null]
  exam_type varchar
  creation_year integer
  pdf_file_id varchar(24) [unique, note: 'MongoDB GridFS file _id for the exam PDF, stored as a 24-character ObjectId string']
  created_at timestamp

  indexes {
    (exam_id, block_id) [unique, note: 'Supports composite FK from exam_room_assignments and validates the exam block']
  }
}

Table rooms {
  room_id varchar [pk]
  room_number integer [not null]
  building varchar [not null]
  capacity integer [not null]

  indexes {
    (room_number, building) [unique]
  }
}

Table exam_room_assignments {
  block_id integer [not null]
  room_id varchar [not null]
  exam_id integer [not null, note: 'FK to exams. Attribute of the room usage, not part of the primary key.']
  created_at timestamp

  indexes {
    (block_id, room_id) [pk, note: 'A room can only be used once per block']
    (exam_id, block_id, room_id) [unique, note: 'Supports FK from student_exam_assignments and keeps the assigned exam explicit']
  }
}

Table student_exam_assignments {
  student_id varchar [not null]
  exam_id integer [not null]
  block_id integer [not null]
  room_id varchar [not null]
  status varchar [not null, default: 'assigned', note: 'assigned, cancelled, absent']
  created_at timestamp

  indexes {
    (student_id, block_id) [pk, note: 'A student can only have one assignment per block']
    (student_id, exam_id) [unique, note: 'A student can only be assigned once to the same exam']
  }
}

// Relationships

Ref: student_programs.student_id > students.student_id
Ref: student_programs.program_id > degree_programs.program_id

Ref: course_enrollments.student_id > students.student_id
Ref: course_enrollments.course_section_id > course_sections.course_section_id

Ref: exams.course_section_id > course_sections.course_section_id
Ref: exams.block_id > exam_blocks.block_id

Ref: exam_room_assignments.block_id > exam_blocks.block_id
Ref: exam_room_assignments.room_id > rooms.room_id
Ref: exam_room_assignments.(exam_id, block_id) > exams.(exam_id, block_id)

Ref: student_exam_assignments.student_id > students.student_id
Ref: student_exam_assignments.(exam_id, block_id, room_id) > exam_room_assignments.(exam_id, block_id, room_id)

// Fixed example data for exam blocks
// Update dates according to the real semester.

Records exam_blocks(block_id, exam_date, day_name, start_time, end_time) {
  1, '2026-06-02', 'Tuesday', '18:00', '20:00'
  2, '2026-06-04', 'Thursday', '18:00', '20:00'
  3, '2026-06-06', 'Saturday', '09:00', '11:00'
  4, '2026-06-06', 'Saturday', '11:00', '13:00'
}
```

## Recommended Constraints

Add these constraints in the actual database implementation if supported:

```sql
CHECK (capacity > 0)
CHECK (end_time > start_time)
CHECK (day_name IN ('Tuesday', 'Thursday', 'Saturday'))
CHECK (status IN ('assigned', 'cancelled', 'absent'))
```

Apply `CHECK (capacity > 0)` to both `course_sections.capacity` and `rooms.capacity`.

## MongoDB PDF Storage

The relational database should not store the exam PDF binary directly. Store each exam PDF in MongoDB and keep only the MongoDB file identifier in the relational `exams.pdf_file_id` column.

Recommended MongoDB approach:

```text
Use MongoDB GridFS for PDF storage.
Store the PDF binary in GridFS.
Store the generated GridFS `fs.files._id` ObjectId in `exams.pdf_file_id` as a 24-character string.
```

Recommended MongoDB database and bucket names:

```text
Database: exam_files
GridFS bucket: exam_pdfs
Collections created by GridFS: exam_pdfs.files and exam_pdfs.chunks
```

Recommended MongoDB metadata for each PDF file:

```json
{
  "filename": "exam-<exam_id>.pdf",
  "contentType": "application/pdf",
  "metadata": {
    "exam_id": 123,
    "course_section_id": 45,
    "uploaded_by": "system-or-user-id",
    "uploaded_at": "2026-06-28T00:00:00Z"
  }
}
```

Relational update flow:

1. Create or update the `exams` row without embedding the PDF binary.
2. Upload the PDF to MongoDB GridFS.
3. Read the generated GridFS file ObjectId.
4. Save that ObjectId as a string in `exams.pdf_file_id`.

Recommended behavior:

```text
`exams.pdf_file_id` should be nullable if an exam can exist before its PDF is uploaded.
`exams.pdf_file_id` should be unique if one stored PDF must belong to only one exam.
If the relational database does not support multiple NULL values in a UNIQUE column, use a partial unique index for non-null `pdf_file_id` values.
Validate `pdf_file_id` as a 24-character hexadecimal MongoDB ObjectId string before saving it.
When replacing a PDF, upload the new file first, update `exams.pdf_file_id`, then delete the old GridFS file after the relational update succeeds.
When deleting an exam, also delete the related MongoDB GridFS file if `pdf_file_id` is present.
Because the relational database and MongoDB are separate datastores, do not assume these writes are atomic together. If a relational update fails after a MongoDB upload, delete the newly uploaded GridFS file to avoid orphaned PDFs.
```

The application should validate that uploaded files are PDFs before writing them to MongoDB. At minimum, validate the MIME type and the file extension. If possible, also inspect the file signature.

## Important Implementation Notes

`student_exam_assignments` includes `exam_id` even though the exam can be inferred from `exam_room_assignments`. This makes each student assignment clearer and allows the database to verify that the assigned room belongs to the same exam and block.

The primary key `(student_id, block_id)` in `student_exam_assignments` prevents a student from being assigned to more than one exam in the same time block.

The primary key `(block_id, room_id)` in `exam_room_assignments` prevents a room from being used by more than one exam in the same time block.

The schema still does not automatically enforce room capacity. Preventing over-capacity assignments requires application logic, a database trigger, or a transaction-level validation query.

The schema still does not automatically enforce that a student assigned to an exam is enrolled in the course section for that exam. Enforce this in application logic or with a database trigger. If strict database-level enforcement is required, add `course_section_id` to `student_exam_assignments` and use composite foreign keys against both `exams` and `course_enrollments`.

`day_name` can become inconsistent with `exam_date` unless validated. If possible, prefer deriving the day name from `exam_date` in queries or application code instead of storing it permanently.
