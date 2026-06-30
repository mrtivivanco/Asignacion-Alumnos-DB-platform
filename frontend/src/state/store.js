export const state = {
  students: [],
  degreePrograms: [],
  courseSections: [],
  examBlocks: [],
  exams: [],
  rooms: [],
  examRoomAssignments: [],
  studentExamAssignments: [],
  examPdfMetadata: {},
};

export function setReferenceData({
  students,
  degreePrograms,
  courseSections,
  examBlocks,
  exams,
  rooms,
  examRoomAssignments,
  studentExamAssignments,
  examPdfMetadata = {},
}) {
  state.students = students;
  state.degreePrograms = degreePrograms;
  state.courseSections = courseSections;
  state.examBlocks = examBlocks;
  state.exams = exams;
  state.rooms = rooms;
  state.examRoomAssignments = examRoomAssignments;
  state.studentExamAssignments = studentExamAssignments;
  state.examPdfMetadata = examPdfMetadata;
}
