/**
 * Auth API - Đăng nhập, đăng xuất, lấy thông tin user hiện tại
 */
import apiClient from "./client";

export const authApi = {
  // Đăng nhập
  login: (email, password) =>
    apiClient.post("/auth/login", { email, password }),

  // Đăng xuất
  logout: () => apiClient.post("/auth/logout"),

  // Lấy thông tin user đang đăng nhập
  getMe: () => apiClient.get("/auth/me"),
};

/**
 * Users API - Quản lý người dùng
 */
export const usersApi = {
  list: (page = 1, pageSize = 20) =>
    apiClient.get("/users", { params: { page, page_size: pageSize } }),

  create: (data) => apiClient.post("/users", data),

  getById: (userId) => apiClient.get(`/users/${userId}`),

  update: (userId, data) => apiClient.put(`/users/${userId}`, data),

  delete: (userId) => apiClient.delete(`/users/${userId}`),

  assignRole: (userId, roleId) =>
    apiClient.post(`/users/${userId}/roles`, { user_id: userId, role_id: roleId }),

  removeRole: (userId, roleId) =>
    apiClient.delete(`/users/${userId}/roles/${roleId}`),
};

/**
 * Students API - Quản lý sinh viên
 */
export const studentsApi = {
  list: (programId = null, page = 1, pageSize = 20) =>
    apiClient.get("/students", {
      params: { program_id: programId, page, page_size: pageSize },
    }),

  getById: (userId) => apiClient.get(`/students/${userId}`),

  update: (userId, data) => apiClient.put(`/students/${userId}`, data),

  getEnrollments: (userId) => apiClient.get(`/students/${userId}/enrollments`),
};

/**
 * Teachers API - Quản lý giáo viên
 */
export const teachersApi = {
  list: (page = 1, pageSize = 20) =>
    apiClient.get("/teachers", { params: { page, page_size: pageSize } }),

  create: (data) => apiClient.post("/teachers", data),

  getById: (teacherId) => apiClient.get(`/teachers/${teacherId}`),

  // Lấy thông tin teacher của user đang đăng nhập (dùng cho trang nhập điểm)
  getMyInfo: () => apiClient.get(`/teachers/me`),

  getClasses: (teacherId, semester = null) =>
    apiClient.get(`/teachers/${teacherId}/classes`, {
      params: { semester },
    }),
};

/**
 * Curriculum API - Chương trình đào tạo
 */
export const curriculumApi = {
  list: () => apiClient.get("/curriculum"),

  create: (data) => apiClient.post("/curriculum", data),

  getById: (programId) => apiClient.get(`/curriculum/${programId}`),

  update: (programId, data) => apiClient.put(`/curriculum/${programId}`, data),

  delete: (programId) => apiClient.delete(`/curriculum/${programId}`),

  addCourse: (programId, courseId) =>
    apiClient.post(`/curriculum/${programId}/courses`, {
      program_id: programId,
      course_id: courseId,
    }),

  removeCourse: (programId, courseId) =>
    apiClient.delete(`/curriculum/${programId}/courses/${courseId}`),
};

/**
 * Courses API - Môn học
 */
export const coursesApi = {
  list: () => apiClient.get("/courses"),

  create: (data) => apiClient.post("/courses", data),

  getById: (courseId) => apiClient.get(`/courses/${courseId}`),

  update: (courseId, data) => apiClient.put(`/courses/${courseId}`, data),

  delete: (courseId) => apiClient.delete(`/courses/${courseId}`),

  addPrerequisite: (courseId, prereqId) =>
    apiClient.post(`/courses/${courseId}/prerequisites`, {
      course_id: courseId,
      prerequisite_course_id: prereqId,
    }),

  removePrerequisite: (courseId, prereqId) =>
    apiClient.delete(`/courses/${courseId}/prerequisites/${prereqId}`),
};

/**
 * Classes API - Lớp học
 */
export const classesApi = {
  list: (courseId = null, semester = null, page = 1, pageSize = 20) =>
    apiClient.get("/classes", {
      params: { course_id: courseId, semester, page, page_size: pageSize },
    }),

  create: (data) => apiClient.post("/classes", data),

  getById: (courseId, classId) =>
    apiClient.get(`/classes/${courseId}/${classId}`),

  update: (courseId, classId, data) =>
    apiClient.put(`/classes/${courseId}/${classId}`, data),

  delete: (courseId, classId) =>
    apiClient.delete(`/classes/${courseId}/${classId}`),

  assignTeacher: (courseId, classId, data) =>
    apiClient.post(`/classes/${courseId}/${classId}/teachers`, data),

  getStudents: (courseId, classId) =>
    apiClient.get(`/classes/${courseId}/${classId}/students`),

  // Thời khóa biểu
  getTeacherTimetable: () => apiClient.get("/classes/timetable/teacher"),
  getStudentTimetable: () => apiClient.get("/classes/timetable/student"),
};

/**
 * Enrollments API - Đăng ký học
 */
export const enrollmentsApi = {
  list: (filters = {}) => apiClient.get("/enrollments", { params: filters }),

  enroll: (data) => apiClient.post("/enrollments", data),

  getById: (classId, studentId) =>
    apiClient.get(`/enrollments/${classId}/${studentId}`),

  updateScore: (classId, studentId, data) =>
    apiClient.put(`/enrollments/${classId}/${studentId}`, data),

  cancel: (classId, studentId) =>
    apiClient.delete(`/enrollments/${classId}/${studentId}`),
};

/**
 * Documents API - Tài liệu học tập
 */
export const documentsApi = {
  list: (teacherId = null, page = 1, pageSize = 20) =>
    apiClient.get("/documents", {
      params: { teacher_id: teacherId, page, page_size: pageSize },
    }),

  create: (data) => apiClient.post("/documents", data),

  getById: (documentId) => apiClient.get(`/documents/${documentId}`),

  update: (documentId, data) => apiClient.put(`/documents/${documentId}`, data),

  delete: (documentId) => apiClient.delete(`/documents/${documentId}`),
};

/**
 * Assignments API - Bài tập
 */
export const assignmentsApi = {
  list: (classId = null, courseId = null) =>
    apiClient.get("/assignments", {
      params: { class_id: classId, course_id: courseId },
    }),

  create: (data) => apiClient.post("/assignments", data),

  getById: (assignmentId) => apiClient.get(`/assignments/${assignmentId}`),

  update: (assignmentId, data) =>
    apiClient.put(`/assignments/${assignmentId}`, data),

  delete: (assignmentId) => apiClient.delete(`/assignments/${assignmentId}`),

  getReports: (assignmentId) =>
    apiClient.get(`/assignments/${assignmentId}/reports`),

  submit: (assignmentId, data) =>
    apiClient.post(`/assignments/${assignmentId}/submit`, data),
};

/**
 * Attendance API - Điểm danh
 */
export const attendanceApi = {
  list: (filters = {}) => apiClient.get("/attendance", { params: filters }),

  mark: (records) => apiClient.post("/attendance", records),

  update: (classId, day, studentId, lessonId, data) =>
    apiClient.put(`/attendance/${classId}/${day}/${studentId}/${lessonId}`, data),
};

/**
 * Logs API - Hệ thống
 */
export const logsApi = {
  getReportLogs: (filters = {}) =>
    apiClient.get("/logs/report", { params: filters }),

  getSystemLogs: (filters = {}) =>
    apiClient.get("/logs/system", { params: filters }),
};
