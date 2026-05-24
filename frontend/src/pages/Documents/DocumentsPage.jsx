/**
 * Trang Tài liệu học tập
 */
import { useState, useEffect } from "react";
import { documentsApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

function CreateDocModal({ teacherId, onClose, onCreated }) {
  const [form, setForm] = useState({ document_id: "", document_name: "", teacher_id: teacherId || "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await documentsApi.create(form);
      onCreated(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Tạo tài liệu thất bại");
    } finally { setLoading(false); }
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
              <input className="form-input" placeholder="VD: DOC010" required
                value={form.document_id} onChange={(e) => setForm({...form, document_id: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Tên tài liệu *</label>
              <input className="form-input" placeholder="VD: Slide bài giảng Tuần 1" required
                value={form.document_name} onChange={(e) => setForm({...form, document_name: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Mã giáo viên *</label>
              <input className="form-input" placeholder="VD: T001" required
                value={form.teacher_id} onChange={(e) => setForm({...form, teacher_id: e.target.value})} />
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

export default function DocumentsPage() {
  const { isTeacher, isAdmin, user } = useAuth();
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const loadDocs = async () => {
    setLoading(true);
    try {
      const res = await documentsApi.list(null, 1, 100);
      setDocs(res.data);
    } catch { setError("Không thể tải tài liệu"); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadDocs(); }, []);

  const handleDelete = async (docId) => {
    if (!window.confirm("Xóa tài liệu này?")) return;
    try {
      await documentsApi.delete(docId);
      setDocs((prev) => prev.filter((d) => d.document_id !== docId));
    } catch (err) { setError(err.response?.data?.detail || "Xóa thất bại"); }
  };

  const filtered = docs.filter((d) =>
    d.document_name?.toLowerCase().includes(search.toLowerCase()) ||
    d.teacher_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">📄 Tài liệu học tập</h2>
          <p className="page-subtitle">{docs.length} tài liệu</p>
        </div>
        {(isTeacher || isAdmin) && (
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            ➕ Đăng tài liệu
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input className="form-input" placeholder="Tìm tài liệu..."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📄</div>
          <h3>Chưa có tài liệu nào</h3>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
          {filtered.map((doc) => (
            <div key={doc.document_id} className="card" style={{ position: "relative" }}>
              <div style={{ fontSize: 32, marginBottom: 10 }}>📄</div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
                {doc.document_name}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                ID: <span className="badge badge-muted">{doc.document_id}</span>
                {" · "}Giáo viên: <span className="badge badge-primary">{doc.teacher_id}</span>
              </div>
              {(isTeacher || isAdmin) && (
                <button className="btn btn-danger btn-sm" style={{ marginTop: 12 }}
                  onClick={() => handleDelete(doc.document_id)}>
                  🗑️ Xóa
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateDocModal onClose={() => setShowCreate(false)} onCreated={loadDocs} />
      )}
    </div>
  );
}
