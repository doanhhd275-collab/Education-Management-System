/**
 * CoursesPage - Quản lý môn học
 * Admin: thêm, xóa môn học + quản lý môn tiên quyết
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

  // Quản lý môn tiên quyết
  const [prereqModal, setPrereqModal] = useState(null); // course object đang quản lý prereq
  const [prereqList, setPrereqList]   = useState([]);   // danh sách prereq của course đang chọn
  const [prereqLoading, setPrereqLoading] = useState(false);
  const [addPrereqId, setAddPrereqId] = useState("");   // mã môn sẽ thêm vào
  const [prereqError, setPrereqError] = useState("");
  const [prereqSaving, setPrereqSaving] = useState(false);

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

  // ── Tạo môn học ──────────────────────────────────────────────────
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

  // ── Xóa môn học ──────────────────────────────────────────────────
  const handleDelete = async (courseId) => {
    if (!window.confirm(`Xóa môn học ${courseId}?`)) return;
    try {
      await coursesApi.delete(courseId);
      fetchData();
    } catch (err) {
      alert("Xóa thất bại: " + (err.response?.data?.detail || err.message));
    }
  };

  // ── Mở modal quản lý tiên quyết ──────────────────────────────────
  const openPrereqModal = async (course) => {
    setPrereqModal(course);
    setAddPrereqId("");
    setPrereqError("");
    setPrereqLoading(true);
    try {
      const res = await coursesApi.getById(course.course_id);
      setPrereqList(res.data.prerequisites || []);
    } catch (err) {
      setPrereqError("Lỗi tải tiên quyết: " + (err.response?.data?.detail || err.message));
    } finally {
      setPrereqLoading(false);
    }
  };

  const closePrereqModal = () => {
    setPrereqModal(null);
    setPrereqList([]);
    setAddPrereqId("");
    setPrereqError("");
  };

  // ── Thêm môn tiên quyết ──────────────────────────────────────────
  const handleAddPrereq = async () => {
    if (!addPrereqId.trim()) return;
    setPrereqSaving(true);
    setPrereqError("");
    try {
      await coursesApi.addPrerequisite(prereqModal.course_id, addPrereqId.trim());
      setAddPrereqId("");
      // Reload
      const res = await coursesApi.getById(prereqModal.course_id);
      setPrereqList(res.data.prerequisites || []);
    } catch (err) {
      setPrereqError(err.response?.data?.detail || err.message);
    } finally {
      setPrereqSaving(false);
    }
  };

  // ── Xóa (drop) môn tiên quyết ────────────────────────────────────
  const handleRemovePrereq = async (prereqId) => {
    if (!window.confirm(`Bỏ môn tiên quyết "${prereqId}" khỏi "${prereqModal.course_id}"?`)) return;
    setPrereqError("");
    try {
      await coursesApi.removePrerequisite(prereqModal.course_id, prereqId);
      setPrereqList(prev => prev.filter(p => p.prerequisite_course_id !== prereqId));
    } catch (err) {
      setPrereqError(err.response?.data?.detail || err.message);
    }
  };

  // ── Render ────────────────────────────────────────────────────────
  return (
    <div>
      {/* Header */}
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

      {/* Form thêm môn học */}
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
                  maxLength={100}
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

      {/* Bảng danh sách môn học */}
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
                  <th>Môn tiên quyết</th>
                  {isAdmin && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {courses.length === 0 ? (
                  <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px" }}>
                    Chưa có môn học nào
                  </td></tr>
                ) : courses.map(c => (
                  <tr key={c.course_id}>
                    <td><code style={{ fontSize: "13px" }}>{c.course_id}</code></td>
                    <td style={{ fontWeight: 500 }}>{c.course_name}</td>
                    <td>
                      {/* Hiển thị số lượng tiên quyết, click để quản lý */}
                      <button
                        className="btn btn-ghost"
                        style={{ fontSize: "12px", padding: "4px 10px" }}
                        onClick={() => openPrereqModal(c)}
                        title="Quản lý môn tiên quyết"
                      >
                        🔗 Tiên quyết
                      </button>
                    </td>
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

      {/* ── Modal quản lý môn tiên quyết ── */}
      {prereqModal && (
        <div
          style={{
            position: "fixed", inset: 0, zIndex: 1000,
            background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
          onClick={e => { if (e.target === e.currentTarget) closePrereqModal(); }}
        >
          <div
            className="card"
            style={{
              width: "100%", maxWidth: "540px", margin: "16px",
              background: "var(--surface)", border: "1px solid var(--border)",
              borderRadius: "12px", padding: "0",
              boxShadow: "0 24px 60px rgba(0,0,0,0.5)",
            }}
          >
            {/* Modal header */}
            <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 className="card-title">Môn tiên quyết</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "2px" }}>
                  Môn học: <strong style={{ color: "var(--text-primary)" }}>{prereqModal.course_id} – {prereqModal.course_name}</strong>
                </p>
              </div>
              <button className="btn btn-ghost" style={{ padding: "4px 8px", fontSize: "16px" }} onClick={closePrereqModal}>✕</button>
            </div>

            {/* Body */}
            <div style={{ padding: "16px 20px 20px" }}>
              {prereqError && (
                <div style={{ color: "var(--danger)", fontSize: "13px", marginBottom: "12px" }}>❌ {prereqError}</div>
              )}

              {/* Thêm tiên quyết (admin only) */}
              {isAdmin && (
                <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
                  <select
                    className="form-input"
                    style={{ flex: 1 }}
                    value={addPrereqId}
                    onChange={e => setAddPrereqId(e.target.value)}
                  >
                    <option value="">-- Chọn môn tiên quyết --</option>
                    {courses
                      .filter(c =>
                        c.course_id !== prereqModal.course_id &&
                        !prereqList.some(p => p.prerequisite_course_id === c.course_id)
                      )
                      .map(c => (
                        <option key={c.course_id} value={c.course_id}>
                          {c.course_id} – {c.course_name}
                        </option>
                      ))
                    }
                  </select>
                  <button
                    className="btn btn-primary"
                    style={{ whiteSpace: "nowrap" }}
                    disabled={!addPrereqId || prereqSaving}
                    onClick={handleAddPrereq}
                  >
                    {prereqSaving ? "..." : "+ Thêm"}
                  </button>
                </div>
              )}

              {/* Danh sách tiên quyết hiện có */}
              {prereqLoading ? (
                <div style={{ textAlign: "center", padding: "24px" }}><div className="spinner" /></div>
              ) : prereqList.length === 0 ? (
                <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "24px", fontSize: "14px" }}>
                  Chưa có môn tiên quyết nào
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {prereqList.map(p => (
                    <div
                      key={p.prerequisite_course_id}
                      style={{
                        display: "flex", alignItems: "center", justifyContent: "space-between",
                        padding: "10px 14px",
                        background: "var(--surface-2, rgba(255,255,255,0.04))",
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                      }}
                    >
                      <div>
                        <code style={{ fontSize: "13px", color: "var(--accent)" }}>
                          {p.prerequisite_course_id}
                        </code>
                        {p.prerequisite_course_name && (
                          <span style={{ marginLeft: "8px", fontSize: "13px", color: "var(--text-secondary)" }}>
                            – {p.prerequisite_course_name}
                          </span>
                        )}
                      </div>
                      {isAdmin && (
                        <button
                          className="btn btn-ghost"
                          style={{ fontSize: "12px", padding: "3px 8px", color: "var(--danger)" }}
                          onClick={() => handleRemovePrereq(p.prerequisite_course_id)}
                          title="Bỏ môn tiên quyết này"
                        >
                          🗑️ Bỏ
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
