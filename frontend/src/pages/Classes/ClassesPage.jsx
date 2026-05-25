/**
 * Trang Quản lý lớp học
 * Admin workflow:
 *   1. Tạo lớp học (course phải tồn tại trước)
 *   2. Gán giáo viên vào lớp
 *   3. Sinh viên đăng ký qua trang Enrollment
 */
import { useState, useEffect } from "react";
import { classesApi, teachersApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

// ── Modal Tạo lớp ────────────────────────────────────────────
function CreateClassModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ course_id: "", class_id: "", semester: "", capacity: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await classesApi.create({ ...form, capacity: form.capacity ? Number(form.capacity) : undefined });
      onCreated(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Tạo lớp thất bại");
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">➕ Tạo lớp học</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <div className="alert" style={{ background: "rgba(99,102,241,0.1)", borderColor: "var(--accent)", marginBottom: 16 }}>
            💡 Môn học phải được tạo trước trong <strong>Môn học</strong>. Mã môn phải chính xác.
          </div>
          <form id="create-class-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Mã môn học *</label>
              <input className="form-input" placeholder="VD: IT3000" required maxLength={10}
                value={form.course_id} onChange={(e) => setForm({...form, course_id: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Mã lớp *</label>
              <input className="form-input" placeholder="VD: IT3000-01" required maxLength={10}
                value={form.class_id} onChange={(e) => setForm({...form, class_id: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Học kỳ</label>
              <input className="form-input" placeholder="VD: 2024-1"
                value={form.semester} onChange={(e) => setForm({...form, semester: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Sĩ số tối đa</label>
              <input className="form-input" type="number" placeholder="VD: 40" min={1}
                value={form.capacity} onChange={(e) => setForm({...form, capacity: e.target.value})} />
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="create-class-form" type="submit" disabled={loading}>
            {loading ? "Đang tạo..." : "Tạo lớp"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Modal Gán giáo viên ───────────────────────────────────────
function AssignTeacherModal({ class_, onClose, onAssigned }) {
  const [teachers, setTeachers] = useState([]);
  const [form, setForm] = useState({ teacher_id: "", semester: class_.semester || "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    teachersApi.list().then((r) => setTeachers(r.data)).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await classesApi.assignTeacher(class_.course_id, class_.class_id, {
        teacher_id: form.teacher_id,
        semester: form.semester,
      });
      onAssigned();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Gán giáo viên thất bại");
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">👨‍🏫 Gán giáo viên vào lớp</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <p style={{ color: "var(--text-secondary)", marginBottom: 16, fontSize: 13 }}>
            Lớp: <strong>{class_.class_id}</strong> · Môn: <strong>{class_.course_id}</strong>
          </p>
          <form id="assign-teacher-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Chọn giáo viên *</label>
              <select className="form-select" required value={form.teacher_id}
                onChange={(e) => setForm({...form, teacher_id: e.target.value})}>
                <option value="">-- Chọn giáo viên --</option>
                {teachers.map((t) => (
                  <option key={t.teacher_id} value={t.teacher_id}>
                    {t.teacher_id} — {t.user?.name || "N/A"}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Học kỳ *</label>
              <input className="form-input" placeholder="VD: 2024-1" required
                value={form.semester} onChange={(e) => setForm({...form, semester: e.target.value})} />
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="assign-teacher-form" type="submit" disabled={loading}>
            {loading ? "Đang gán..." : "Gán giáo viên"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────
export default function ClassesPage() {
  const { isAdmin } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [semesterFilter, setSemesterFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [assignTarget, setAssignTarget] = useState(null); // lớp đang gán giáo viên
  const [error, setError] = useState("");

  const loadClasses = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await classesApi.list(null, semesterFilter || null, 1, 100);
      setClasses(res.data);
    } catch { setError("Không thể tải danh sách lớp học"); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadClasses(); }, [semesterFilter]);

  const handleDelete = async (courseId, classId) => {
    if (!window.confirm(`Xóa lớp "${classId}"? Tất cả đăng ký liên quan cũng sẽ bị xóa.`)) return;
    try {
      await classesApi.delete(courseId, classId);
      setClasses((prev) => prev.filter((c) => !(c.course_id === courseId && c.class_id === classId)));
    } catch (err) { setError(err.response?.data?.detail || "Xóa thất bại"); }
  };

  const filtered = classes.filter((c) =>
    c.class_id?.toLowerCase().includes(search.toLowerCase()) ||
    c.course_id?.toLowerCase().includes(search.toLowerCase())
  );

  const semesters = [...new Set(classes.map((c) => c.semester).filter(Boolean))];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">🏛️ Quản lý lớp học</h2>
          <p className="page-subtitle">Tổng cộng: {classes.length} lớp</p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            ➕ Tạo lớp học
          </button>
        )}
      </div>

      {/* Hướng dẫn workflow cho Admin */}
      {isAdmin && (
        <div className="card" style={{ marginBottom: 20, padding: "14px 20px", borderLeft: "4px solid var(--accent)" }}>
          <strong style={{ color: "var(--accent)" }}>📋 Quy trình tạo lớp học:</strong>
          <ol style={{ margin: "8px 0 0 20px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.8 }}>
            <li>Tạo <strong>Môn học</strong> (trang Môn học)</li>
            <li>Tạo <strong>Lớp học</strong> tại đây (nút Tạo lớp học)</li>
            <li><strong>Gán giáo viên</strong> vào lớp (nút 👨‍🏫 trong bảng bên dưới)</li>
            <li>Sinh viên <strong>đăng ký</strong> lớp qua trang Đăng ký học tập</li>
          </ol>
        </div>
      )}

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input className="form-input" placeholder="Tìm theo mã lớp, mã môn..."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="form-select" style={{ maxWidth: 160 }}
          value={semesterFilter} onChange={(e) => setSemesterFilter(e.target.value)}>
          <option value="">Tất cả học kỳ</option>
          {semesters.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏛️</div>
          <h3>Chưa có lớp học nào</h3>
          {isAdmin && <p style={{ color: "var(--text-secondary)", marginTop: 8 }}>Nhấn "Tạo lớp học" để bắt đầu</p>}
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã lớp</th>
                  <th>Mã môn</th>
                  <th>Học kỳ</th>
                  <th style={{ textAlign: "center" }}>Sĩ số tối đa</th>
                  {isAdmin && <th style={{ textAlign: "center" }}>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={`${c.course_id}-${c.class_id}`}>
                    <td><span className="badge badge-primary">{c.class_id}</span></td>
                    <td style={{ color: "var(--text-secondary)" }}>{c.course_id}</td>
                    <td>
                      {c.semester
                        ? <span className="badge badge-info">{c.semester}</span>
                        : <span style={{ color: "var(--text-muted)" }}>—</span>}
                    </td>
                    <td style={{ textAlign: "center" }}>{c.capacity ?? "—"}</td>
                    {isAdmin && (
                      <td style={{ textAlign: "center" }}>
                        <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            title="Gán giáo viên vào lớp này"
                            onClick={() => setAssignTarget(c)}
                          >
                            👨‍🏫 Gán GV
                          </button>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleDelete(c.course_id, c.class_id)}
                          >
                            🗑️ Xóa
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showCreate && (
        <CreateClassModal onClose={() => setShowCreate(false)} onCreated={loadClasses} />
      )}

      {assignTarget && (
        <AssignTeacherModal
          class_={assignTarget}
          onClose={() => setAssignTarget(null)}
          onAssigned={loadClasses}
        />
      )}
    </div>
  );
}
