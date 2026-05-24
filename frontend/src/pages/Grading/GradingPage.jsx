/**
 * GradingPage - Trang nhập điểm (Giáo viên)
 *
 * Luồng:
 *   1. Giáo viên xem danh sách lớp của mình
 *   2. Chọn lớp → xem sinh viên đã đăng ký
 *   3. Nhập điểm giữa kỳ / cuối kỳ / xếp loại cho từng sinh viên
 *
 * Admin cũng có thể dùng trang này để nhập điểm (xem tất cả lớp).
 */
import { useState, useEffect } from "react";
import { teachersApi, enrollmentsApi, classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

// ── Modal nhập/sửa điểm ─────────────────────────────────────────
function ScoreModal({ enrollment, onClose, onSaved }) {
  const [form, setForm] = useState({
    midterm_score:    enrollment.midterm_score   ?? "",
    final_term_score: enrollment.final_term_score ?? "",
    grade:  enrollment.grade  ?? "",
    status: enrollment.status ?? "STUDYING",
  });
  const [saving, setSaving] = useState(false);
  const [error,  setError]  = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await enrollmentsApi.updateScore(enrollment.class_id, enrollment.student_id, {
        midterm_score:    form.midterm_score    !== "" ? Number(form.midterm_score)    : undefined,
        final_term_score: form.final_term_score !== "" ? Number(form.final_term_score) : undefined,
        grade:  form.grade  || undefined,
        status: form.status,
      });
      onSaved();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Cập nhật thất bại");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 440 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">✏️ Nhập điểm</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <div style={{
            padding: "10px 14px", background: "var(--bg-tertiary)",
            borderRadius: "var(--radius)", marginBottom: 16, fontSize: 13,
          }}>
            Sinh viên: <strong>{enrollment.student_id}</strong>
            &nbsp;|&nbsp; Lớp: <strong>{enrollment.class_id}</strong>
          </div>
          <form id="score-form" onSubmit={handleSubmit}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div>
                <label className="form-label">Điểm giữa kỳ (0–10)</label>
                <input className="form-input" type="number" step="0.1" min="0" max="10"
                  placeholder="0.0"
                  value={form.midterm_score}
                  onChange={(e) => setForm({ ...form, midterm_score: e.target.value })} />
              </div>
              <div>
                <label className="form-label">Điểm cuối kỳ (0–10)</label>
                <input className="form-input" type="number" step="0.1" min="0" max="10"
                  placeholder="0.0"
                  value={form.final_term_score}
                  onChange={(e) => setForm({ ...form, final_term_score: e.target.value })} />
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label className="form-label">Xếp loại</label>
                <select className="form-select" value={form.grade}
                  onChange={(e) => setForm({ ...form, grade: e.target.value })}>
                  <option value="">— Chưa xếp —</option>
                  {["A", "B+", "B", "C+", "C", "D+", "D", "F"].map(g =>
                    <option key={g} value={g}>{g}</option>
                  )}
                </select>
              </div>
              <div>
                <label className="form-label">Trạng thái</label>
                <select className="form-select" value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <option value="STUDYING">Đang học</option>
                  <option value="PASSED">Đã qua</option>
                  <option value="FAILED">Rớt</option>
                </select>
              </div>
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="score-form" type="submit" disabled={saving}>
            {saving ? "Đang lưu..." : "💾 Lưu điểm"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Grade badge ──────────────────────────────────────────────────
const GradeBadge = ({ grade }) => {
  const colors = { A: "success", "B+": "success", B: "primary", "C+": "primary", C: "warning", "D+": "warning", D: "warning", F: "danger" };
  if (!grade) return <span style={{ color: "var(--text-muted)" }}>—</span>;
  return <span className={`badge badge-${colors[grade] || "muted"}`}>{grade}</span>;
};

const StatusBadge = ({ status }) => ({
  STUDYING: <span className="badge badge-info">Đang học</span>,
  PASSED:   <span className="badge badge-success">Đã qua</span>,
  FAILED:   <span className="badge badge-danger">Rớt</span>,
}[status] || <span className="badge badge-muted">{status}</span>);

// ── Main component ───────────────────────────────────────────────
export default function GradingPage() {
  const { user, isAdmin, isTeacher } = useAuth();

  const [myTeacherId,    setMyTeacherId]    = useState(null);
  const [teacherClasses, setTeacherClasses] = useState([]);  // lớp của GV
  const [selectedClass,  setSelectedClass]  = useState(null); // {class_id, course_id, semester}
  const [enrollments,    setEnrollments]    = useState([]);   // sinh viên trong lớp
  const [scoreTarget,    setScoreTarget]    = useState(null); // enrollment đang nhập điểm
  const [loading,        setLoading]        = useState(true);
  const [loadingEnroll,  setLoadingEnroll]  = useState(false);
  const [error,          setError]          = useState("");

  // Bước 1: Lấy teacher_id của user đang đăng nhập
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        if (isTeacher) {
          const res = await teachersApi.getMyInfo();
          setMyTeacherId(res.data.teacher_id);
          // Bước 2: Lấy danh sách lớp
          const classRes = await teachersApi.getClasses(res.data.teacher_id);
          setTeacherClasses(classRes.data);
        } else if (isAdmin) {
          // Admin: không cần teacher_id, có thể chọn lớp từ dropdown
          setTeacherClasses([]); // Admin sẽ nhập class_id thủ công
        }
      } catch (err) {
        setError("Không tìm thấy thông tin giáo viên: " + (err.response?.data?.detail || err.message));
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [isTeacher, isAdmin]);

  // Bước 3: Khi chọn lớp → load sinh viên
  const handleSelectClass = async (cls) => {
    setSelectedClass(cls);
    setEnrollments([]);
    setLoadingEnroll(true);
    try {
      const res = await enrollmentsApi.list({ class_id: cls.class_id, course_id: cls.course_id });
      setEnrollments(res.data);
    } catch (err) {
      setError("Lỗi tải danh sách sinh viên: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoadingEnroll(false);
    }
  };

  if (loading) return <div className="loading-page"><div className="spinner" /> Đang tải...</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">✏️ Nhập điểm</h2>
          <p className="page-subtitle">
            {isTeacher ? `Lớp đang dạy: ${teacherClasses.length}` : "Admin: nhập điểm cho tất cả lớp"}
          </p>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20 }}>
        {/* Cột trái: Danh sách lớp */}
        <div>
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border-light)" }}>
              <h3 className="card-title">📚 Lớp của tôi</h3>
            </div>
            {teacherClasses.length === 0 ? (
              <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>
                Chưa được phân công lớp nào
              </div>
            ) : (
              <div>
                {teacherClasses.map((cls) => {
                  const isSelected = selectedClass?.class_id === cls.class_id
                    && selectedClass?.course_id === cls.course_id;
                  return (
                    <div
                      key={`${cls.course_id}-${cls.class_id}`}
                      onClick={() => handleSelectClass(cls)}
                      style={{
                        padding: "12px 16px",
                        borderBottom: "1px solid var(--border-light)",
                        cursor: "pointer",
                        background: isSelected ? "var(--accent-light)" : "transparent",
                        borderLeft: isSelected ? "3px solid var(--accent)" : "3px solid transparent",
                        transition: "var(--transition)",
                      }}
                    >
                      <div style={{ fontWeight: 600, fontSize: 13, color: isSelected ? "var(--accent)" : "var(--text-primary)" }}>
                        {cls.class_id}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                        Môn: {cls.course_id} · HK: {cls.semester}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Cột phải: Danh sách sinh viên + nhập điểm */}
        <div>
          {!selectedClass ? (
            <div className="card">
              <div className="empty-state">
                <div className="empty-state-icon">👈</div>
                <h3>Chọn lớp để xem sinh viên</h3>
                <p>Click vào một lớp ở bên trái để xem danh sách sinh viên và nhập điểm.</p>
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: 0 }}>
              <div style={{
                padding: "14px 20px", borderBottom: "1px solid var(--border-light)",
                display: "flex", alignItems: "center", justifyContent: "space-between",
              }}>
                <div>
                  <h3 className="card-title">
                    Lớp: {selectedClass.class_id}
                    <span style={{ marginLeft: 8 }} className="badge badge-primary">{selectedClass.course_id}</span>
                  </h3>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                    Học kỳ: {selectedClass.semester} · {enrollments.length} sinh viên
                  </div>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => handleSelectClass(selectedClass)}>
                  🔄 Tải lại
                </button>
              </div>

              {loadingEnroll ? (
                <div className="loading-page" style={{ minHeight: 150 }}>
                  <div className="spinner" /> Đang tải sinh viên...
                </div>
              ) : enrollments.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon">👥</div>
                  <h3>Chưa có sinh viên đăng ký lớp này</h3>
                </div>
              ) : (
                <div className="table-wrapper">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Mã SV</th>
                        <th style={{ textAlign: "center" }}>Điểm GK</th>
                        <th style={{ textAlign: "center" }}>Điểm CK</th>
                        <th style={{ textAlign: "center" }}>Xếp loại</th>
                        <th style={{ textAlign: "center" }}>Trạng thái</th>
                        <th style={{ textAlign: "center" }}>Hành động</th>
                      </tr>
                    </thead>
                    <tbody>
                      {enrollments.map((e) => (
                        <tr key={`${e.class_id}-${e.student_id}`}>
                          <td>
                            <span className="badge badge-muted">{e.student_id}</span>
                          </td>
                          <td style={{ textAlign: "center", fontWeight: 600 }}>
                            {e.midterm_score != null ? (
                              <span style={{ color: e.midterm_score >= 5 ? "var(--success)" : "var(--danger)" }}>
                                {e.midterm_score.toFixed(1)}
                              </span>
                            ) : "—"}
                          </td>
                          <td style={{ textAlign: "center", fontWeight: 600 }}>
                            {e.final_term_score != null ? (
                              <span style={{ color: e.final_term_score >= 5 ? "var(--success)" : "var(--danger)" }}>
                                {e.final_term_score.toFixed(1)}
                              </span>
                            ) : "—"}
                          </td>
                          <td style={{ textAlign: "center" }}>
                            <GradeBadge grade={e.grade} />
                          </td>
                          <td style={{ textAlign: "center" }}>
                            <StatusBadge status={e.status} />
                          </td>
                          <td style={{ textAlign: "center" }}>
                            <button
                              className="btn btn-primary btn-sm"
                              onClick={() => setScoreTarget(e)}
                            >
                              ✏️ Nhập điểm
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal nhập điểm */}
      {scoreTarget && (
        <ScoreModal
          enrollment={scoreTarget}
          onClose={() => setScoreTarget(null)}
          onSaved={() => handleSelectClass(selectedClass)}
        />
      )}
    </div>
  );
}
