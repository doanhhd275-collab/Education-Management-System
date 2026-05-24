/**
 * Trang Đăng ký học tập
 * - Sinh viên: xem lớp đã đăng ký + đăng ký thêm
 * - Admin: xem tất cả, nhập điểm
 * - Teacher: nhập điểm
 */
import { useState, useEffect } from "react";
import { enrollmentsApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

// Modal đăng ký lớp mới
function EnrollModal({ onClose, onEnrolled, studentId }) {
  const [form, setForm] = useState({ class_id: "", course_id: "", student_id: studentId });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await enrollmentsApi.enroll(form);
      onEnrolled(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Đăng ký thất bại");
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📝 Đăng ký lớp học</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <form id="enroll-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Mã môn học *</label>
              <input className="form-input" placeholder="VD: IT3000" required
                value={form.course_id} onChange={(e) => setForm({...form, course_id: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Mã lớp *</label>
              <input className="form-input" placeholder="VD: IT3000-01" required
                value={form.class_id} onChange={(e) => setForm({...form, class_id: e.target.value})} />
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="enroll-form" type="submit" disabled={loading}>
            {loading ? "Đang đăng ký..." : "Đăng ký"}
          </button>
        </div>
      </div>
    </div>
  );
}

// Modal nhập điểm
function ScoreModal({ enrollment, onClose, onUpdated }) {
  const [form, setForm] = useState({
    midterm_score: enrollment.midterm_score ?? "",
    final_term_score: enrollment.final_term_score ?? "",
    grade: enrollment.grade ?? "",
    status: enrollment.status ?? "STUDYING",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await enrollmentsApi.updateScore(enrollment.class_id, enrollment.student_id, {
        midterm_score: form.midterm_score !== "" ? Number(form.midterm_score) : undefined,
        final_term_score: form.final_term_score !== "" ? Number(form.final_term_score) : undefined,
        grade: form.grade || undefined,
        status: form.status,
      });
      onUpdated(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Cập nhật thất bại");
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">✏️ Nhập điểm</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <p style={{ color: "var(--text-muted)", marginBottom: 16, fontSize: 13 }}>
            SV: <strong>{enrollment.student_id}</strong> | Lớp: <strong>{enrollment.class_id}</strong>
          </p>
          <form id="score-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Điểm giữa kỳ (0-10)</label>
              <input className="form-input" type="number" step="0.1" min="0" max="10"
                value={form.midterm_score} onChange={(e) => setForm({...form, midterm_score: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Điểm cuối kỳ (0-10)</label>
              <input className="form-input" type="number" step="0.1" min="0" max="10"
                value={form.final_term_score} onChange={(e) => setForm({...form, final_term_score: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Xếp loại</label>
              <select className="form-select" value={form.grade} onChange={(e) => setForm({...form, grade: e.target.value})}>
                <option value="">Chọn xếp loại</option>
                {["A", "B", "C", "D", "F"].map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Trạng thái</label>
              <select className="form-select" value={form.status} onChange={(e) => setForm({...form, status: e.target.value})}>
                <option value="STUDYING">Đang học</option>
                <option value="PASSED">Đã qua</option>
                <option value="FAILED">Rớt</option>
              </select>
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="score-form" type="submit" disabled={loading}>
            {loading ? "Đang lưu..." : "Lưu điểm"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function EnrollmentsPage() {
  const { user, isStudent, isAdmin, isTeacher } = useAuth();
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [showEnroll, setShowEnroll]   = useState(false);
  const [editEnrollment, setEditEnrollment] = useState(null);
  const [error, setError] = useState("");

  const loadEnrollments = async () => {
    setLoading(true);
    try {
      const filters = isStudent ? { student_id: user.user_id } : {};
      const res = await enrollmentsApi.list(filters);
      setEnrollments(res.data);
    } catch { setError("Không thể tải danh sách đăng ký"); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadEnrollments(); }, []);

  const getStatusBadge = (status) => ({
    STUDYING: <span className="badge badge-info">Đang học</span>,
    PASSED:   <span className="badge badge-success">Đã qua</span>,
    FAILED:   <span className="badge badge-danger">Rớt</span>,
  }[status] || <span className="badge badge-muted">{status}</span>);

  const getGradeBadge = (grade) => ({
    A: <span className="badge badge-success">A</span>,
    B: <span className="badge badge-primary">B</span>,
    C: <span className="badge badge-warning">C</span>,
    D: <span className="badge badge-warning">D</span>,
    F: <span className="badge badge-danger">F</span>,
  }[grade] || <span style={{ color: "var(--text-muted)" }}>—</span>);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">📝 Đăng ký học tập</h2>
          <p className="page-subtitle">
            {isStudent ? `Lớp đã đăng ký: ${enrollments.length}` : `Tổng: ${enrollments.length} enrollment`}
          </p>
        </div>
        {isStudent && (
          <button className="btn btn-primary" onClick={() => setShowEnroll(true)}>
            ➕ Đăng ký lớp học
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : enrollments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <h3>Chưa có đăng ký nào</h3>
          {isStudent && <p>Nhấn "Đăng ký lớp học" để bắt đầu</p>}
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  {!isStudent && <th>Sinh viên</th>}
                  <th>Mã lớp</th>
                  <th>Mã môn</th>
                  <th>Điểm GK</th>
                  <th>Điểm CK</th>
                  <th>Xếp loại</th>
                  <th>Trạng thái</th>
                  {(isAdmin || isTeacher) && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {enrollments.map((e) => (
                  <tr key={`${e.class_id}-${e.student_id}`}>
                    {!isStudent && <td><span className="badge badge-muted">{e.student_id}</span></td>}
                    <td><span className="badge badge-primary">{e.class_id}</span></td>
                    <td style={{ color: "var(--text-secondary)" }}>{e.course_id}</td>
                    <td style={{ fontWeight: 500 }}>{e.midterm_score?.toFixed(1) ?? "—"}</td>
                    <td style={{ fontWeight: 500 }}>{e.final_term_score?.toFixed(1) ?? "—"}</td>
                    <td>{getGradeBadge(e.grade)}</td>
                    <td>{getStatusBadge(e.status)}</td>
                    {(isAdmin || isTeacher) && (
                      <td>
                        <button className="btn btn-secondary btn-sm"
                          onClick={() => setEditEnrollment(e)}>
                          ✏️ Nhập điểm
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showEnroll && (
        <EnrollModal
          studentId={user.user_id}
          onClose={() => setShowEnroll(false)}
          onEnrolled={loadEnrollments}
        />
      )}

      {editEnrollment && (
        <ScoreModal
          enrollment={editEnrollment}
          onClose={() => setEditEnrollment(null)}
          onUpdated={loadEnrollments}
        />
      )}
    </div>
  );
}
