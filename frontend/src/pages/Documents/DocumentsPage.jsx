/**
 * Trang Tài liệu học tập
 * - Teacher: đăng tài liệu (chọn lớp/môn từ dropdown), teacher_id tự động từ JWT
 * - Student/All: xem và mở link tài liệu (có thể lọc theo lớp)
 */
import { useState, useEffect } from "react";
import { documentsApi, classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

/* ─── Modal đăng tài liệu (Teacher) ─────────────────────────────── */
function CreateDocModal({ onClose, onCreated, myClasses }) {
  const [form, setForm] = useState({
    document_id: "",
    document_name: "",
    link_url: "",
    deadline: "",
    class_id: "",
    course_id: "",
  });
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handleClassChange = (e) => {
    const sel = myClasses.find((c) => c.class_id === e.target.value);
    setForm((f) => ({
      ...f,
      class_id:  e.target.value,
      course_id: sel ? sel.course_id : f.course_id,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await documentsApi.create({
        document_id:   form.document_id,
        document_name: form.document_name,
        link_url:      form.link_url  || undefined,
        deadline:      form.deadline  || undefined,
        class_id:      form.class_id  || undefined,
        course_id:     form.course_id || undefined,
      });
      onCreated(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Tạo tài liệu thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📄 Đăng tài liệu mới</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <form id="doc-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Mã tài liệu *</label>
              <input
                className="form-input" placeholder="VD: DOC010" required maxLength={10}
                value={form.document_id} onChange={(e) => setForm({ ...form, document_id: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Tên tài liệu *</label>
              <input
                className="form-input" placeholder="VD: Slide bài giảng Tuần 1" required
                value={form.document_name} onChange={(e) => setForm({ ...form, document_name: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Lớp học</label>
              {myClasses.length > 0 ? (
                <select className="form-input" value={form.class_id} onChange={handleClassChange}>
                  <option value="">-- Chọn lớp (tùy chọn) --</option>
                  {myClasses.map((c) => (
                    <option key={c.class_id} value={c.class_id}>
                      {c.course_id} · {c.class_id}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  className="form-input" placeholder="VD: CS101-01" maxLength={10}
                  value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })}
                />
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Mã môn học</label>
              <input
                className="form-input" placeholder="VD: CS101" maxLength={10}
                value={form.course_id} onChange={(e) => setForm({ ...form, course_id: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Link tài liệu</label>
              <input
                className="form-input" type="url" placeholder="https://drive.google.com/..."
                value={form.link_url} onChange={(e) => setForm({ ...form, link_url: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Hạn (tuỳ chọn)</label>
              <input
                className="form-input" type="datetime-local"
                value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })}
              />
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="doc-form" type="submit" disabled={loading}>
            {loading ? "Đang lưu..." : "Đăng tài liệu"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Main Page ───────────────────────────────────────────────── */
export default function DocumentsPage() {
  const { isTeacher, isAdmin, isStudent, user } = useAuth();
  const [docs,        setDocs]        = useState([]);
  const [myClasses,   setMyClasses]   = useState([]);
  const [filterClass, setFilterClass] = useState("");
  const [loading,     setLoading]     = useState(true);
  const [showCreate,  setShowCreate]  = useState(false);
  const [search,      setSearch]      = useState("");
  const [error,       setError]       = useState("");

  const loadAll = async () => {
    setLoading(true);
    try {
      const params = { page: 1, page_size: 100 };
      if (filterClass) params.class_id = filterClass;

      const [docRes, classRes] = await Promise.all([
        documentsApi.list(null, params.page, params.page_size, filterClass || undefined),
        classesApi.list(),
      ]);
      setDocs(docRes.data);

      // Lấy danh sách lớp liên quan đến user
      if (user?.user_id) {
        let filtered = [];
        if (isTeacher) {
          filtered = classRes.data.filter((c) =>
            c.teachers?.some((t) => t.teacher_id === user.user_id || t.user_id === user.user_id)
          );
        } else if (isStudent) {
          filtered = classRes.data.filter((c) =>
            c.students?.some((s) => s.student_id === user.user_id || s.user_id === user.user_id)
          );
        }
        setMyClasses(filtered.length > 0 ? filtered : classRes.data);
      }
    } catch {
      setError("Không thể tải tài liệu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, [filterClass]);

  const handleDelete = async (docId) => {
    if (!confirm("Xóa tài liệu này?")) return;
    try {
      await documentsApi.delete(docId);
      loadAll();
    } catch {
      alert("Xóa thất bại");
    }
  };

  const filtered = docs.filter((d) =>
    !search || d.document_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">📁 Tài liệu học tập</h2>
          <p className="page-subtitle">{filtered.length} tài liệu</p>
        </div>
        {(isTeacher || isAdmin) && (
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            ➕ Đăng tài liệu
          </button>
        )}
      </div>

      {/* Thanh lọc */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <input
          className="form-input"
          style={{ flex: 1, minWidth: 200 }}
          placeholder="🔍 Tìm tài liệu..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="form-input"
          style={{ minWidth: 240 }}
          value={filterClass}
          onChange={(e) => setFilterClass(e.target.value)}
        >
          <option value="">📚 Tất cả lớp học</option>
          {myClasses.map((c) => (
            <option key={c.class_id} value={c.class_id}>
              {c.course_id} · {c.class_id}
            </option>
          ))}
        </select>
        {filterClass && (
          <button className="btn btn-secondary btn-sm" onClick={() => setFilterClass("")}>
            ✕ Xóa lọc
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📁</div>
          <h3>Chưa có tài liệu nào</h3>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
          {filtered.map((doc) => (
            <div key={doc.document_id} className="card" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {/* Icon + tên */}
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{
                  width: 42, height: 42, borderRadius: 10,
                  background: "var(--bg-card-hover)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22, flexShrink: 0
                }}>📄</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: 14,
                    whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {doc.document_name}
                  </div>
                  {/* Mã môn + lớp */}
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2, display: "flex", gap: 8 }}>
                    {doc.course_id && (
                      <span className="badge badge-muted" style={{ fontSize: 11 }}>{doc.course_id}</span>
                    )}
                    {doc.class_id && (
                      <span className="badge badge-muted" style={{ fontSize: 11 }}>{doc.class_id}</span>
                    )}
                    {!doc.course_id && !doc.class_id && (
                      <span>ID: {doc.document_id} · GV: {doc.teacher_id || "—"}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* GV / deadline */}
              {(doc.teacher_id || doc.deadline) && (
                <div style={{ fontSize: 12, color: "var(--text-muted)", display: "flex", gap: 12 }}>
                  {doc.teacher_id && <span>GV: <strong>{doc.teacher_id}</strong></span>}
                  {doc.deadline && (
                    <span>Hạn: {new Date(doc.deadline).toLocaleDateString("vi-VN")}</span>
                  )}
                </div>
              )}

              {/* Actions */}
              <div style={{ display: "flex", gap: 8, marginTop: "auto" }}>
                {doc.link_url ? (
                  <a href={doc.link_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                    🔗 Mở tài liệu
                  </a>
                ) : (
                  <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Không có link</span>
                )}
                {(isTeacher || isAdmin) && (
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(doc.document_id)}>
                    🗑 Xóa
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateDocModal
          onClose={() => setShowCreate(false)}
          onCreated={loadAll}
          myClasses={myClasses}
        />
      )}
    </div>
  );
}
