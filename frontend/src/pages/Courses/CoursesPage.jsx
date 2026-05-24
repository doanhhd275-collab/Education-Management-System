/**
 * CoursesPage - Quản lý môn học
 * Admin: thêm, xóa môn học
 */
import { useState, useEffect } from "react";
import { coursesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function CoursesPage() {
  const { isAdmin } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm]       = useState({ course_id: "", course_name: "" });
  const [saving, setSaving]   = useState(false);
  const [formError, setFormError] = useState("");
  const [error, setError]     = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await coursesApi.list();
      setCourses(res.data);
    } catch (err) {
      setError("Lỗi tải dữ liệu: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      await coursesApi.create(form);
      setShowForm(false);
      setForm({ course_id: "", course_name: "" });
      fetchData();
    } catch (err) {
      setFormError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (courseId) => {
    if (!window.confirm(`Xóa môn học ${courseId}?`)) return;
    try {
      await coursesApi.delete(courseId);
      fetchData();
    } catch (err) {
      alert("Xóa thất bại: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)" }}>Môn học</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>
            Quản lý các môn học trong hệ thống
          </p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => { setShowForm(true); setFormError(""); }}>
            + Thêm môn học
          </button>
        )}
      </div>

      {showForm && isAdmin && (
        <div className="card" style={{ marginBottom: "24px", borderColor: "var(--accent)" }}>
          <div className="card-header">
            <h3 className="card-title">Thêm môn học mới</h3>
          </div>
          <form onSubmit={handleSave}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "16px", marginBottom: "16px" }}>
              <div>
                <label className="form-label">Mã môn học *</label>
                <input
                  className="form-input"
                  placeholder="VD: IT3007"
                  maxLength={10}
                  required
                  value={form.course_id}
                  onChange={e => setForm(f => ({ ...f, course_id: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Tên môn học *</label>
                <input
                  className="form-input"
                  placeholder="VD: Hệ điều hành"
                  maxLength={30}
                  required
                  value={form.course_name}
                  onChange={e => setForm(f => ({ ...f, course_name: e.target.value }))}
                />
              </div>
            </div>
            {formError && (
              <div style={{ color: "var(--danger)", fontSize: "13px", marginBottom: "12px" }}>❌ {formError}</div>
            )}
            <div style={{ display: "flex", gap: "10px" }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Đang lưu..." : "✓ Lưu"}
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Hủy</button>
            </div>
          </form>
        </div>
      )}

      {error && <div style={{ color: "var(--danger)", marginBottom: "16px" }}>{error}</div>}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Danh sách môn học ({courses.length})</h3>
        </div>
        {loading ? (
          <div className="loading-page"><div className="spinner" /></div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã môn</th>
                  <th>Tên môn học</th>
                  {isAdmin && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {courses.length === 0 ? (
                  <tr><td colSpan={3} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px" }}>
                    Chưa có môn học nào
                  </td></tr>
                ) : courses.map(c => (
                  <tr key={c.course_id}>
                    <td><code style={{ fontSize: "13px" }}>{c.course_id}</code></td>
                    <td style={{ fontWeight: 500 }}>{c.course_name}</td>
                    {isAdmin && (
                      <td>
                        <button
                          className="btn btn-ghost"
                          style={{ fontSize: "12px", padding: "4px 10px", color: "var(--danger)" }}
                          onClick={() => handleDelete(c.course_id)}
                        >
                          🗑️ Xóa
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
