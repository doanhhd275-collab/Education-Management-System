/**
 * Trang Điểm danh (Attendance)
 */
import { useState, useEffect } from "react";
import { attendanceApi, classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function AttendancePage() {
  const { isTeacher, isAdmin, isStudent, user } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // State cho việc điểm danh mới (Teacher/Admin)
  const [showMarkForm, setShowMarkForm] = useState(false);
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");
  const [studentsInClass, setStudentsInClass] = useState([]);
  const [lessonId, setLessonId] = useState("");
  const [attendanceData, setAttendanceData] = useState({}); // { studentId: true/false }

  const loadRecords = async () => {
    setLoading(true);
    try {
      const filters = isStudent ? { student_id: user.user_id } : {};
      const res = await attendanceApi.list(filters);
      setRecords(res.data);
    } catch { setError("Không thể tải lịch sử điểm danh"); }
    finally { setLoading(false); }
  };

  const loadClassesForTeacher = async () => {
    try {
      // Tạm thời lấy tất cả lớp (nếu là teacher/admin)
      const res = await classesApi.list();
      setClasses(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { 
    loadRecords(); 
    if (isTeacher || isAdmin) loadClassesForTeacher();
  }, [isStudent, isTeacher, isAdmin, user.user_id]);

  const handleClassChange = async (e) => {
    const cid = e.target.value;
    setSelectedClass(cid);
    if (!cid) {
      setStudentsInClass([]);
      return;
    }
    try {
      const classObj = classes.find(c => c.class_id === cid);
      if (classObj) {
        const res = await classesApi.getStudents(classObj.course_id, cid);
        setStudentsInClass(res.data);
        
        // Khởi tạo data điểm danh (mặc định có mặt = false, tức absent = false)
        const initialData = {};
        res.data.forEach(s => { initialData[s.student_id] = false; });
        setAttendanceData(initialData);
      }
    } catch (err) {
      alert("Lỗi khi lấy ds sinh viên");
    }
  };

  const submitAttendance = async () => {
    if (!selectedClass || !lessonId) {
      alert("Vui lòng chọn lớp và nhập mã bài học (VD: Buổi 1)");
      return;
    }
    
    const classObj = classes.find(c => c.class_id === selectedClass);
    
    const payload = studentsInClass.map(s => ({
      class_id: selectedClass,
      course_id: classObj.course_id,
      day: new Date().toISOString(),
      student_id: s.student_id,
      lesson_id: lessonId,
      absent: attendanceData[s.student_id] || false,
      submit_assignment_status: false
    }));

    try {
      await attendanceApi.mark(payload);
      alert("Điểm danh thành công!");
      setShowMarkForm(false);
      loadRecords();
    } catch (err) {
      alert("Lỗi khi điểm danh");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">✅ Điểm danh</h2>
          <p className="page-subtitle">Lịch sử điểm danh</p>
        </div>
        {(isTeacher || isAdmin) && (
          <button className="btn btn-primary" onClick={() => setShowMarkForm(!showMarkForm)}>
            {showMarkForm ? "Hủy điểm danh" : "📝 Điểm danh lớp học"}
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {/* Form điểm danh */}
      {showMarkForm && (
        <div className="card" style={{ marginBottom: 24, borderLeft: "4px solid var(--accent)" }}>
          <h3 className="card-title" style={{ marginBottom: 16 }}>Thực hiện điểm danh</h3>
          <div className="flex gap-16" style={{ marginBottom: 16 }}>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Chọn lớp</label>
              <select className="form-select" value={selectedClass} onChange={handleClassChange}>
                <option value="">-- Chọn lớp --</option>
                {classes.map(c => <option key={c.class_id} value={c.class_id}>{c.class_id}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ flex: 1, margin: 0 }}>
              <label className="form-label">Tên/Mã buổi học</label>
              <input className="form-input" placeholder="VD: Buổi 1, Week 2..." 
                value={lessonId} onChange={e => setLessonId(e.target.value)} />
            </div>
          </div>
          
          {studentsInClass.length > 0 && (
            <div>
              <table className="table" style={{ marginBottom: 16 }}>
                <thead>
                  <tr>
                    <th>Mã SV</th>
                    <th>Họ tên</th>
                    <th>Vắng mặt?</th>
                  </tr>
                </thead>
                <tbody>
                  {studentsInClass.map(s => (
                    <tr key={s.student_id}>
                      <td><span className="badge badge-muted">{s.student_id}</span></td>
                      <td>{s.student_name}</td>
                      <td>
                        <input type="checkbox" 
                          checked={attendanceData[s.student_id]} 
                          onChange={(e) => setAttendanceData({...attendanceData, [s.student_id]: e.target.checked})} 
                          style={{ width: 18, height: 18 }}
                        /> 
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button className="btn btn-success" onClick={submitAttendance}>💾 Lưu điểm danh</button>
            </div>
          )}
        </div>
      )}

      {/* Danh sách lịch sử */}
      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : records.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✅</div>
          <h3>Chưa có dữ liệu điểm danh</h3>
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  {!isStudent && <th>Sinh viên</th>}
                  <th>Lớp</th>
                  <th>Buổi</th>
                  <th>Ngày</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, i) => (
                  <tr key={i}>
                    {!isStudent && <td><span className="badge badge-muted">{r.student_id}</span></td>}
                    <td><span className="badge badge-primary">{r.class_id}</span></td>
                    <td>{r.lesson_id}</td>
                    <td style={{ color: "var(--text-secondary)" }}>
                      {new Date(r.day).toLocaleDateString("vi-VN")}
                    </td>
                    <td>
                      {r.absent 
                        ? <span className="badge badge-danger">Vắng mặt</span> 
                        : <span className="badge badge-success">Có mặt</span>}
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
