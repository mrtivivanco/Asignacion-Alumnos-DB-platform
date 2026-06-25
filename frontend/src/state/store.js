export const state = {
  alumnos: [],
  carreras: [],
  cursos: [],
  bloques: [],
  pruebas: [],
  salas: [],
  usoSala: [],
  asignaciones: [],
};

export function setReferenceData({
  alumnos,
  carreras,
  cursos,
  bloques,
  pruebas,
  salas,
  usoSala,
  asignaciones,
}) {
  state.alumnos = alumnos;
  state.carreras = carreras;
  state.cursos = cursos;
  state.bloques = bloques;
  state.pruebas = pruebas;
  state.salas = salas;
  state.usoSala = usoSala;
  state.asignaciones = asignaciones;
}
