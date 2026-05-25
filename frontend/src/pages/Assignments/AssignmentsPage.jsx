/**
 * Trang Bài tập
 * - Teacher/Admin: tạo bài tập (với link), xem bài nộp
 * - Student: xem bài tập, mở link, nộp bài
 */
import { useState, useEffect } from "react";
import { assignmentsApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

function CreateAssignmentModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    assignment_id: "",
    assignment_name: "",
    class_id: "",
    course_id: "",
    link_url: "",
    deadline: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await assignmentsApi.create({
        assignment_id: form.assignment_id,
        assignment_name: form.assignment_name,
        class_id: form.class_id,
        course_id: form.course_id,
        link_url: form.link_url || undefined,
        deadline: form.deadline || undefined,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Tạo bài tập thất bại");
    } finally {
      setLoading(false);
    }
  };

  const f = (field) => ({
    value: form[field],
    onChange: (e) => setForm({ ...form, [field]: e.target.value }),
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📌 Tạo bài tập mới</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <form id="assign-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Mã bài tập *</label>
              <input
                className="form-input"
                placeholder="VD: ASS001"
                required
                maxLength={10}
                {...f("assignment_id")}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Tên bài tập *</label>
              <input
                className="form-input"
                placeholder="VD: Bài tập lập trình tuần 1"
                required
                {...f("assignment_name")}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Mã môn *</label>
              <input
                className="form-input"
                placeholder="VD: CS101"
                required
                maxLength={10}
                {...f("course_id")}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Mã lớp *</label>
              <input
                className="form-input"
                placeholder="VD: CS101-01"
                required
                maxLength={10}
                {...f("class_id")}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Link bài tập</label>
              <input
                className="form-input"
                type="url"
                placeholder="https://classroom.google.com/..."
                {...f("link_url")}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Deadline</label>
              <input className="form-input" type="datetime-local" {...f("deadline")} />
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-primary" form="assign-form" type="submit" disabled={loading}>
            {loading ? "Đang tạo..." : "Tạo bài tập"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AssignmentsPage() {
  const { isTeacher, isAdmin, isStudent, user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [error, setError] = useState("");

  const loadAssignments = async () => {
    setLoading(true);
    try {
      const res = await assignmentsApi.list();
      setAssignments(res.data);
    } catch {
      setError("Không thể tải danh sách bài tập");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAssignments(); }, []);

  const handleSubmit = async (assignmentId) => {
    if (!window.confirm("Nộp bài tập này?")) return;
    const assignment = assignments.find((a) => a.assignment_id === assignmentId);
    try {
      await assignmentsApi.submit(assignmentId, {
        assignment_id: assignmentId,
        student_id: user.user_id,
        class_id: assignment?.class_id || "",
      });
      alert("Nộp bài thành công!");
    } catch (err) {
      alert(err.response?.data?.detail || "Nộp bài thất bại");
    }
  };

  const isOverdue = (deadline) => deadline && new Date(deadline) < new Date();

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">📌 Bài tập</h2>
          <p className="page-subtitle">{assignments.length} bài tập</p>
        </div>
        {(isTeacher || isAdmin) && (
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            ➕ Tạo bài tập
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : assignments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📌</div>
          <h3>Chưa có bài tập nào</h3>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {assignments.map((a) => (
            <div key={a.assignment_id} className="card">
              {/* Header: tên + deadline */}
              <div className="flex-between" style={{ marginBottom: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span className="badge badge-primary">{a.assignment_id}</span>
                  <strong style={{ color: "var(--text-primary)" }}>{a.assignment_name}</strong>
                </div>
                {a.deadline && (
                  <span className={`badge ${isOverdue(a.deadline) ? "badge-danger" : "badge-warning"}`}>
                    {isOverdue(a.deadline) ? "⚠️ Quá hạn" : "⏰"}{" "}
                    {new Date(a.deadline).toLocaleDateString("vi-VN")}
                  </span>
                )}
              </div>

              {/* Thông tin môn / lớp */}
              <div style={{ fontSize: 12, color: "var(--text-muted)", display: "flex", gap: 16, marginBottom: 12 }}>
                <span>Môn: <strong>{a.course_id}</strong></span>
                <span>Lớp: <strong>{a.class_id}</strong></span>
              </div>

              {/* Hành động */}
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                {/* Link bài tập */}
                {a.link_url ? (
                  <a
                    href={a.link_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary btn-sm"
                  >
                    🔗 Xem đề bài
                  </a>
                ) : (
                  <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Chưa có link đề bài</span>
                )}

                {/* Nộp bài (chỉ Student) */}
                {isStudent && (
                  <button
                    className="btn btn-success btn-sm"
                    onClick={() => handleSubmit(a.assignment_id)}
                    disabled={isOverdue(a.deadline)}
                    title={isOverdue(a.deadline) ? "Đã quá hạn nộp bài" : ""}
                  >
                    📤 Nộp bài
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateAssignmentModal onClose={() => setShowCreate(false)} onCreated={loadAssignments} />
      )}
    </div>
  );
}
