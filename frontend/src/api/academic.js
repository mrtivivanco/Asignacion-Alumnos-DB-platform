import { fetchJson } from "./client.js";

export function listAlumnos() {
  return fetchJson("/api/alumnos");
}

export function createAlumno(alumnoData) {
  return fetchJson("/api/alumnos", {
    method: "POST",
    body: JSON.stringify(alumnoData),
  });
}

export function listCarreras() {
  return fetchJson("/api/carreras");
}

export function createAlumnoCarrera(alumnoCarreraData) {
  return fetchJson("/api/alumno-carreras", {
    method: "POST",
    body: JSON.stringify(alumnoCarreraData),
  });
}

export function listCursos() {
  return fetchJson("/api/cursos");
}

export function listBloques() {
  return fetchJson("/api/bloques");
}

export function listPruebas() {
  return fetchJson("/api/pruebas");
}

export function listSalas() {
  return fetchJson("/api/salas");
}

export function listUsoSala() {
  return fetchJson("/api/uso-sala");
}

export function listAsignaciones() {
  return fetchJson("/api/asignaciones");
}

export function createAsignacion(asignacionData) {
  return fetchJson("/api/asignaciones", {
    method: "POST",
    body: JSON.stringify(asignacionData),
  });
}

export function listAsignacionesByAlumno(rutAlumno) {
  return fetchJson(`/api/alumnos/${encodeURIComponent(rutAlumno)}/asignaciones`);
}
