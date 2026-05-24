/**
 * CurriculumPage - Quản lý chương trình đào tạo
 * Admin: thêm, xóa chương trình
 */
import { useState, useEffect } from "react";
import { curriculumApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function CurriculumPage() {
  const { isAdmin } = useAuth();
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm]         = useState({ program_id: "", program_name: "" });
  const [saving, setSaving]     = useState(false);
  const [formError, setFormError] = useState("");
  const [error, setError]       = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await curriculumApi.list();
      setPrograms(res.data);
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
      await curriculumApi.create(form);
      setShowForm(false);
      setForm({ program_id: "", program_name: "" });
      fetchData();
    } catch (err) {
      setFormError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (programId) => {
    if (!window.confirm(`Xóa chương trình ${programId}?`)) return;
    try {
      await curriculumApi.delete(programId);
      fetchData();
    } catch (err) {
      alert("Xóa thất bại: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)" }}>
            Chương trình đào tạo
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>
            Quản lý các chương trình đào tạo trong hệ thống
          </p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => { setShowForm(true); setFormError(""); }}>
            + Thêm chương trình
          </button>
        )}
      </div>

      {/* Form thêm */}
      {showForm && isAdmin && (
        <div className="card" style={{ marginBottom: "24px", borderColor: "var(--accent)" }}>
          <div className="card-header">
            <h3 className="card-title">Thêm chương trình đào tạo</h3>
          </div>
          <form onSubmit={handleSave}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "16px", marginBottom: "16px" }}>
              <div>
                <label className="form-label">Mã chương trình *</label>
                <input
                  className="form-input"
                  placeholder="VD: CNTT-K67"
                  maxLength={10}
                  required
                  value={form.program_id}
                  onChange={e => setForm(f => ({ ...f, program_id: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Tên chương trình *</label>
                <input
                  className="form-input"
                  placeholder="VD: Công nghệ thông tin Khóa 67"
                  maxLength={30}
                  required
                  value={form.program_name}
                  onChange={e => setForm(f => ({ ...f, program_name: e.target.value }))}
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

      {error && (
        <div style={{ color: "var(--danger)", marginBottom: "16px" }}>{error}</div>
      )}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Danh sách ({programs.length})</h3>
        </div>
        {loading ? (
          <div className="loading-page"><div className="spinner" /></div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã chương trình</th>
                  <th>Tên chương trình</th>
                  {isAdmin && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {programs.length === 0 ? (
                  <tr><td colSpan={3} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px" }}>
                    Chưa có chương trình nào
                  </td></tr>
                ) : programs.map(p => (
                  <tr key={p.program_id}>
                    <td><code style={{ fontSize: "13px" }}>{p.program_id}</code></td>
                    <td style={{ fontWeight: 500 }}>{p.program_name}</td>
                    {isAdmin && (
                      <td>
                        <button
                          className="btn btn-ghost"
                          style={{ fontSize: "12px", padding: "4px 10px", color: "var(--danger)" }}
                          onClick={() => handleDelete(p.program_id)}
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
