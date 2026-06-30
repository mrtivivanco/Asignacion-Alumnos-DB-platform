function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function firstDefined(...values) {
  return values.find((value) => value !== undefined && value !== null);
}

function fillSelect(selector, items = [], valueFor, labelFor) {
  const select = document.querySelector(selector);

  if (!select) {
    return;
  }

  const selectedValue = select.value;
  const hasSelectedValue = items.some((item) => String(valueFor(item)) === selectedValue);

  select.innerHTML = items
    .map((item) => `<option value="${escapeHtml(valueFor(item))}">${escapeHtml(labelFor(item))}</option>`)
    .join("");

  if (hasSelectedValue) {
    select.value = selectedValue;
  }
}

function setText(selector, value) {
  const element = document.querySelector(selector);

  if (element) {
    element.textContent = value;
  }
}

function searchValue(selector) {
  return document.querySelector(selector)?.value.trim().toLowerCase() ?? "";
}

function filterValue(selector) {
  return document.querySelector(selector)?.value ?? "";
}

function matchesSearch(values, query) {
  if (!query) {
    return true;
  }

  return values.some((value) => String(value ?? "").toLowerCase().includes(query));
}

function formatDate(value) {
  if (!value) {
    return "Sin fecha";
  }

  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function programNameFromCourse(courseName) {
  return String(courseName ?? "").split(" - ")[0] || "Sin carrera";
}

function fillFilterSelect(selector, options, placeholder) {
  const select = document.querySelector(selector);

  if (!select) {
    return;
  }

  const selectedValue = select.value;
  select.innerHTML = [
    `<option value="">${escapeHtml(placeholder)}</option>`,
    ...options.map((option) => `<option value="${escapeHtml(option.value)}">${escapeHtml(option.label)}</option>`),
  ].join("");

  select.value = options.some((option) => option.value === selectedValue) ? selectedValue : "";
}

function uniqueSortedOptions(values, labelFor = (value) => value) {
  return [...new Set(values.filter(Boolean))]
    .sort((left, right) => String(labelFor(left)).localeCompare(String(labelFor(right)), "es"))
    .map((value) => ({ value, label: labelFor(value) }));
}

function uniqueDateOptions(values) {
  return [...new Set(values.filter(Boolean))]
    .sort()
    .map((value) => ({ value, label: formatDate(value) }));
}

function formatTime(value) {
  return value ? String(value).slice(0, 5) : "--:--";
}

function formatDateTime(value) {
  if (!value) {
    return "Sin fecha";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatBytes(value) {
  const bytes = Number(value);

  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "Tamano no informado";
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function stateList(state, englishKey, spanishKey) {
  return firstDefined(state[englishKey], state[spanishKey], []);
}

function studentId(student) {
  return firstDefined(student.student_id, student.rut, "");
}

function studentFirstName(student) {
  return firstDefined(student.first_name, student.nombre, "");
}

function studentLastName(student) {
  return firstDefined(student.last_name, student.apellido, "");
}

function studentLabel(student) {
  return `${studentFirstName(student)} ${studentLastName(student)} (${studentId(student)})`;
}

function programId(program) {
  return firstDefined(program.program_id, program.id_carrera, "");
}

function programName(program) {
  return firstDefined(program.name, program.nombre, "Carrera sin nombre");
}

function courseSectionId(courseSection) {
  return firstDefined(courseSection.course_section_id, courseSection.id_curso, "");
}

function courseSectionName(courseSection) {
  return firstDefined(courseSection.name, courseSection.nombre, "Curso sin nombre");
}

function courseSectionCapacity(courseSection) {
  return firstDefined(courseSection.capacity, courseSection.cupo, 0);
}

function courseSectionLabel(courseSection) {
  return courseSectionName(courseSection);
}

function blockId(block) {
  return firstDefined(block.block_id, block.n_bloque, "");
}

function blockDayName(block) {
  return firstDefined(block.day_name, block.dia, "Sin dia");
}

function blockStartTime(block) {
  return firstDefined(block.start_time, block.hora_inicio);
}

function blockEndTime(block) {
  return firstDefined(block.end_time, block.hora_fin);
}

function blockDate(block) {
  return firstDefined(block.exam_date, block.fecha);
}

function blockLabel(block) {
  return `B${blockId(block)} · ${blockDayName(block)} ${formatDate(blockDate(block))} · ${formatTime(blockStartTime(block))}-${formatTime(blockEndTime(block))}`;
}

function roomId(room) {
  return firstDefined(room.room_id, room.id_sala, "");
}

function roomCapacity(room) {
  return firstDefined(room.capacity, room.cupo, 0);
}

function roomNumber(room) {
  return firstDefined(room.room_number, room.n_sala, "");
}

function roomBuilding(room) {
  return firstDefined(room.building, room.edificio, "");
}

function roomLabel(room) {
  return `${roomId(room)} · cupo ${roomCapacity(room)}`;
}

function examId(exam) {
  return firstDefined(exam.exam_id, exam.id_evaluacion, "");
}

function examPdfFileId(exam) {
  return firstDefined(exam.pdf_file_id, exam.pdf_id, "");
}

function examName(exam) {
  return firstDefined(exam.name, exam.nombre, "Prueba sin nombre");
}

function examBlock(exam) {
  return firstDefined(exam.block, exam.bloque, {});
}

function examCourseSection(exam) {
  return firstDefined(exam.course_section, exam.curso, {});
}

function examLabel(exam) {
  const courseSection = examCourseSection(exam);
  const block = examBlock(exam);
  const blockText = blockId(block) ? ` · ${blockLabel(block)}` : "";

  return `${examName(exam)} · ${courseSectionLabel(courseSection)}${blockText}`;
}

function pdfMetadataFileName(metadata, exam) {
  return firstDefined(metadata?.filename, metadata?.metadata?.filename, `prueba-${examId(exam)}.pdf`);
}

function pdfMetadataUploadDate(metadata) {
  return firstDefined(metadata?.upload_date, metadata?.metadata?.uploaded_at);
}

function assignmentExam(assignment) {
  return firstDefined(assignment.exam, assignment.prueba, {});
}

function assignmentStudent(assignment) {
  return firstDefined(assignment.student, assignment.alumno, {});
}

function assignmentRoom(assignment) {
  return firstDefined(assignment.room, assignment.sala, {});
}

function assignmentBlock(assignment) {
  return firstDefined(assignment.exam_block, assignment.block, assignment.bloque, {});
}

function assignmentBlockId(assignment) {
  return firstDefined(assignment.block_id, assignment.n_bloque, blockId(assignmentBlock(assignment)), "");
}

function examRoomAssignmentExam(examRoomAssignment) {
  return firstDefined(examRoomAssignment.exam, examRoomAssignment.prueba, {});
}

function examRoomAssignmentRoom(examRoomAssignment) {
  return firstDefined(examRoomAssignment.room, examRoomAssignment.sala, {});
}

function examRoomAssignmentBlock(examRoomAssignment) {
  return firstDefined(examRoomAssignment.block, examRoomAssignment.bloque, examRoomAssignment.exam_block, {});
}

function renderEmptyList(list, message) {
  list.innerHTML = `
    <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4 text-sm font-bold text-[#555555]">
      ${escapeHtml(message)}
    </li>
  `;
}

export function setStatusMessage(message) {
  setText("#status-message", message);
}

export function setFeedbackMessage(message, title = "Mensaje del sistema") {
  const panel = document.querySelector("#feedback-panel");

  if (!panel) {
    return;
  }

  setText("#feedback-title", title);
  setText("#feedback-message", message);
  panel.classList.remove("hidden");
}

export function clearFeedbackMessage() {
  document.querySelector("#feedback-panel")?.classList.add("hidden");
}

export function bindFeedbackHandlers() {
  document.querySelector("#feedback-close")?.addEventListener("click", clearFeedbackMessage);
}

export function renderStudentExamAssignments(assignments) {
  const list = document.querySelector("#alumno-asignacion-list");

  if (!list) {
    return;
  }

  if (assignments.length === 0) {
    renderEmptyList(list, "Este alumno no tiene pruebas asignadas.");
    return;
  }

  list.innerHTML = assignments
    .map((assignment) => {
      const exam = assignmentExam(assignment);
      const room = assignmentRoom(assignment);

      return `
        <li class="flex flex-col gap-2 rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4 sm:flex-row sm:items-center sm:justify-between">
          <strong class="text-lg font-black text-black">${escapeHtml(examName(exam))}</strong>
          <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
            Bloque ${escapeHtml(assignmentBlockId(assignment))} · ${escapeHtml(roomId(room))}
          </span>
        </li>
      `;
    })
    .join("");
}

export function renderAlumnoAsignaciones(assignments) {
  renderStudentExamAssignments(assignments);
}

export function renderAssignments(assignments) {
  const list = document.querySelector("#assignment-list");

  if (!list) {
    return;
  }

  const query = searchValue("#assignment-search");
  const assignmentsByExam = new Map();

  for (const assignment of assignments) {
    const exam = assignmentExam(assignment);
    const id = examId(exam) || `${examName(exam)}-${assignmentBlockId(assignment)}-${roomId(assignmentRoom(assignment))}`;
    const group = assignmentsByExam.get(id) ?? [];
    group.push(assignment);
    assignmentsByExam.set(id, group);
  }

  const allExamGroups = [...assignmentsByExam.values()];
  const filterRows = [];

  for (const group of allExamGroups) {
    const firstAssignment = group[0];
    const exam = assignmentExam(firstAssignment);
    const block = assignmentBlock(firstAssignment);
    const courseName = courseSectionName(examCourseSection(exam));
    filterRows.push({
      programName: programNameFromCourse(courseName),
      courseName,
      date: blockDate(block),
    });
  }

  fillFilterSelect(
    "#assignment-program-filter",
    uniqueSortedOptions(filterRows.map((row) => row.programName)),
    "Todas las carreras",
  );

  const selectedProgram = filterValue("#assignment-program-filter");
  const courseRows = filterRows.filter((row) => !selectedProgram || row.programName === selectedProgram);
  fillFilterSelect(
    "#assignment-course-filter",
    uniqueSortedOptions(courseRows.map((row) => row.courseName)),
    "Todos los ramos",
  );

  const selectedCourse = filterValue("#assignment-course-filter");
  const dateRows = courseRows.filter((row) => !selectedCourse || row.courseName === selectedCourse);
  fillFilterSelect("#assignment-date-filter", uniqueDateOptions(dateRows.map((row) => row.date)), "Todas las fechas");

  const selectedDate = filterValue("#assignment-date-filter");
  const hasActiveFilter = Boolean(query || selectedProgram || selectedCourse || selectedDate);

  const examGroups = allExamGroups.filter((group) => {
    const firstAssignment = group[0];
    const exam = assignmentExam(firstAssignment);
    const room = assignmentRoom(firstAssignment);
    const block = assignmentBlock(firstAssignment);
    const courseSection = examCourseSection(exam);
    const courseName = courseSectionName(courseSection);
    const programName = programNameFromCourse(courseName);
    const date = blockDate(block);
    const students = group.flatMap((assignment) => {
      const student = assignmentStudent(assignment);
      return [studentLabel(student), studentId(student), student.email];
    });

    if (selectedProgram && programName !== selectedProgram) {
      return false;
    }

    if (selectedCourse && courseName !== selectedCourse) {
      return false;
    }

    if (selectedDate && date !== selectedDate) {
      return false;
    }

    return matchesSearch(
      [
        examId(exam),
        examName(exam),
        courseSectionName(courseSection),
        roomId(room),
        blockId(block),
        assignmentBlockId(firstAssignment),
        ...students,
      ],
      query,
    );
  });

  if (examGroups.length === 0) {
    renderEmptyList(
      list,
      hasActiveFilter ? "No hay asignaciones que coincidan con los filtros." : "No hay pruebas asignadas todavia.",
    );
    return;
  }

  list.innerHTML = examGroups
    .map((group) => {
      const firstAssignment = group[0];
      const exam = assignmentExam(firstAssignment);
      const room = assignmentRoom(firstAssignment);
      const block = assignmentBlock(firstAssignment);
      const courseSection = examCourseSection(exam);
      const students = [...group].sort((left, right) =>
        studentLabel(assignmentStudent(left)).localeCompare(studentLabel(assignmentStudent(right)), "es"),
      );

      return `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <details ${query ? "open" : ""}>
            <summary class="cursor-pointer list-none">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <strong class="text-lg font-black text-black">${escapeHtml(examName(exam))}</strong>
                  <p class="mt-1 text-sm font-bold text-[#555555]">${escapeHtml(courseSectionName(courseSection))}</p>
                </div>
                <span class="rounded-md bg-[#2B8BE3] px-3 py-1 text-sm font-black text-white">
                  ${escapeHtml(group.length)} alumnos asignados
                </span>
              </div>
              <div class="mt-3 grid gap-2 border-l-4 border-[#E5A93C] pl-3 text-sm font-bold text-[#333333] sm:grid-cols-3">
                <span>Sala ${escapeHtml(roomId(room))}</span>
                <span>Bloque ${escapeHtml(blockId(block))}</span>
                <span>${escapeHtml(blockDayName(block))} ${formatDate(blockDate(block))} · ${formatTime(blockStartTime(block))}-${formatTime(blockEndTime(block))}</span>
              </div>
              <p class="mt-3 text-xs font-black uppercase tracking-[0.16em] text-[#555555]">Abrir para ver alumnos</p>
            </summary>
            <ul class="mt-4 grid gap-2 border-t border-[#e0e0e0] pt-4">
              ${students
                .map((assignment) => {
                  const student = assignmentStudent(assignment);
                  return `
                    <li class="flex flex-col gap-1 rounded-md bg-white px-3 py-2 text-sm sm:flex-row sm:items-center sm:justify-between">
                      <span class="font-black text-black">${escapeHtml(studentLabel(student))}</span>
                      <span class="font-bold text-[#555555]">${escapeHtml(student.email ?? "Sin email")}</span>
                    </li>
                  `;
                })
                .join("")}
            </ul>
          </details>
        </li>
      `;
    })
    .join("");
}

export function renderAsignaciones(assignments) {
  renderAssignments(assignments);
}

export function renderStudents(students) {
  const list = document.querySelector("#alumno-list");

  if (!list) {
    return;
  }

  const query = searchValue("#student-search");
  const filteredStudents = students.filter((student) =>
    matchesSearch([studentFirstName(student), studentLastName(student), studentId(student), student.email], query),
  );

  if (filteredStudents.length === 0) {
    renderEmptyList(list, query ? "No hay alumnos que coincidan con la busqueda." : "No hay alumnos registrados.");
    return;
  }

  list.innerHTML = filteredStudents
    .map(
      (student) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <strong class="text-lg font-black text-black">${escapeHtml(studentFirstName(student))} ${escapeHtml(studentLastName(student))}</strong>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              ${escapeHtml(studentId(student))}
            </span>
          </div>
          <p class="mt-2 text-sm text-[#555555]">${escapeHtml(student.email ?? "Sin email registrado")}</p>
        </li>
      `,
    )
    .join("");
}

export function renderAlumnos(students) {
  renderStudents(students);
}

export function renderDegreePrograms(programs) {
  const list = document.querySelector("#degree-program-list");

  if (!list) {
    return;
  }

  const query = searchValue("#degree-program-search");
  const filteredPrograms = programs.filter((program) => matchesSearch([programName(program), programId(program)], query));

  if (filteredPrograms.length === 0) {
    renderEmptyList(list, query ? "No hay carreras que coincidan con la busqueda." : "No hay carreras disponibles.");
    return;
  }

  list.innerHTML = filteredPrograms
    .map(
      (program) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <strong class="text-lg font-black text-black">${escapeHtml(programName(program))}</strong>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              Carrera #${escapeHtml(programId(program))}
            </span>
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderCourseSections(courseSections) {
  const list = document.querySelector("#course-section-list");

  if (!list) {
    return;
  }

  const query = searchValue("#course-section-search");
  const filteredCourseSections = courseSections.filter((courseSection) =>
    matchesSearch(
      [courseSectionName(courseSection), courseSectionId(courseSection), courseSectionCapacity(courseSection)],
      query,
    ),
  );

  if (filteredCourseSections.length === 0) {
    renderEmptyList(list, query ? "No hay cursos que coincidan con la busqueda." : "No hay cursos disponibles.");
    return;
  }

  list.innerHTML = filteredCourseSections
    .map(
      (courseSection) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">${escapeHtml(courseSectionName(courseSection))}</strong>
            </div>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              Curso #${escapeHtml(courseSectionId(courseSection))}
            </span>
          </div>
          <div class="mt-3 border-l-4 border-[#E5A93C] pl-3 text-sm font-bold text-[#333333]">
            Cupo ${escapeHtml(courseSectionCapacity(courseSection))}
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderExamBlocks(examBlocks) {
  const list = document.querySelector("#exam-block-list");

  if (!list) {
    return;
  }

  const query = searchValue("#exam-block-search");
  const filteredBlocks = examBlocks.filter((block) =>
    matchesSearch([blockId(block), blockDayName(block), blockDate(block), blockStartTime(block), blockEndTime(block)], query),
  );

  if (filteredBlocks.length === 0) {
    renderEmptyList(list, query ? "No hay bloques que coincidan con la busqueda." : "No hay bloques disponibles.");
    return;
  }

  list.innerHTML = filteredBlocks
    .map(
      (block) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">Bloque ${escapeHtml(blockId(block))}</strong>
              <p class="mt-1 text-sm font-bold text-[#555555]">${escapeHtml(blockDayName(block))} · ${formatDate(blockDate(block))}</p>
            </div>
            <span class="rounded-md bg-[#2B8BE3] px-3 py-1 text-sm font-black text-white">
              ${formatTime(blockStartTime(block))}-${formatTime(blockEndTime(block))}
            </span>
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderRooms(rooms) {
  const list = document.querySelector("#room-list");

  if (!list) {
    return;
  }

  const query = searchValue("#room-search");
  const filteredRooms = rooms.filter((room) =>
    matchesSearch([roomId(room), roomBuilding(room), roomNumber(room), roomCapacity(room)], query),
  );

  if (filteredRooms.length === 0) {
    renderEmptyList(list, query ? "No hay salas que coincidan con la busqueda." : "No hay salas disponibles.");
    return;
  }

  list.innerHTML = filteredRooms
    .map(
      (room) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">Sala ${escapeHtml(roomId(room))}</strong>
              <p class="mt-1 text-sm font-bold text-[#555555]">Edificio ${escapeHtml(roomBuilding(room))} · Numero ${escapeHtml(roomNumber(room))}</p>
            </div>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              Cupo ${escapeHtml(roomCapacity(room))}
            </span>
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderExamRoomAssignments(examRoomAssignments) {
  const list = document.querySelector("#exam-room-assignment-list");

  if (!list) {
    return;
  }

  const query = searchValue("#reservation-search");
  const filteredAssignments = examRoomAssignments.filter((assignment) => {
    const exam = examRoomAssignmentExam(assignment);
    const room = examRoomAssignmentRoom(assignment);
    const block = examRoomAssignmentBlock(assignment);
    const courseSection = examCourseSection(exam);

    return matchesSearch(
      [examName(exam), courseSectionName(courseSection), roomId(room), blockId(block)],
      query,
    );
  });

  if (filteredAssignments.length === 0) {
    renderEmptyList(list, query ? "No hay reservas que coincidan con la busqueda." : "No hay reservas de sala registradas.");
    return;
  }

  list.innerHTML = filteredAssignments
    .map((assignment) => {
      const exam = examRoomAssignmentExam(assignment);
      const room = examRoomAssignmentRoom(assignment);
      const block = examRoomAssignmentBlock(assignment);
      const courseSection = examCourseSection(exam);

      return `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">${escapeHtml(examName(exam))}</strong>
              <p class="mt-1 text-sm font-bold text-[#555555]">${escapeHtml(courseSectionLabel(courseSection))}</p>
            </div>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              Sala ${escapeHtml(roomId(room))}
            </span>
          </div>
          <div class="mt-3 border-l-4 border-[#E5A93C] pl-3 text-sm font-bold text-[#333333]">
            Bloque ${escapeHtml(blockId(block))} · ${escapeHtml(blockDayName(block))} · ${formatTime(blockStartTime(block))}-${formatTime(blockEndTime(block))}
          </div>
        </li>
      `;
    })
    .join("");
}

export function renderExamPdfs(exams, metadataByExamId = {}) {
  const list = document.querySelector("#exam-pdf-list");

  if (!list) {
    return;
  }

  const query = searchValue("#exam-pdf-search");
  const filteredExams = exams.filter((exam) => {
    const courseSection = examCourseSection(exam);
    const block = examBlock(exam);
    const metadata = metadataByExamId[examId(exam)];

    return matchesSearch(
      [
        examId(exam),
        examName(exam),
        courseSectionName(courseSection),
        blockId(block),
        pdfMetadataFileName(metadata, exam),
        examPdfFileId(exam) ? "con pdf" : "sin pdf",
      ],
      query,
    );
  });

  if (filteredExams.length === 0) {
    renderEmptyList(list, query ? "No hay pruebas PDF que coincidan con la busqueda." : "No hay pruebas disponibles.");
    return;
  }

  list.innerHTML = filteredExams
    .map((exam) => {
      const id = examId(exam);
      const courseSection = examCourseSection(exam);
      const block = examBlock(exam);
      const metadata = metadataByExamId[id];
      const hasPdf = Boolean(examPdfFileId(exam) || metadata?.pdf_file_id);
      const filename = pdfMetadataFileName(metadata, exam);
      const statusClass = hasPdf ? "bg-electric text-white" : "bg-white text-[#555555]";
      const statusText = hasPdf ? "PDF cargado" : "Sin PDF";
      const metadataText = hasPdf
        ? `${escapeHtml(filename)} · ${formatBytes(metadata?.length)} · ${formatDateTime(pdfMetadataUploadDate(metadata))}`
        : "Carga un archivo PDF para habilitar descarga y eliminacion.";
      const actions = hasPdf
        ? `
          <div class="mt-4 flex flex-wrap gap-2">
            <button class="rounded-md border border-[#d9d9d9] bg-white px-3 py-2 text-sm font-black text-[#333333] transition hover:border-electric hover:text-electric" type="button" data-pdf-action="download" data-exam-id="${escapeHtml(id)}" data-filename="${escapeHtml(filename)}">
              Descargar
            </button>
            <button class="rounded-md border border-[#d9d9d9] bg-white px-3 py-2 text-sm font-black text-[#333333] transition hover:border-electric hover:text-electric" type="button" data-pdf-action="delete" data-exam-id="${escapeHtml(id)}">
              Eliminar PDF
            </button>
          </div>
        `
        : "";

      return `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">${escapeHtml(examName(exam))}</strong>
              <p class="mt-1 text-sm font-bold text-[#555555]">
                ${escapeHtml(courseSectionLabel(courseSection))} · Bloque ${escapeHtml(blockId(block))}
              </p>
            </div>
            <span class="rounded-md px-3 py-1 text-sm font-black ${statusClass}">${statusText}</span>
          </div>
          <p class="mt-3 border-l-4 border-[#E5A93C] pl-3 text-sm font-bold leading-6 text-[#333333]">
            ${metadataText}
          </p>
          ${actions}
        </li>
      `;
    })
    .join("");
}

export function renderDashboardBlocks(examBlocks) {
  const list = document.querySelector("#dashboard-block-list");

  if (!list) {
    return;
  }

  if (examBlocks.length === 0) {
    renderEmptyList(list, "No hay bloques extraordinarios configurados.");
    return;
  }

  list.innerHTML = examBlocks
    .map(
      (block) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">Bloque ${escapeHtml(blockId(block))}</strong>
              <p class="mt-1 text-sm font-bold text-[#555555]">${escapeHtml(blockDayName(block))} · ${formatDate(blockDate(block))}</p>
            </div>
            <span class="rounded-md bg-[#2B8BE3] px-3 py-1 text-sm font-black text-white">
              ${formatTime(blockStartTime(block))}-${formatTime(blockEndTime(block))}
            </span>
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderReadinessChecklist({
  degreePrograms,
  courseSections,
  rooms,
  examBlocks,
  exams,
  examRoomAssignments,
}) {
  const list = document.querySelector("#dashboard-readiness-list");

  if (!list) {
    return;
  }

  const items = [
    ["Carreras cargadas", degreePrograms.length],
    ["Cursos cargados", courseSections.length],
    ["Salas cargadas", rooms.length],
    ["Bloques cargados", examBlocks.length],
    ["Pruebas creadas", exams.length],
    ["Salas reservadas", examRoomAssignments.length],
  ];

  list.innerHTML = items
    .map(([label, count]) => {
      const isReady = count > 0;
      const badgeClass = isReady ? "bg-electric text-white" : "bg-white text-[#555555]";
      const badgeText = isReady ? "Listo" : "Faltan datos";

      return `
        <li class="flex flex-col gap-3 rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <strong class="text-base font-black text-black">${escapeHtml(label)}</strong>
            <p class="mt-1 text-sm font-bold text-[#555555]">${escapeHtml(count)} registros</p>
          </div>
          <span class="rounded-md px-3 py-1 text-sm font-black ${badgeClass}">${badgeText}</span>
        </li>
      `;
    })
    .join("");
}

export function renderSelects(state) {
  const students = stateList(state, "students", "alumnos");
  const courseSections = stateList(state, "courseSections", "cursos");
  const examBlocks = stateList(state, "examBlocks", "bloques");
  const exams = stateList(state, "exams", "pruebas");
  const rooms = stateList(state, "rooms", "salas");
  const studentAssignmentQuery = searchValue("#asignaciones-alumno-filter");
  const filteredStudents = students.filter((student) =>
    matchesSearch([studentFirstName(student), studentLastName(student), studentId(student), student.email], studentAssignmentQuery),
  );

  fillSelect("#prueba-curso", courseSections, courseSectionId, courseSectionLabel);
  fillSelect("#asignaciones-by-alumno-select", filteredStudents, studentId, studentLabel);
  fillSelect("#reserva-prueba", exams, examId, examLabel);
  fillSelect("#reserva-sala", rooms, roomId, roomLabel);
  fillSelect("#reserva-bloque", examBlocks, blockId, blockLabel);
  fillSelect("#exam-pdf-select", exams, examId, examLabel);
}

function renderStats(state) {
  const students = stateList(state, "students", "alumnos");
  const examBlocks = stateList(state, "examBlocks", "bloques");
  const exams = stateList(state, "exams", "pruebas");
  const rooms = stateList(state, "rooms", "salas");
  const courseSections = stateList(state, "courseSections", "cursos");

  setText("#student-count", students.length);
  setText("#exam-count", exams.length);
  setText("#block-count", examBlocks.length);
  setText("#room-count", rooms.length);
  setText("#course-section-count", courseSections.length);
}

export function bindFilterHandlers(state) {
  const selectors = [
    "#student-search",
    "#asignaciones-alumno-filter",
    "#assignment-search",
    "#assignment-program-filter",
    "#assignment-course-filter",
    "#assignment-date-filter",
    "#degree-program-search",
    "#course-section-search",
    "#exam-block-search",
    "#room-search",
    "#reservation-search",
    "#exam-pdf-search",
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    element?.addEventListener("input", () => render(state));
    element?.addEventListener("change", () => render(state));
  }
}

export function render(state) {
  const students = stateList(state, "students", "alumnos");
  const assignments = stateList(state, "studentExamAssignments", "asignaciones");
  const degreePrograms = stateList(state, "degreePrograms", "carreras");
  const courseSections = stateList(state, "courseSections", "cursos");
  const examBlocks = stateList(state, "examBlocks", "bloques");
  const rooms = stateList(state, "rooms", "salas");
  const exams = stateList(state, "exams", "pruebas");
  const examRoomAssignments = stateList(state, "examRoomAssignments", "usoSala");
  const examPdfMetadata = firstDefined(state.examPdfMetadata, {});

  renderSelects(state);
  renderStats(state);
  renderAssignments(assignments);
  renderStudents(students);
  renderDegreePrograms(degreePrograms);
  renderCourseSections(courseSections);
  renderExamBlocks(examBlocks);
  renderRooms(rooms);
  renderExamRoomAssignments(examRoomAssignments);
  renderExamPdfs(exams, examPdfMetadata);
  renderDashboardBlocks(examBlocks);
  renderReadinessChecklist({
    degreePrograms,
    courseSections,
    rooms,
    examBlocks,
    exams,
    examRoomAssignments,
  });
}
