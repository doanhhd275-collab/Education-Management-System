/**
 * Trang Điểm danh (Attendance)
 * - STUDENT: chọn lớp → xem lịch sử điểm danh của lớp đó (read-only)
 * - TEACHER/ADMIN: xem tất cả + điểm danh lớp học
 */
import { useState, useEffect } from "react";
import { attendanceApi, classesApi, enrollmentsApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function AttendancePage() {
  const { isTeacher, isAdmin, isStudent, user } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Student: lớp đã đăng ký + lớp đang chọn để xem điểm danh
  const [myClasses, setMyClasses] = useState([]);
  const [selectedStudentClass, setSelectedStudentClass] = useState("");

  // Filter cho TEACHER/ADMIN
  const [filterClass, setFilterClass] = useState("");
  const [filterStudent, setFilterStudent] = useState("");

  // State form điểm danh (Teacher/Admin)
  const [showMarkForm, setShowMarkForm] = useState(false);
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");
  const [studentsInClass, setStudentsInClass] = useState([]);
  const [lessonId, setLessonId] = useState("");
  const [attendanceData, setAttendanceData] = useState({});

  const loadRecords = async (filters = {}) => {
    setLoading(true);
    setError("");
    try {
      const res = await attendanceApi.list(filters);
      setRecords(res.data);
    } catch {
      setError("Không thể tải lịch sử điểm danh");
    } finally {
      setLoading(false);
    }
  };

  // Load lớp đã đăng ký của sinh viên
  const loadMyClasses = async () => {
    try {
      const res = await enrollmentsApi.list({ student_id: user.user_id });
      // Lấy danh sách lớp duy nhất
      const unique = [];
      const seen = new Set();
      for (const e of res.data) {
        if (!seen.has(e.class_id)) {
          seen.add(e.class_id);
          unique.push({ class_id: e.class_id, course_id: e.course_id });
        }
      }
      setMyClasses(unique);
    } catch {
      // ignore
    }
  };

  const loadClassesForTeacher = async () => {
    try {
      const res = await classesApi.list();
      setClasses(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (isStudent) {
      loadMyClasses();
      loadRecords(); // Load tất cả trước, user có thể lọc sau
    } else {
      loadRecords();
      if (isTeacher || isAdmin) loadClassesForTeacher();
    }
  }, [isStudent, isTeacher, isAdmin]);

  // Student chọn lớp → lọc lại
  const handleStudentClassChange = (e) => {
    const cls = e.target.value;
    setSelectedStudentClass(cls);
    if (cls) {
      loadRecords({ class_id: cls });
    } else {
      loadRecords();
    }
  };

  // TEACHER/ADMIN: lọc lại khi nhấn tìm kiếm
  const handleFilter = () => {
    const filters = {};
    if (filterClass) filters.class_id = filterClass;
    if (filterStudent) filters.student_id = filterStudent;
    loadRecords(filters);
  };

  const handleClassChange = async (e) => {
    const cid = e.target.value;
    setSelectedClass(cid);
    setStudentsInClass([]);
    if (!cid) return;
    try {
      const classObj = classes.find((c) => c.class_id === cid);
      if (classObj) {
        const res = await classesApi.getStudents(classObj.course_id, cid);
        setStudentsInClass(res.data);
        const initialData = {};
        res.data.forEach((s) => { initialData[s.student_id] = false; });
        setAttendanceData(initialData);
      }
    } catch {
      alert("Lỗi khi lấy danh sách sinh viên");
    }
  };

  const submitAttendance = async () => {
    if (!selectedClass || !lessonId) {
      alert("Vui lòng chọn lớp và nhập mã buổi học");
      return;
    }
    const classObj = classes.find((c) => c.class_id === selectedClass);
    const payload = studentsInClass.map((s) => ({
      class_id: selectedClass,
      course_id: classObj.course_id,
      day: new Date().toISOString(),
      student_id: s.student_id,
      lesson_id: lessonId,
      absent: attendanceData[s.student_id] || false,
      submit_assignment_status: false,
    }));
    try {
      await attendanceApi.mark(payload);
      alert("Điểm danh thành công!");
      setShowMarkForm(false);
      setSelectedClass("");
      setStudentsInClass([]);
      setLessonId("");
      loadRecords();
    } catch {
      alert("Lỗi khi điểm danh");
    }
  };

  // Tính thống kê cho sinh viên
  const totalSessions = records.length;
  const absentCount = records.filter((r) => r.absent).length;
  const presentCount = totalSessions - absentCount;
  const attendanceRate = totalSessions > 0
    ? Math.round((presentCount / totalSessions) * 100)
    : 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">✅ Điểm danh</h2>
          <p className="page-subtitle">
            {isStudent ? "Lịch sử điểm danh của bạn" : "Quản lý điểm danh lớp học"}
          </p>
        </div>
        {(isTeacher || isAdmin) && (
          <button
            className="btn btn-primary"
            onClick={() => setShowMarkForm(!showMarkForm)}
          >
            {showMarkForm ? "✖ Hủy" : "📝 Điểm danh lớp học"}
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {/* Thống kê + bộ lọc lớp cho SINH VIÊN */}
      {isStudent && (
        <>
          {!loading && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 24 }}>
              {[
                { label: "Tổng buổi học", value: totalSessions, color: "var(--accent)" },
                { label: "Có mặt", value: presentCount, color: "var(--success)" },
                { label: "Vắng mặt", value: absentCount, color: "#e74c3c" },
                {
                  label: "Tỷ lệ chuyên cần",
                  value: `${attendanceRate}%`,
                  color: attendanceRate >= 80 ? "var(--success)" : "#e74c3c",
                },
              ].map((stat) => (
                <div key={stat.label} className="card" style={{ textAlign: "center", padding: "16px 12px" }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: stat.color }}>{stat.value}</div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>{stat.label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Dropdown chọn lớp */}
          <div className="card" style={{ marginBottom: 20, padding: "16px 20px", display: "flex", alignItems: "center", gap: 16 }}>
            <span style={{ fontWeight: 600, whiteSpace: "nowrap", color: "var(--text-primary)" }}>🏛️ Lọc theo lớp:</span>
            <select
              className="form-select"
              value={selectedStudentClass}
              onChange={handleStudentClassChange}
              style={{ flex: 1, maxWidth: 320 }}
            >
              <option value="">-- Tất cả lớp --</option>
              {myClasses.map((c) => (
                <option key={c.class_id} value={c.class_id}>
                  {c.class_id} | Môn: {c.course_id}
                </option>
              ))}
            </select>
            {selectedStudentClass && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => { setSelectedStudentClass(""); loadRecords(); }}
              >
                ↺ Xem tất cả
              </button>
            )}
          </div>
        </>
      )}

      {/* Bộ lọc cho TEACHER/ADMIN */}
      {(isTeacher || isAdmin) && !showMarkForm && (
        <div className="card" style={{ marginBottom: 20, padding: "16px 20px" }}>
          <div className="flex gap-16" style={{ alignItems: "flex-end" }}>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Lọc theo lớp</label>
              <select
                className="form-input"
                value={filterClass}
                onChange={(e) => setFilterClass(e.target.value)}
              >
                <option value="">-- Tất cả lớp --</option>
                {classes.map((c) => (
                  <option key={c.class_id} value={c.class_id}>
                    {c.course_id} · {c.class_id}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Lọc theo sinh viên</label>
              <input
                className="form-input"
                placeholder="Nhập mã sinh viên..."
                value={filterStudent}
                onChange={(e) => setFilterStudent(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" onClick={handleFilter}>
              🔍 Tìm kiếm
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => { setFilterClass(""); setFilterStudent(""); loadRecords(); }}
            >
              ↺ Reset
            </button>
          </div>
        </div>
      )}

      {/* Form điểm danh (TEACHER/ADMIN) */}
      {showMarkForm && (
        <div className="card" style={{ marginBottom: 24, borderLeft: "4px solid var(--accent)" }}>
          <h3 className="card-title" style={{ marginBottom: 16 }}>Thực hiện điểm danh</h3>
          <div className="flex gap-16" style={{ marginBottom: 16 }}>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Chọn lớp</label>
              <select className="form-select" value={selectedClass} onChange={handleClassChange}>
                <option value="">-- Chọn lớp --</option>
                {classes.map((c) => (
                  <option key={c.class_id} value={c.class_id}>
                    {c.class_id} — {c.course_id}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Tên / Mã buổi học</label>
              <input
                className="form-input"
                placeholder="VD: Buổi 1, Week 2..."
                value={lessonId}
                onChange={(e) => setLessonId(e.target.value)}
              />
            </div>
          </div>

          {studentsInClass.length > 0 ? (
            <div>
              <table className="table" style={{ marginBottom: 16 }}>
                <thead>
                  <tr>
                    <th>Mã SV</th>
                    <th>Họ tên</th>
                    <th style={{ textAlign: "center" }}>Vắng mặt</th>
                  </tr>
                </thead>
                <tbody>
                  {studentsInClass.map((s) => (
                    <tr key={s.student_id}>
                      <td><span className="badge badge-muted">{s.student_id}</span></td>
                      <td>{s.student_name}</td>
                      <td style={{ textAlign: "center" }}>
                        <input
                          type="checkbox"
                          checked={attendanceData[s.student_id] || false}
                          onChange={(e) =>
                            setAttendanceData({ ...attendanceData, [s.student_id]: e.target.checked })
                          }
                          style={{ width: 18, height: 18, cursor: "pointer" }}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button className="btn btn-success" onClick={submitAttendance}>
                💾 Lưu điểm danh
              </button>
            </div>
          ) : selectedClass ? (
            <p style={{ color: "var(--text-secondary)", fontStyle: "italic" }}>
              Không có sinh viên trong lớp này.
            </p>
          ) : null}
        </div>
      )}

      {/* Danh sách lịch sử điểm danh */}
      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : records.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✅</div>
          <h3>Chưa có dữ liệu điểm danh</h3>
          {isStudent && (
            <p style={{ color: "var(--text-secondary)", marginTop: 8 }}>
              {selectedStudentClass
                ? `Lớp ${selectedStudentClass} chưa có buổi điểm danh nào.`
                : "Chọn lớp ở trên để xem, hoặc giáo viên chưa điểm danh."}
            </p>
          )}
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  {!isStudent && <th>Sinh viên</th>}
                  <th>Lớp</th>
                  <th>Môn học</th>
                  <th>Buổi học</th>
                  <th>Ngày</th>
                  <th style={{ textAlign: "center" }}>Trạng thái</th>
                  <th style={{ textAlign: "center" }}>Nộp bài</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, i) => (
                  <tr key={i}>
                    {!isStudent && (
                      <td><span className="badge badge-muted">{r.student_id}</span></td>
                    )}
                    <td><span className="badge badge-primary">{r.class_id}</span></td>
                    <td>
                      <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                        {r.course_id}
                      </span>
                    </td>
                    <td>{r.lesson_id}</td>
                    <td style={{ color: "var(--text-secondary)" }}>
                      {new Date(r.day).toLocaleDateString("vi-VN", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                      })}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      {r.absent
                        ? <span className="badge badge-danger">❌ Vắng mặt</span>
                        : <span className="badge badge-success">✅ Có mặt</span>}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      {r.submit_assignment_status
                        ? <span className="badge badge-success">Đã nộp</span>
                        : <span className="badge badge-muted">Chưa nộp</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
