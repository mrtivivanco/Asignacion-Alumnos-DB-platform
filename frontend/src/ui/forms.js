import {
  createAlumno,
  createAlumnoCarrera,
  createAsignacion,
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

export function bindFormHandlers({ loadData, showError }) {
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
      await createAsignacion({
        rut_alumno: formData.get("rut_alumno"),
        ...usoSala,
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
