/**
 * Trang Bài tập
 * - Teacher/Admin: tạo bài tập, xem bài nộp, chấm điểm
 * - Student: xem bài tập (filter theo lớp), nộp bài, xem điểm của mình
 */
import { useState, useEffect } from "react";
import { assignmentsApi, classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

/* ─── Modal xem & chấm điểm bài nộp (Teacher/Admin) ────────────── */
function ViewReportsModal({ assignment, onClose }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");
  const [grading, setGrading] = useState({}); // { student_id: {grade, feedback} }
  const [saving, setSaving]   = useState({});

  const loadReports = () => {
    setLoading(true);
    assignmentsApi.getReports(assignment.assignment_id)
      .then((r) => {
        setReports(r.data);
        // khởi tạo form chấm điểm với giá trị hiện tại
        const init = {};
        r.data.forEach((rp) => {
          init[rp.student_id] = { grade: rp.grade ?? "", feedback: rp.feedback ?? "" };
        });
        setGrading(init);
      })
      .catch(() => setError("Không thể tải danh sách bài nộp"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadReports(); }, [assignment.assignment_id]);

  const handleGrade = async (studentId) => {
    setSaving((s) => ({ ...s, [studentId]: true }));
    try {
      await assignmentsApi.gradeSubmission(
        assignment.assignment_id,
        studentId,
        grading[studentId]
      );
      loadReports();
    } catch {
      alert("Chấm điểm thất bại");
    } finally {
      setSaving((s) => ({ ...s, [studentId]: false }));
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 800 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📋 Bài nộp — {assignment.assignment_name}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          {loading ? (
            <div style={{ textAlign: "center", padding: 24, color: "var(--text-muted)" }}>Đang tải...</div>
          ) : reports.length === 0 ? (
            <div style={{ textAlign: "center", padding: 24, color: "var(--text-muted)" }}>
              <div style={{ fontSize: 36, marginBottom: 8 }}>📭</div>
              Chưa có sinh viên nào nộp bài
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Sinh viên</th>
                  <th>Họ tên</th>
                  <th>Ngày nộp</th>
                  <th>Link bài nộp</th>
                  <th style={{ width: 90 }}>Điểm</th>
                  <th>Nhận xét</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.student_id}>
                    <td><span className="badge badge-muted">{r.student_id}</span></td>
                    <td style={{ fontWeight: 500 }}>{r.student_name || "—"}</td>
                    <td style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                      {r.submit_date ? new Date(r.submit_date).toLocaleString("vi-VN") : "—"}
                    </td>
                    <td>
                      {r.link_url ? (
                        <a href={r.link_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                          🔗 Xem bài
                        </a>
                      ) : <span style={{ color: "var(--text-muted)", fontSize: 12 }}>Chưa nộp</span>}
                    </td>
                    <td>
                      <input
                        type="number"
                        min={0} max={10} step={0.5}
                        className="form-input"
                        style={{ width: 70, padding: "4px 6px", fontSize: 13 }}
                        placeholder="0-10"
                        value={grading[r.student_id]?.grade ?? ""}
                        onChange={(e) => setGrading((g) => ({
                          ...g,
                          [r.student_id]: { ...g[r.student_id], grade: e.target.value }
                        }))}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-input"
                        style={{ fontSize: 13, padding: "4px 6px" }}
                        placeholder="Nhận xét..."
                        value={grading[r.student_id]?.feedback ?? ""}
                        onChange={(e) => setGrading((g) => ({
                          ...g,
                          [r.student_id]: { ...g[r.student_id], feedback: e.target.value }
                        }))}
                      />
                    </td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        disabled={saving[r.student_id]}
                        onClick={() => handleGrade(r.student_id)}
                      >
                        {saving[r.student_id] ? "..." : "💾 Lưu"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div style={{ marginTop: 12, fontSize: 13, color: "var(--text-muted)" }}>
            Tổng: <strong>{reports.length}</strong> bài nộp
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Đóng</button>
        </div>
      </div>
    </div>
  );
}

/* ─── Modal nộp bài (Student) ──────────────────────────────────── */
function SubmitModal({ assignment, studentId, onClose, onSubmitted }) {
  const [linkUrl, setLinkUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!linkUrl.trim()) { setError("Vui lòng nhập link bài làm"); return; }
    setLoading(true);
    setError("");
    try {
      await assignmentsApi.submit(assignment.assignment_id, {
        assignment_id: assignment.assignment_id,
        student_id: studentId,
        class_id: assignment.class_id || "",
        link_url: linkUrl.trim(),
      });
      onSubmitted();
      onClose();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail)
        ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
        : (typeof detail === "string" ? detail : "Nộp bài thất bại"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📤 Nộp bài tập</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">⚠️ {error}</div>}
          <p style={{ color: "var(--text-secondary)", marginBottom: 16, fontSize: 13 }}>
            Bài tập: <strong>{assignment.assignment_name}</strong>
            <span style={{ marginLeft: 12, color: "var(--text-muted)" }}>
              Môn: {assignment.course_id} · Lớp: {assignment.class_id}
            </span>
          </p>
          <form id="submit-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Link bài nộp *</label>
              <input
                className="form-input"
                type="url"
                placeholder="https://drive.google.com/... hoặc link bài làm của bạn"
                value={linkUrl}
                onChange={(e) => setLinkUrl(e.target.value)}
                required
              />
              <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                💡 Nhập link Google Drive, GitHub, Classroom... để giáo viên dễ chấm bài
              </p>
            </div>
          </form>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Hủy</button>
          <button className="btn btn-success" form="submit-form" type="submit" disabled={loading}>
            {loading ? "Đang nộp..." : "📤 Xác nhận nộp bài"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Modal tạo bài tập (Teacher) ────────────────────────────── */
function CreateAssignmentModal({ onClose, onCreated, myClasses }) {
  const [form, setForm] = useState({
    assignment_id: "", assignment_name: "",
    class_id: "", course_id: "", link_url: "", deadline: "",
  });
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handleClassChange = (e) => {
    const sel = myClasses.find((c) => c.class_id === e.target.value);
    setForm((f) => ({
      ...f,
      class_id: e.target.value,
      course_id: sel ? sel.course_id : f.course_id,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await assignmentsApi.create({
        assignment_id: form.assignment_id,
        assignment_name: form.assignment_name,
        class_id: form.class_id,
        course_id: form.course_id,
        link_url: form.link_url || undefined,
        deadline: form.deadline || undefined,
      });
      onCreated(); onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Tạo bài tập thất bại");
    } finally {
      setLoading(false);
    }
  };

  const f = (field) => ({ value: form[field], onChange: (e) => setForm({ ...form, [field]: e.target.value }) });

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
              <input className="form-input" placeholder="VD: ASS001" required maxLength={10} {...f("assignment_id")} />
            </div>
            <div className="form-group">
              <label className="form-label">Tên bài tập *</label>
              <input className="form-input" placeholder="VD: Bài tập lập trình tuần 1" required {...f("assignment_name")} />
            </div>
            <div className="form-group">
              <label className="form-label">Lớp học *</label>
              {myClasses.length > 0 ? (
                <select className="form-input" required value={form.class_id} onChange={handleClassChange}>
                  <option value="">-- Chọn lớp --</option>
                  {myClasses.map((c) => (
                    <option key={c.class_id} value={c.class_id}>
                      {c.course_id} · {c.class_id}
                    </option>
                  ))}
                </select>
              ) : (
                <input className="form-input" placeholder="VD: CS101-01" required maxLength={10} {...f("class_id")} />
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Mã môn *</label>
              <input className="form-input" placeholder="VD: CS101" required maxLength={10} {...f("course_id")} />
            </div>
            <div className="form-group">
              <label className="form-label">Link đề bài</label>
              <input className="form-input" type="url" placeholder="https://classroom.google.com/..." {...f("link_url")} />
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

/* ─── Main Page ───────────────────────────────────────────────── */
export default function AssignmentsPage() {
  const { isTeacher, isAdmin, isStudent, user } = useAuth();
  const [assignments,  setAssignments]  = useState([]);
  const [myClasses,    setMyClasses]    = useState([]); // lớp của GV hoặc SV
  const [mySubmissions, setMySubmissions] = useState({}); // { assignment_id: report }
  const [filterClass,  setFilterClass]  = useState("");
  const [loading,      setLoading]      = useState(true);
  const [showCreate,   setShowCreate]   = useState(false);
  const [submitTarget, setSubmitTarget] = useState(null);
  const [viewReportsTarget, setViewReportsTarget] = useState(null);
  const [error, setError] = useState("");

  const loadAll = async () => {
    setLoading(true);
    try {
      const params = filterClass ? { class_id: filterClass } : {};
      const [assRes, classRes] = await Promise.all([
        assignmentsApi.list(params),
        classesApi.list(),
      ]);
      setAssignments(assRes.data);

      // Lớp GV phụ trách hoặc SV đăng ký
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

      // Sinh viên: load bài nộp của mình
      if (isStudent) {
        try {
          const subRes = await assignmentsApi.getMySubmissions();
          const subMap = {};
          subRes.data.forEach((s) => { subMap[s.assignment_id] = s; });
          setMySubmissions(subMap);
        } catch { /* ignore */ }
      }
    } catch {
      setError("Không thể tải dữ liệu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, [filterClass]);

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

      {/* Bộ lọc theo lớp */}
      <div style={{ marginBottom: 20, display: "flex", gap: 12, alignItems: "center" }}>
        <select
          className="form-input"
          style={{ maxWidth: 300 }}
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
      ) : assignments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📌</div>
          <h3>Chưa có bài tập nào</h3>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {assignments.map((a) => {
            const mySub = mySubmissions[a.assignment_id];
            return (
              <div key={a.assignment_id} className="card">
                {/* Header */}
                <div className="flex-between" style={{ marginBottom: 8 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span className="badge badge-primary">{a.assignment_id}</span>
                    <strong style={{ color: "var(--text-primary)" }}>{a.assignment_name}</strong>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    {a.deadline && (
                      <span className={`badge ${isOverdue(a.deadline) ? "badge-danger" : "badge-warning"}`}>
                        {isOverdue(a.deadline) ? "⚠️ Quá hạn" : "⏰"}{" "}
                        {new Date(a.deadline).toLocaleDateString("vi-VN")}
                      </span>
                    )}
                    {/* Hiển thị điểm SV */}
                    {isStudent && mySub?.grade != null && (
                      <span className="badge badge-success" title={mySub.feedback || ""}>
                        ✅ Điểm: {mySub.grade}/10
                      </span>
                    )}
                    {isStudent && mySub && mySub.grade == null && (
                      <span className="badge badge-muted">📤 Đã nộp · Chờ chấm</span>
                    )}
                  </div>
                </div>

                {/* Môn / Lớp */}
                <div style={{ fontSize: 12, color: "var(--text-muted)", display: "flex", gap: 16, marginBottom: 12 }}>
                  <span>Môn: <strong>{a.course_id}</strong></span>
                  <span>Lớp: <strong>{a.class_id}</strong></span>
                  {isStudent && mySub?.feedback && (
                    <span style={{ color: "var(--color-primary)", fontStyle: "italic" }}>
                      💬 {mySub.feedback}
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {a.link_url ? (
                    <a href={a.link_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                      🔗 Xem đề bài
                    </a>
                  ) : (
                    <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Chưa có link đề bài</span>
                  )}

                  {isStudent && (
                    <button
                      className={`btn btn-sm ${mySub ? "btn-warning" : "btn-success"}`}
                      onClick={() => setSubmitTarget(a)}
                      disabled={isOverdue(a.deadline) && !mySub}
                      title={isOverdue(a.deadline) ? "Đã quá hạn nộp bài" : (mySub ? "Nộp lại" : "Nộp bài")}
                    >
                      {mySub ? "🔄 Nộp lại" : "📤 Nộp bài"}
                    </button>
                  )}

                  {(isTeacher || isAdmin) && (
                    <button className="btn btn-secondary btn-sm" onClick={() => setViewReportsTarget(a)}>
                      📄 Xem bài nộp
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showCreate && (
        <CreateAssignmentModal
          onClose={() => setShowCreate(false)}
          onCreated={loadAll}
          myClasses={myClasses}
        />
      )}
      {submitTarget && (
        <SubmitModal
          assignment={submitTarget}
          studentId={user.user_id}
          onClose={() => setSubmitTarget(null)}
          onSubmitted={loadAll}
        />
      )}
      {viewReportsTarget && (
        <ViewReportsModal
          assignment={viewReportsTarget}
          onClose={() => setViewReportsTarget(null)}
        />
      )}
    </div>
  );
}
