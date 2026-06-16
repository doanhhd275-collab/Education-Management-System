/**
 * CurriculumPage - Quản lý chương trình đào tạo
 * Admin: thêm, sửa, xóa chương trình; thêm/xóa môn học trong chương trình
 */
import { useState, useEffect, useCallback } from "react";
import { curriculumApi, coursesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function CurriculumPage() {
  const { isAdmin } = useAuth();

  // ── Danh sách chương trình ──────────────────────────────────────
  const [programs, setPrograms]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");

  // ── Form tạo mới ────────────────────────────────────────────────
  const [showForm, setShowForm]   = useState(false);
  const [form, setForm]           = useState({ program_id: "", program_name: "" });
  const [saving, setSaving]       = useState(false);
  const [formError, setFormError] = useState("");

  // ── Chỉnh sửa tên chương trình ──────────────────────────────────
  const [editId, setEditId]       = useState(null);   // program_id đang sửa
  const [editName, setEditName]   = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState("");

  // ── Chi tiết + quản lý môn học ──────────────────────────────────
  const [detailId, setDetailId]           = useState(null);  // program_id đang xem
  const [detail, setDetail]               = useState(null);  // CurriculumResponse
  const [detailLoading, setDetailLoading] = useState(false);
  const [allCourses, setAllCourses]       = useState([]);    // toàn bộ môn học
  const [addCourseId, setAddCourseId]     = useState("");    // course_id sẽ thêm
  const [addPrereqId, setAddPrereqId]     = useState("");    // môn tiên quyết khi thêm
  const [courseAdding, setCourseAdding]   = useState(false);
  const [courseError, setCourseError]     = useState("");

  // ── Fetch danh sách ─────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await curriculumApi.list();
      setPrograms(res.data);
    } catch (err) {
      setError("Lỗi tải dữ liệu: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // ── Fetch chi tiết chương trình ─────────────────────────────────
  const openDetail = async (programId) => {
    setDetailId(programId);
    setDetailLoading(true);
    setCourseError("");
    setAddCourseId("");
    setAddPrereqId("");
    try {
      const [detRes, cRes] = await Promise.all([
        curriculumApi.getById(programId),
        coursesApi.list(),
      ]);
      setDetail(detRes.data);
      setAllCourses(cRes.data);
    } catch (err) {
      setCourseError("Lỗi tải chi tiết: " + (err.response?.data?.detail || err.message));
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setDetailId(null);
    setDetail(null);
    setCourseError("");
  };

  // ── Tạo chương trình mới ────────────────────────────────────────
  const handleCreate = async (e) => {
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

  // ── Xóa chương trình ────────────────────────────────────────────
  const handleDelete = async (programId) => {
    if (!window.confirm(`Xóa chương trình "${programId}"?`)) return;
    try {
      await curriculumApi.delete(programId);
      if (detailId === programId) closeDetail();
      fetchData();
    } catch (err) {
      alert("Xóa thất bại: " + (err.response?.data?.detail || err.message));
    }
  };

  // ── Bắt đầu sửa tên ─────────────────────────────────────────────
  const startEdit = (program) => {
    setEditId(program.program_id);
    setEditName(program.program_name);
    setEditError("");
  };

  const cancelEdit = () => {
    setEditId(null);
    setEditName("");
    setEditError("");
  };

  const handleSaveEdit = async (programId) => {
    if (!editName.trim()) { setEditError("Tên không được để trống"); return; }
    setEditSaving(true);
    setEditError("");
    try {
      await curriculumApi.update(programId, { program_name: editName.trim() });
      // Cập nhật lại local state
      setPrograms(prev =>
        prev.map(p => p.program_id === programId ? { ...p, program_name: editName.trim() } : p)
      );
      // Nếu đang xem detail thì refresh
      if (detailId === programId) {
        setDetail(prev => prev ? { ...prev, program_name: editName.trim() } : prev);
      }
      cancelEdit();
    } catch (err) {
      setEditError(err.response?.data?.detail || err.message);
    } finally {
      setEditSaving(false);
    }
  };

  // ── Thêm môn vào chương trình (kèm tiên quyết tuỳ chọn) ────────
  const handleAddCourse = async () => {
    if (!addCourseId) { setCourseError("Chọn môn học cần thêm"); return; }
    setCourseAdding(true);
    setCourseError("");
    try {
      // 1. Thêm môn vào chương trình
      await curriculumApi.addCourse(detailId, addCourseId);

      // 2. Nếu có chọn tiên quyết → đăng ký quan hệ tiên quyết
      if (addPrereqId) {
        try {
          await coursesApi.addPrerequisite(addCourseId, addPrereqId);
        } catch (prereqErr) {
          // Môn tiên quyết có thể đã được gán trước — không block luồng chính
          console.warn("addPrerequisite:", prereqErr?.response?.data?.detail || prereqErr.message);
        }
      }

      // 3. Refresh detail
      const res = await curriculumApi.getById(detailId);
      setDetail(res.data);
      setAddCourseId("");
      setAddPrereqId("");
    } catch (err) {
      setCourseError(err.response?.data?.detail || err.message);
    } finally {
      setCourseAdding(false);
    }
  };

  // ── Xóa môn khỏi chương trình ───────────────────────────────────
  const handleRemoveCourse = async (courseId) => {
    if (!window.confirm("Gỡ môn học này khỏi chương trình?")) return;
    try {
      await curriculumApi.removeCourse(detailId, courseId);
      setDetail(prev => ({
        ...prev,
        curriculum_courses: prev.curriculum_courses.filter(cc => cc.course_id !== courseId),
      }));
    } catch (err) {
      setCourseError(err.response?.data?.detail || err.message);
    }
  };

  // ── Danh sách môn chưa có trong chương trình ────────────────────
  const addedCourseIds = new Set((detail?.curriculum_courses || []).map(cc => cc.course_id));
  const availableCourses = allCourses.filter(c => !addedCourseIds.has(c.course_id));

  // ───────────────────────────────────────────────────────────────
  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)" }}>
            Chương trình đào tạo
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>
            Quản lý các chương trình đào tạo và môn học trong hệ thống
          </p>
        </div>
        {isAdmin && (
          <button
            className="btn btn-primary"
            onClick={() => { setShowForm(true); setFormError(""); }}
          >
            + Thêm chương trình
          </button>
        )}
      </div>

      {/* ── Form tạo mới ── */}
      {showForm && isAdmin && (
        <div className="card" style={{ marginBottom: "24px", borderColor: "var(--accent)" }}>
          <div className="card-header">
            <h3 className="card-title">Thêm chương trình đào tạo</h3>
          </div>
          <form onSubmit={handleCreate}>
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

      {error && <div style={{ color: "var(--danger)", marginBottom: "16px" }}>{error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: detailId ? "1fr 1fr" : "1fr", gap: "24px" }}>
        {/* ── Bảng danh sách ── */}
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
                    <th>Hành động</th>
                  </tr>
                </thead>
                <tbody>
                  {programs.length === 0 ? (
                    <tr>
                      <td colSpan={3} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px" }}>
                        Chưa có chương trình nào
                      </td>
                    </tr>
                  ) : programs.map(p => (
                    <tr
                      key={p.program_id}
                      style={{
                        background: detailId === p.program_id ? "var(--accent-subtle, rgba(99,102,241,0.08))" : undefined,
                      }}
                    >
                      <td><code style={{ fontSize: "13px" }}>{p.program_id}</code></td>
                      <td style={{ fontWeight: 500 }}>
                        {/* Inline edit */}
                        {isAdmin && editId === p.program_id ? (
                          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                            <input
                              className="form-input"
                              style={{ fontSize: "13px", padding: "4px 8px" }}
                              value={editName}
                              maxLength={100}
                              autoFocus
                              onChange={e => setEditName(e.target.value)}
                              onKeyDown={e => {
                                if (e.key === "Enter") handleSaveEdit(p.program_id);
                                if (e.key === "Escape") cancelEdit();
                              }}
                            />
                            {editError && (
                              <span style={{ color: "var(--danger)", fontSize: "12px" }}>❌ {editError}</span>
                            )}
                            <div style={{ display: "flex", gap: "6px" }}>
                              <button
                                className="btn btn-primary"
                                style={{ fontSize: "12px", padding: "3px 10px" }}
                                onClick={() => handleSaveEdit(p.program_id)}
                                disabled={editSaving}
                              >
                                {editSaving ? "..." : "✓ Lưu"}
                              </button>
                              <button
                                className="btn btn-ghost"
                                style={{ fontSize: "12px", padding: "3px 10px" }}
                                onClick={cancelEdit}
                              >
                                Hủy
                              </button>
                            </div>
                          </div>
                        ) : (
                          p.program_name
                        )}
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                          {/* Xem chi tiết / quản lý môn */}
                          <button
                            className="btn btn-ghost"
                            style={{ fontSize: "12px", padding: "4px 10px" }}
                            onClick={() =>
                              detailId === p.program_id ? closeDetail() : openDetail(p.program_id)
                            }
                          >
                            {detailId === p.program_id ? "✕ Đóng" : "📋 Môn học"}
                          </button>

                          {/* Sửa tên */}
                          {isAdmin && editId !== p.program_id && (
                            <button
                              className="btn btn-ghost"
                              style={{ fontSize: "12px", padding: "4px 10px" }}
                              onClick={() => startEdit(p)}
                            >
                              ✏️ Sửa
                            </button>
                          )}

                          {/* Xóa */}
                          {isAdmin && (
                            <button
                              className="btn btn-ghost"
                              style={{ fontSize: "12px", padding: "4px 10px", color: "var(--danger)" }}
                              onClick={() => handleDelete(p.program_id)}
                            >
                              🗑️ Xóa
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ── Panel chi tiết môn học ── */}
        {detailId && (
          <div className="card" style={{ borderColor: "var(--accent)", alignSelf: "start" }}>
            <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 className="card-title">
                  Môn học – <code style={{ fontSize: "14px" }}>{detailId}</code>
                </h3>
                {detail && (
                  <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
                    {detail.program_name}
                  </p>
                )}
              </div>
              <button
                className="btn btn-ghost"
                style={{ fontSize: "12px", padding: "4px 10px" }}
                onClick={closeDetail}
              >
                ✕ Đóng
              </button>
            </div>

            {detailLoading ? (
              <div className="loading-page"><div className="spinner" /></div>
            ) : (
              <>
                {/* Thêm môn — chỉ Admin */}
                {isAdmin && (
                  <div style={{ padding: "16px", borderBottom: "1px solid var(--border)" }}>
                    <label className="form-label">Thêm môn học vào chương trình</label>

                    {/* Dòng 1: chọn môn cần thêm */}
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginTop: "8px" }}>
                      <div>
                        <label style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px", display: "block" }}>
                          Môn học *
                        </label>
                        <select
                          className="form-input"
                          value={addCourseId}
                          onChange={e => { setAddCourseId(e.target.value); setCourseError(""); }}
                        >
                          <option value="">-- Chọn môn học --</option>
                          {availableCourses.map(c => (
                            <option key={c.course_id} value={c.course_id}>
                              [{c.course_id}] {c.course_name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px", display: "block" }}>
                          Môn tiên quyết
                        </label>
                        <select
                          className="form-input"
                          value={addPrereqId}
                          onChange={e => setAddPrereqId(e.target.value)}
                          disabled={!addCourseId}
                        >
                          <option value="">— Không có —</option>
                          {(detail?.curriculum_courses || []).map(cc => (
                            <option key={cc.course_id} value={cc.course_id}>
                              [{cc.course_id}] {cc.course?.course_name || cc.course_id}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <button
                      className="btn btn-primary"
                      style={{ marginTop: "10px" }}
                      onClick={handleAddCourse}
                      disabled={courseAdding || !addCourseId}
                    >
                      {courseAdding ? "Đang thêm..." : "+ Thêm môn học"}
                    </button>
                    {courseError && (
                      <div style={{ color: "var(--danger)", fontSize: "12px", marginTop: "6px" }}>
                        ❌ {courseError}
                      </div>
                    )}
                    {availableCourses.length === 0 && !detailLoading && (
                      <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "6px" }}>
                        Tất cả môn học đã có trong chương trình.
                      </p>
                    )}
                  </div>
                )}

                {/* Danh sách môn trong chương trình */}
                <div className="table-wrapper">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Mã môn</th>
                        <th>Tên môn học</th>
                        {isAdmin && <th></th>}
                      </tr>
                    </thead>
                    <tbody>
                      {(!detail?.curriculum_courses || detail.curriculum_courses.length === 0) ? (
                        <tr>
                          <td colSpan={3} style={{ textAlign: "center", color: "var(--text-muted)", padding: "24px" }}>
                            Chưa có môn học nào trong chương trình
                          </td>
                        </tr>
                      ) : detail.curriculum_courses.map(cc => (
                        <tr key={cc.course_id}>
                          <td>
                            <code style={{ fontSize: "12px" }}>{cc.course_id}</code>
                          </td>
                          <td style={{ fontSize: "14px" }}>
                            {cc.course?.course_name || cc.course_id}
                          </td>
                          {isAdmin && (
                            <td>
                              <button
                                className="btn btn-ghost"
                                style={{ fontSize: "11px", padding: "3px 8px", color: "var(--danger)" }}
                                onClick={() => handleRemoveCourse(cc.course_id)}
                              >
                                🗑️ Gỡ
                              </button>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
