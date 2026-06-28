import {
  createAlumno,
  createAlumnoCarrera,
  createAsignacionesCurso,
  createPrueba,
  createUsoSala,
  listAsignacionesByAlumno,
} from "../api/academic.js";
import { renderAlumnoAsignaciones } from "./render.js";

function parseUsoSalaKey(value) {
  const [idEvaluacion, idSala, nBloque] = value.split("|");
  return {
    id_evaluacion: Number(idEvaluacion),
    id_sala: idSala,
    n_bloque: Number(nBloque),
  };
}

export function bindFormHandlers({ loadData, showError, setStatusMessage }) {
  document.querySelector("#alumno-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const rut = String(formData.get("rut")).trim();
    const idCarrera = Number(formData.get("id_carrera"));

    try {
      await createAlumno({
        rut,
        nombre: formData.get("nombre"),
        apellido: formData.get("apellido"),
        email: formData.get("email") || null,
      });

      await createAlumnoCarrera({
        rut_alumno: rut,
        id_carrera: idCarrera,
      });

      form.reset();
      await loadData();
    } catch (error) {
      showError(error);
    }
  });

  document.querySelector("#asignacion-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const usoSala = parseUsoSalaKey(formData.get("uso_sala_key"));

    try {
      const result = await createAsignacionesCurso(usoSala);

      form.reset();
      await loadData();
      setStatusMessage(
        `Asignacion por curso lista: ${result.total_asignados} alumnos asignados sin solapamientos.`,
      );
    } catch (error) {
      showError(error);
    }
  });

  document.querySelector("#prueba-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const prueba = await createPrueba({
        id_curso: Number(formData.get("id_curso")),
        nombre: formData.get("nombre"),
        anio_creacion: Number(formData.get("anio_creacion")),
      });

      await createUsoSala({
        id_evaluacion: prueba.id_evaluacion,
        id_sala: formData.get("id_sala"),
        n_bloque: Number(formData.get("n_bloque")),
      });

      form.reset();
      await loadData();
    } catch (error) {
      showError(error);
    }
  });

  document.querySelector("#load-alumno-asignaciones").addEventListener("click", async () => {
    const rutAlumno = document.querySelector("#asignaciones-by-alumno-select").value;

    try {
      const asignaciones = await listAsignacionesByAlumno(rutAlumno);
      renderAlumnoAsignaciones(asignaciones);
    } catch (error) {
      showError(error);
    }
  });
}
