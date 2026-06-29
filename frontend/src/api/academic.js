import { fetchBlob, fetchJson } from "./client.js";

function withQuery(path, params = {}) {
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, value);
    }
  }

  const query = searchParams.toString();
  return query ? `${path}?${query}` : path;
}

export function listStudents(params) {
  return fetchJson(withQuery("/api/students", params));
}

export function createStudent(studentData) {
  return fetchJson("/api/students", {
    method: "POST",
    body: JSON.stringify(studentData),
  });
}

export function updateStudent(studentId, studentData) {
  return fetchJson(`/api/students/${encodeURIComponent(studentId)}`, {
    method: "PATCH",
    body: JSON.stringify(studentData),
  });
}

export function deleteStudent(studentId) {
  return fetchJson(`/api/students/${encodeURIComponent(studentId)}`, { method: "DELETE" });
}

export function listDegreePrograms(params) {
  return fetchJson(withQuery("/api/degree-programs", params));
}

export function createDegreeProgram(programData) {
  return fetchJson("/api/degree-programs", {
    method: "POST",
    body: JSON.stringify(programData),
  });
}

export function updateDegreeProgram(programId, programData) {
  return fetchJson(`/api/degree-programs/${programId}`, {
    method: "PATCH",
    body: JSON.stringify(programData),
  });
}

export function deleteDegreeProgram(programId) {
  return fetchJson(`/api/degree-programs/${programId}`, { method: "DELETE" });
}

export function createStudentProgram(studentProgramData) {
  return fetchJson("/api/student-programs", {
    method: "POST",
    body: JSON.stringify(studentProgramData),
  });
}

export function listCourseSections(params) {
  return fetchJson(withQuery("/api/course-sections", params));
}

export function createCourseSection(courseSectionData) {
  return fetchJson("/api/course-sections", {
    method: "POST",
    body: JSON.stringify(courseSectionData),
  });
}

export function updateCourseSection(courseSectionId, courseSectionData) {
  return fetchJson(`/api/course-sections/${courseSectionId}`, {
    method: "PATCH",
    body: JSON.stringify(courseSectionData),
  });
}

export function deleteCourseSection(courseSectionId) {
  return fetchJson(`/api/course-sections/${courseSectionId}`, { method: "DELETE" });
}

export function listCourseEnrollments(params) {
  return fetchJson(withQuery("/api/course-enrollments", params));
}

export function createCourseEnrollment(courseEnrollmentData) {
  return fetchJson("/api/course-enrollments", {
    method: "POST",
    body: JSON.stringify(courseEnrollmentData),
  });
}

export function listExamBlocks() {
  return fetchJson("/api/exam-blocks");
}

export function createExamBlock(examBlockData) {
  return fetchJson("/api/exam-blocks", {
    method: "POST",
    body: JSON.stringify(examBlockData),
  });
}

export function updateExamBlock(blockId, examBlockData) {
  return fetchJson(`/api/exam-blocks/${blockId}`, {
    method: "PATCH",
    body: JSON.stringify(examBlockData),
  });
}

export function deleteExamBlock(blockId) {
  return fetchJson(`/api/exam-blocks/${blockId}`, { method: "DELETE" });
}

export function listExams(params) {
  return fetchJson(withQuery("/api/exams", params));
}

export function createExam(examData) {
  return fetchJson("/api/exams", {
    method: "POST",
    body: JSON.stringify(examData),
  });
}

export function listRooms(params) {
  return fetchJson(withQuery("/api/rooms", params));
}

export function createRoom(roomData) {
  return fetchJson("/api/rooms", {
    method: "POST",
    body: JSON.stringify(roomData),
  });
}

export function updateRoom(roomId, roomData) {
  return fetchJson(`/api/rooms/${encodeURIComponent(roomId)}`, {
    method: "PATCH",
    body: JSON.stringify(roomData),
  });
}

export function deleteRoom(roomId) {
  return fetchJson(`/api/rooms/${encodeURIComponent(roomId)}`, { method: "DELETE" });
}

export function listExamRoomAssignments(params) {
  return fetchJson(withQuery("/api/exam-room-assignments", params));
}

export function createExamRoomAssignment(examRoomAssignmentData) {
  return fetchJson("/api/exam-room-assignments", {
    method: "POST",
    body: JSON.stringify(examRoomAssignmentData),
  });
}

export function updateExamRoomAssignment(blockId, roomId, examRoomAssignmentData) {
  return fetchJson(`/api/exam-room-assignments/${blockId}/${encodeURIComponent(roomId)}`, {
    method: "PATCH",
    body: JSON.stringify(examRoomAssignmentData),
  });
}

export function deleteExamRoomAssignment(blockId, roomId) {
  return fetchJson(`/api/exam-room-assignments/${blockId}/${encodeURIComponent(roomId)}`, {
    method: "DELETE",
  });
}

export function listStudentExamAssignments(params) {
  return fetchJson(withQuery("/api/student-exam-assignments", params));
}

export function createCourseExamAssignments(courseExamAssignmentData) {
  return fetchJson("/api/student-exam-assignments/course", {
    method: "POST",
    body: JSON.stringify(courseExamAssignmentData),
  });
}

export function listExamAssignmentsByStudent(studentId) {
  return fetchJson(`/api/students/${encodeURIComponent(studentId)}/exam-assignments`);
}

export function listAssignmentConflicts(params) {
  return fetchJson(withQuery("/api/assignment-conflicts", params));
}

export function uploadExamPdf(examId, file) {
  const formData = new FormData();
  formData.set("file", file);

  return fetchJson(`/api/exams/${examId}/pdf`, {
    method: "POST",
    body: formData,
  });
}

export function downloadExamPdf(examId) {
  return fetchBlob(`/api/exams/${examId}/pdf`);
}

export function getExamPdfMetadata(examId) {
  return fetchJson(`/api/exams/${examId}/pdf/metadata`);
}

export function deleteExamPdf(examId) {
  return fetchJson(`/api/exams/${examId}/pdf`, { method: "DELETE" });
}
