import "./styles.css";

import {
  listAlumnos,
  listAsignaciones,
  listBloques,
  listCarreras,
  listCursos,
  listPruebas,
  listSalas,
  listUsoSala,
} from "./api/academic.js";
import { setReferenceData, state } from "./state/store.js";
import { bindFormHandlers } from "./ui/forms.js";
import { render, setStatusMessage } from "./ui/render.js";

async function loadData() {
  setStatusMessage("Cargando asignaciones desde la API...");

  const [alumnos, carreras, cursos, bloques, pruebas, salas, usoSala, asignaciones] =
    await Promise.all([
      listAlumnos(),
      listCarreras(),
      listCursos(),
      listBloques(),
      listPruebas(),
      listSalas(),
      listUsoSala(),
      listAsignaciones(),
    ]);

  setReferenceData({ alumnos, carreras, cursos, bloques, pruebas, salas, usoSala, asignaciones });

  render(state);
  setStatusMessage("Conectado. Los datos vienen desde PostgreSQL a traves de FastAPI.");
}

function showError(error) {
  setStatusMessage(`No se pudo completar la solicitud: ${error.message}`);
}

bindFormHandlers({ loadData, showError });

loadData().catch((error) => {
  setStatusMessage(`No se pudieron cargar los datos de la API: ${error.message}`);
});
