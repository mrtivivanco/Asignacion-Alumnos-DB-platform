import {
  createCourseExamAssignments,
  createExam,
  createExamRoomAssignment,
  createStudent,
  createStudentProgram,
  deleteExamPdf,
  downloadExamPdf,
  getExamPdfMetadata,
  listExamAssignmentsByStudent,
  uploadExamPdf,
} from "../api/academic.js";
import { renderStudentExamAssignments } from "./render.js";

function parseExamRoomAssignmentKey(value) {
  const [examId, roomId, blockId] = value.split("|");
  return {
    exam_id: Number(examId),
    room_id: roomId,
    block_id: Number(blockId),
  };
}

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

export function bindFormHandlers({ loadData, showError, setFeedbackMessage, setStatusMessage, recordConflictMessage }) {
  function reportError(error, action, { recordConflict = false } = {}) {
    const message = `${action}: ${error.message}`;
    showError(error);
    setFeedbackMessage(message, "Operacion no completada");
    if (recordConflict) {
      recordConflictMessage(message);
    }
  }

  document.querySelector("#alumno-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const studentId = String(formData.get("rut")).trim();
    const programId = Number(formData.get("id_carrera"));

    try {
      await createStudent({
        student_id: studentId,
        first_name: formData.get("nombre"),
        last_name: formData.get("apellido"),
        email: formData.get("email") || null,
      });

      await createStudentProgram({
        student_id: studentId,
        program_id: programId,
      });

      form.reset();
      await loadData();
      setStatusMessage("Alumno guardado correctamente.");
      setFeedbackMessage("El alumno fue registrado y asociado a su carrera.", "Alumno guardado");
    } catch (error) {
      reportError(error, "No se pudo guardar el alumno");
    }
  });

  document.querySelector("#asignacion-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const examRoomAssignment = parseExamRoomAssignmentKey(formData.get("uso_sala_key"));

    try {
      const result = await createCourseExamAssignments(examRoomAssignment);
      const totalAssigned = result?.total_assigned ?? 0;
      const totalEnrolled = result?.total_enrolled ?? totalAssigned;
      const totalConflicts = result?.total_conflicts ?? result?.conflicts?.length ?? 0;
      const conflictText = totalConflicts > 0
        ? ` ${totalConflicts} alumnos fueron omitidos por conflictos.`
        : " No se detectaron conflictos.";

      form.reset();
      await loadData();
      setStatusMessage(
        `Asignacion por curso lista: ${totalAssigned} de ${totalEnrolled} alumnos asignados.${conflictText}`,
      );
      setFeedbackMessage(
        `Se asignaron ${totalAssigned} de ${totalEnrolled} alumnos para la prueba seleccionada.${conflictText} Revisa la pagina de conflictos para ver el detalle persistido.`,
        totalConflicts > 0 ? "Asignaciones con conflictos" : "Asignaciones generadas",
      );
    } catch (error) {
      reportError(error, "No se pudieron generar las asignaciones", { recordConflict: true });
    }
  });

  document.querySelector("#prueba-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const blockId = Number(formData.get("n_bloque"));

    try {
      const exam = await createExam({
        course_section_id: Number(formData.get("id_curso")),
        block_id: blockId,
        name: formData.get("nombre"),
        creation_year: Number(formData.get("anio_creacion")),
      });

      await createExamRoomAssignment({
        exam_id: exam.exam_id,
        room_id: formData.get("id_sala"),
        block_id: blockId,
      });

      form.reset();
      await loadData();
      setStatusMessage("Prueba creada y sala reservada correctamente.");
      setFeedbackMessage("La prueba fue creada y quedo asociada a la sala y bloque seleccionados.", "Prueba creada");
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
      setStatusMessage("Reserva de sala creada correctamente.");
      setFeedbackMessage("La sala quedo reservada para la prueba y bloque seleccionados.", "Reserva creada");
    } catch (error) {
      reportError(error, "No se pudo reservar la sala");
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

    try {
      const assignments = await listExamAssignmentsByStudent(studentId);
      renderStudentExamAssignments(assignments);
      setStatusMessage("Asignaciones del alumno cargadas correctamente.");
    } catch (error) {
      reportError(error, "No se pudieron cargar las asignaciones del alumno");
    }
  });
}
