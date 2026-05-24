/**
 * UsersPage - Quản lý người dùng (chỉ ADMIN)
 * Chức năng: xem danh sách, thêm, xóa, gán role
 */
import { useState, useEffect } from "react";
import { usersApi } from "../../api";

const ROLES = [
  { id: "ADMIN",   label: "Quản trị viên" },
  { id: "TEACHER", label: "Giáo viên" },
  { id: "STUDENT", label: "Sinh viên" },
];

const roleBadge = { ADMIN: "badge-danger", TEACHER: "badge-warning", STUDENT: "badge-info" };
const roleLabel = { ADMIN: "Quản trị viên", TEACHER: "Giáo viên", STUDENT: "Sinh viên" };

const EMPTY_FORM = {
  user_id: "", email: "", name: "", contact: "", password: "", role_id: "STUDENT",
};

export default function UsersPage() {
  const [users, setUsers]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm]       = useState(EMPTY_FORM);
  const [saving, setSaving]   = useState(false);
  const [formError, setFormError] = useState("");

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.list(1, 100);
      setUsers(res.data);
    } catch (err) {
      setError("Không tải được danh sách người dùng: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      const { role_id, ...userData } = form;
      // 1. Tạo user
      const res = await usersApi.create(userData);
      const newUserId = res.data.user_id;
      // 2. Gán role
      await usersApi.assignRole(newUserId, role_id);
      setShowForm(false);
      setForm(EMPTY_FORM);
      fetchUsers();
    } catch (err) {
      setFormError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm(`Xóa người dùng ${userId}? Hành động này không thể hoàn tác.`)) return;
    try {
      await usersApi.delete(userId);
      setUsers(prev => prev.filter(u => u.user_id !== userId));
    } catch (err) {
      alert("Xóa thất bại: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)" }}>
            Quản lý người dùng
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>
            Thêm, xóa và quản lý tài khoản hệ thống
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => { setShowForm(true); setFormError(""); }}>
          + Thêm người dùng
        </button>
      </div>

      {/* Form thêm người dùng */}
      {showForm && (
        <div className="card" style={{ marginBottom: "24px", borderColor: "var(--accent)" }}>
          <div className="card-header">
            <h3 className="card-title">Thêm người dùng mới</h3>
          </div>
          <form onSubmit={handleSave}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>
              <div>
                <label className="form-label">Mã người dùng *</label>
                <input
                  className="form-input"
                  placeholder="VD: U010"
                  maxLength={10}
                  required
                  value={form.user_id}
                  onChange={e => setForm(f => ({ ...f, user_id: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Họ và tên *</label>
                <input
                  className="form-input"
                  placeholder="VD: Nguyễn Văn A"
                  maxLength={30}
                  required
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Email *</label>
                <input
                  className="form-input"
                  type="email"
                  placeholder="VD: user@ems.edu.vn"
                  required
                  value={form.email}
                  onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Mật khẩu *</label>
                <input
                  className="form-input"
                  type="password"
                  placeholder="Tối thiểu 6 ký tự"
                  minLength={6}
                  required
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Số điện thoại</label>
                <input
                  className="form-input"
                  placeholder="VD: 0901234567"
                  maxLength={15}
                  value={form.contact}
                  onChange={e => setForm(f => ({ ...f, contact: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">Vai trò *</label>
                <select
                  className="form-input"
                  value={form.role_id}
                  onChange={e => setForm(f => ({ ...f, role_id: e.target.value }))}
                >
                  {ROLES.map(r => (
                    <option key={r.id} value={r.id}>{r.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {formError && (
              <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid var(--danger)", borderRadius: "8px", padding: "10px 14px", color: "var(--danger)", fontSize: "13px", marginBottom: "12px" }}>
                ❌ {formError}
              </div>
            )}

            <div style={{ display: "flex", gap: "10px" }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Đang lưu..." : "✓ Lưu người dùng"}
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => { setShowForm(false); setForm(EMPTY_FORM); }}>
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ color: "var(--danger)", padding: "12px", background: "rgba(239,68,68,0.1)", borderRadius: "8px", marginBottom: "16px" }}>
          {error}
        </div>
      )}

      {/* Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Danh sách người dùng ({users.length})</h3>
        </div>
        {loading ? (
          <div className="loading-page"><div className="spinner" /> Đang tải...</div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã</th>
                  <th>Họ và tên</th>
                  <th>Email</th>
                  <th>SĐT</th>
                  <th>Vai trò</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px" }}>
                    Chưa có người dùng nào
                  </td></tr>
                ) : users.map(u => (
                  <tr key={u.user_id}>
                    <td><code style={{ fontSize: "12px" }}>{u.user_id}</code></td>
                    <td style={{ fontWeight: 500 }}>{u.name}</td>
                    <td style={{ color: "var(--text-muted)" }}>{u.email}</td>
                    <td style={{ color: "var(--text-muted)" }}>{u.contact || "—"}</td>
                    <td>
                      <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                        {u.user_roles?.length > 0
                          ? u.user_roles.map(ur => (
                              <span key={ur.role_id} className={`badge ${roleBadge[ur.role_id] || "badge-info"}`}>
                                {roleLabel[ur.role_id] || ur.role_id}
                              </span>
                            ))
                          : <span className="badge badge-default">Chưa có role</span>
                        }
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost"
                        style={{ fontSize: "12px", padding: "4px 10px", color: "var(--danger)" }}
                        onClick={() => handleDelete(u.user_id)}
                      >
                        🗑️ Xóa
                      </button>
                    </td>
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
