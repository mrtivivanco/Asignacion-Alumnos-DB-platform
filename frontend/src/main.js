import "./styles.css";

import {
  getExamPdfMetadata,
  listCourseSections,
  listDegreePrograms,
  listExamBlocks,
  listExamRoomAssignments,
  listExams,
  listRooms,
  listStudentExamAssignments,
  listStudents,
} from "./api/academic.js";
import { setReferenceData, state } from "./state/store.js";
import { bindFormHandlers } from "./ui/forms.js";
import { bindNavigation } from "./ui/navigation.js";
import {
  bindFeedbackHandlers,
  bindFilterHandlers,
  render,
  setFeedbackMessage,
  setStatusMessage,
} from "./ui/render.js";

async function loadExamPdfMetadata(exams) {
  const examsWithPdf = exams
    .map((exam) => ({ examId: exam.exam_id ?? exam.id_evaluacion, hasPdf: Boolean(exam.pdf_file_id) }))
    .filter((exam) => exam.examId && exam.hasPdf);
  const metadataResults = await Promise.allSettled(
    examsWithPdf.map(async (exam) => [exam.examId, await getExamPdfMetadata(exam.examId)]),
  );

  return Object.fromEntries(
    metadataResults
      .filter((result) => result.status === "fulfilled")
      .map((result) => result.value),
  );
}

async function loadData() {
  setStatusMessage("Cargando asignaciones desde la API...");

  const [
    students,
    degreePrograms,
    courseSections,
    examBlocks,
    exams,
    rooms,
    examRoomAssignments,
    studentExamAssignments,
  ] =
    await Promise.all([
      listStudents(),
      listDegreePrograms(),
      listCourseSections(),
      listExamBlocks(),
      listExams(),
      listRooms(),
      listExamRoomAssignments(),
      listStudentExamAssignments(),
    ]);

  const examPdfMetadata = await loadExamPdfMetadata(exams);

  setReferenceData({
    students,
    degreePrograms,
    courseSections,
    examBlocks,
    exams,
    rooms,
    examRoomAssignments,
    studentExamAssignments,
    examPdfMetadata,
  });

  render(state);
  setStatusMessage("Conectado. Los datos vienen desde PostgreSQL a traves de FastAPI.");
}

function showError(error) {
  const message = `No se pudo completar la solicitud: ${error.message}`;
  setStatusMessage(message);
  setFeedbackMessage(message, "Operacion no completada");
}

bindNavigation();
bindFeedbackHandlers();
bindFilterHandlers(state);
bindFormHandlers({ loadData, showError, setFeedbackMessage, setStatusMessage });

loadData().catch((error) => {
  const message = `No se pudieron cargar los datos de la API: ${error.message}`;
  setStatusMessage(message);
  setFeedbackMessage(message, "Carga inicial fallida");
});
