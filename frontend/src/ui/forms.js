import {
  createExam,
  createExamRoomAssignment,
  deleteExamPdf,
  downloadExamPdf,
  getExamPdfMetadata,
  listExamAssignmentsByStudent,
  uploadExamPdf,
} from "../api/academic.js";
import { renderStudentExamAssignments } from "./render.js";

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function pdfFilename(metadata, examId) {
  return metadata?.filename || metadata?.metadata?.filename || `prueba-${examId}.pdf`;
}

export function bindFormHandlers({ loadData, showError, setFeedbackMessage, setStatusMessage }) {
  function reportError(error, action) {
    const message = `${action}: ${error.message}`;
    showError(error);
    setFeedbackMessage(message, "Operacion no completada");
  }

  document.querySelector("#prueba-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      await createExam({
        course_section_id: Number(formData.get("id_curso")),
        name: formData.get("nombre"),
        creation_year: Number(formData.get("anio_creacion")),
      });

      form.reset();
      await loadData();
      setStatusMessage("Prueba creada correctamente.");
      setFeedbackMessage("La prueba fue creada. Ahora puedes reservarle sala y bloque desde la pantalla correspondiente.", "Prueba creada");
    } catch (error) {
      reportError(error, "No se pudo crear la prueba");
    }
  });

  document.querySelector("#reserva-sala-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      await createExamRoomAssignment({
        exam_id: Number(formData.get("exam_id")),
        room_id: formData.get("room_id"),
        block_id: Number(formData.get("block_id")),
      });

      form.reset();
      await loadData();
      setStatusMessage("Reserva creada y alumnos asignados correctamente.");
      setFeedbackMessage(
        "La prueba quedo reservada en la sala y bloque seleccionados, y sus alumnos inscritos fueron asignados automaticamente.",
        "Reserva y asignaciones creadas",
      );
    } catch (error) {
      reportError(error, "No se pudo reservar la sala ni asignar alumnos");
    }
  });

  document.querySelector("#exam-pdf-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const examId = Number(formData.get("exam_id"));
    const file = formData.get("pdf_file");

    if (!file || typeof file === "string" || file.size === 0) {
      setFeedbackMessage("Selecciona un archivo PDF antes de cargar.", "PDF requerido");
      return;
    }

    try {
      const result = await uploadExamPdf(examId, file);

      form.reset();
      await loadData();
      setStatusMessage("PDF cargado correctamente.");
      setFeedbackMessage(`El PDF ${result.filename || file.name} quedo asociado a la prueba seleccionada.`, "PDF cargado");
    } catch (error) {
      reportError(error, "No se pudo cargar el PDF");
    }
  });

  document.querySelector("#exam-pdf-list").addEventListener("click", async (event) => {
    const button = event.target.closest?.("[data-pdf-action]");

    if (!button) {
      return;
    }

    const examId = Number(button.dataset.examId);
    const action = button.dataset.pdfAction;

    try {
      if (action === "download") {
        let metadata = null;

        try {
          metadata = await getExamPdfMetadata(examId);
        } catch {
          metadata = null;
        }

        const blob = await downloadExamPdf(examId);
        downloadBlob(blob, pdfFilename(metadata, examId));
        setStatusMessage("PDF descargado correctamente.");
        return;
      }

      if (action === "delete") {
        const shouldDelete = window.confirm("Eliminar el PDF asociado a esta prueba?");

        if (!shouldDelete) {
          return;
        }

        const result = await deleteExamPdf(examId);

        await loadData();
        setStatusMessage(result?.deleted === false ? "La prueba no tenia PDF asociado." : "PDF eliminado correctamente.");
        setFeedbackMessage(
          result?.deleted === false ? "La prueba seleccionada no tenia PDF para eliminar." : "El PDF fue eliminado de la prueba seleccionada.",
          "PDF actualizado",
        );
      }
    } catch (error) {
      reportError(error, action === "delete" ? "No se pudo eliminar el PDF" : "No se pudo descargar el PDF");
    }
  });

  document.querySelector("#load-alumno-asignaciones").addEventListener("click", async () => {
    const studentId = document.querySelector("#asignaciones-by-alumno-select").value;

    if (!studentId) {
      setFeedbackMessage("No hay un alumno seleccionado para consultar.", "Selecciona un alumno");
      return;
    }

    try {
      const assignments = await listExamAssignmentsByStudent(studentId);
      renderStudentExamAssignments(assignments);
      setStatusMessage("Asignaciones del alumno cargadas correctamente.");
    } catch (error) {
      reportError(error, "No se pudieron cargar las asignaciones del alumno");
    }
  });
}
