/**
 * Trang Quản lý sinh viên
 */
import { useState, useEffect } from "react";
import { studentsApi } from "../../api";

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState("");
  const [error, setError]       = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await studentsApi.list(null, 1, 100);
        setStudents(res.data);
      } catch {
        setError("Không thể tải danh sách sinh viên");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = students.filter(
    (s) =>
      s.user?.name?.toLowerCase().includes(search.toLowerCase()) ||
      s.user_id?.toLowerCase().includes(search.toLowerCase()) ||
      s.program_id?.toLowerCase().includes(search.toLowerCase())
  );

  const getWarningBadge = (level) => {
    if (level === 0) return <span className="badge badge-success">Bình thường</span>;
    if (level === 1) return <span className="badge badge-warning">Cảnh báo 1</span>;
    return <span className="badge badge-danger">Cảnh báo {level}</span>;
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">🎓 Quản lý sinh viên</h2>
          <p className="page-subtitle">Tổng cộng: {students.length} sinh viên</p>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            className="form-input"
            placeholder="Tìm theo tên, mã SV, chương trình..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🎓</div>
          <h3>Không tìm thấy sinh viên</h3>
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã SV</th>
                  <th>Họ tên</th>
                  <th>Chương trình</th>
                  <th>GPA</th>
                  <th>CPA</th>
                  <th>Cảnh báo</th>
                  <th>Tốt nghiệp</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => (
                  <tr key={s.user_id}>
                    <td><span className="badge badge-muted">{s.user_id}</span></td>
                    <td style={{ fontWeight: 500 }}>{s.user?.name || "—"}</td>
                    <td style={{ color: "var(--text-secondary)" }}>{s.program_id}</td>
                    <td>
                      {s.gpa != null ? (
                        <span style={{ color: s.gpa >= 3 ? "var(--success)" : s.gpa >= 2 ? "var(--warning)" : "var(--danger)", fontWeight: 600 }}>
                          {s.gpa.toFixed(1)}
                        </span>
                      ) : "—"}
                    </td>
                    <td>{s.cpa?.toFixed(1) ?? "—"}</td>
                    <td>{getWarningBadge(s.warning_level ?? 0)}</td>
                    <td>
                      {s.graduation_condition
                        ? <span className="badge badge-success">✓ Đủ điều kiện</span>
                        : <span className="badge badge-muted">Chưa</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
