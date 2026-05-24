/**
 * Trang Quản lý lớp học
 */
import { useState, useEffect } from "react";
import { classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

function CreateClassModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ course_id: "", class_id: "", semester: "", capacity: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
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
          <form id="create-class-form" onSubmit={handleSubmit}>
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
            <div className="form-group">
              <label className="form-label">Học kỳ</label>
              <input className="form-input" placeholder="VD: 2024-1"
                value={form.semester} onChange={(e) => setForm({...form, semester: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Sĩ số tối đa</label>
              <input className="form-input" type="number" placeholder="VD: 40"
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

export default function ClassesPage() {
  const { isAdmin } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch]   = useState("");
  const [semesterFilter, setSemesterFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [error, setError] = useState("");

  const loadClasses = async () => {
    setLoading(true);
    try {
      const res = await classesApi.list(null, semesterFilter || null, 1, 100);
      setClasses(res.data);
    } catch { setError("Không thể tải danh sách lớp học"); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadClasses(); }, [semesterFilter]);

  const handleDelete = async (courseId, classId) => {
    if (!window.confirm(`Xóa lớp "${classId}"?`)) return;
    try {
      await classesApi.delete(courseId, classId);
      setClasses((prev) => prev.filter((c) => !(c.course_id === courseId && c.class_id === classId)));
    } catch (err) { setError(err.response?.data?.detail || "Xóa thất bại"); }
  };

  const filtered = classes.filter(
    (c) =>
      c.class_id?.toLowerCase().includes(search.toLowerCase()) ||
      c.course_id?.toLowerCase().includes(search.toLowerCase())
  );

  // Lấy danh sách học kỳ unique
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
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã lớp</th>
                  <th>Mã môn</th>
                  <th>Học kỳ</th>
                  <th>Sĩ số tối đa</th>
                  {isAdmin && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={`${c.course_id}-${c.class_id}`}>
                    <td><span className="badge badge-primary">{c.class_id}</span></td>
                    <td style={{ color: "var(--text-secondary)" }}>{c.course_id}</td>
                    <td>{c.semester ? <span className="badge badge-info">{c.semester}</span> : "—"}</td>
                    <td>{c.capacity ?? "—"}</td>
                    {isAdmin && (
                      <td>
                        <button className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(c.course_id, c.class_id)}>
                          🗑️ Xóa
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

      {showCreate && (
        <CreateClassModal onClose={() => setShowCreate(false)} onCreated={loadClasses} />
      )}
    </div>
  );
}
