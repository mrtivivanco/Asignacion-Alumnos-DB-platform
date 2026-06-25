function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fillSelect(selector, items, valueFor, labelFor) {
  const select = document.querySelector(selector);
  const selectedValue = select.value;

  select.innerHTML = items
    .map((item) => `<option value="${escapeHtml(valueFor(item))}">${escapeHtml(labelFor(item))}</option>`)
    .join("");

  if (selectedValue) {
    select.value = selectedValue;
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function formatTime(value) {
  return value.slice(0, 5);
}

function alumnoLabel(alumno) {
  return `${alumno.nombre} ${alumno.apellido} (${alumno.rut})`;
}

function usoSalaKey(uso) {
  return `${uso.id_evaluacion}|${uso.id_sala}|${uso.n_bloque}`;
}

function usoSalaLabel(uso) {
  return `${uso.prueba.nombre} | B${uso.n_bloque} | ${uso.sala.id_sala}`;
}

function cursoLabel(curso) {
  return `${curso.nombre} · Seccion ${curso.seccion}`;
}

function bloqueLabel(bloque) {
  return `B${bloque.n_bloque} · ${bloque.dia} ${formatTime(bloque.hora_inicio)}-${formatTime(bloque.hora_fin)}`;
}

function salaLabel(sala) {
  return `${sala.id_sala} · cupo ${sala.cupo}`;
}

export function setStatusMessage(message) {
  document.querySelector("#status-message").textContent = message;
}

export function renderAsignaciones(asignaciones) {
  const list = document.querySelector("#assignment-list");

  list.innerHTML = asignaciones
    .map(
      (asignacion) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <strong class="text-lg font-black text-black">${escapeHtml(asignacion.prueba.nombre)}</strong>
              <p class="mt-1 text-sm text-[#555555]">
                ${escapeHtml(alumnoLabel(asignacion.alumno))}
              </p>
            </div>
            <span class="rounded-md bg-[#2B8BE3] px-3 py-1 text-sm font-black text-white">
              Bloque ${asignacion.n_bloque}
            </span>
          </div>
          <div class="mt-3 grid gap-2 border-l-4 border-[#E5A93C] pl-3 text-sm font-bold text-[#333333] sm:grid-cols-2">
            <span>${escapeHtml(asignacion.prueba.curso.nombre)} · Seccion ${escapeHtml(asignacion.prueba.curso.seccion)}</span>
            <span>Sala ${escapeHtml(asignacion.sala.id_sala)}</span>
            <span>${escapeHtml(asignacion.bloque.dia)} ${formatDate(asignacion.bloque.fecha)}</span>
            <span>${formatTime(asignacion.bloque.hora_inicio)}-${formatTime(asignacion.bloque.hora_fin)}</span>
          </div>
        </li>
      `,
    )
    .join("");
}

export function renderAlumnos(alumnos) {
  const list = document.querySelector("#alumno-list");

  list.innerHTML = alumnos
    .map(
      (alumno) => `
        <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <strong class="text-lg font-black text-black">${escapeHtml(alumno.nombre)} ${escapeHtml(alumno.apellido)}</strong>
            <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
              ${escapeHtml(alumno.rut)}
            </span>
          </div>
          <p class="mt-2 text-sm text-[#555555]">${escapeHtml(alumno.email ?? "Sin email registrado")}</p>
        </li>
      `,
    )
    .join("");
}

export function renderSelects(state) {
  fillSelect("#alumno-carrera", state.carreras, (carrera) => carrera.id_carrera, (carrera) => carrera.nombre);
  fillSelect("#prueba-curso", state.cursos, (curso) => curso.id_curso, cursoLabel);
  fillSelect("#prueba-sala", state.salas, (sala) => sala.id_sala, salaLabel);
  fillSelect("#prueba-bloque", state.bloques, (bloque) => bloque.n_bloque, bloqueLabel);
  fillSelect("#asignacion-uso-sala", state.usoSala, usoSalaKey, usoSalaLabel);
  fillSelect("#asignaciones-by-alumno-select", state.alumnos, (alumno) => alumno.rut, alumnoLabel);
}

export function renderAlumnoAsignaciones(asignaciones) {
  const list = document.querySelector("#alumno-asignacion-list");

  if (asignaciones.length === 0) {
    list.innerHTML = `
      <li class="rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4 text-sm font-bold text-[#555555]">
        Este alumno no tiene pruebas asignadas.
      </li>
    `;
    return;
  }

  list.innerHTML = asignaciones
    .map(
      (asignacion) => `
        <li class="flex flex-col gap-2 rounded-md border border-[#e7e7e7] bg-[#f7f7f7] p-4 sm:flex-row sm:items-center sm:justify-between">
          <strong class="text-lg font-black text-black">${escapeHtml(asignacion.prueba.nombre)}</strong>
          <span class="rounded-md bg-white px-3 py-1 text-sm font-bold text-[#333333]">
            Bloque ${asignacion.n_bloque} · ${escapeHtml(asignacion.sala.id_sala)}
          </span>
        </li>
      `,
    )
    .join("");
}

function renderStats(state) {
  document.querySelector("#student-count").textContent = state.alumnos.length;
  document.querySelector("#assignment-count").textContent = state.asignaciones.length;
  document.querySelector("#block-count").textContent = state.bloques.length;
}

export function render(state) {
  renderSelects(state);
  renderStats(state);
  renderAsignaciones(state.asignaciones);
  renderAlumnos(state.alumnos);
}
