/**
 * Trang Quản lý giáo viên
 */
import { useState, useEffect } from "react";
import { teachersApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function TeachersPage() {
  const { isAdmin } = useAuth();
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const loadTeachers = async () => {
    try {
      const res = await teachersApi.list();
      setTeachers(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTeachers(); }, []);

  const filtered = teachers.filter(
    (t) =>
      t.user?.name?.toLowerCase().includes(search.toLowerCase()) ||
      t.teacher_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">👨‍🏫 Quản lý giáo viên</h2>
          <p className="page-subtitle">Tổng cộng: {teachers.length} giáo viên</p>
        </div>
      </div>

      <div className="search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input className="form-input" placeholder="Tìm theo tên, mã GV..."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="spinner" /> Đang tải...</div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Mã GV</th>
                  <th>Họ tên</th>
                  <th>Email</th>
                  <th>Điện thoại</th>
                  {isAdmin && <th>Hành động</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr key={t.teacher_id}>
                    <td><span className="badge badge-primary">{t.teacher_id}</span></td>
                    <td style={{ fontWeight: 500 }}>{t.user?.name || "—"}</td>
                    <td style={{ color: "var(--text-secondary)" }}>{t.user?.email}</td>
                    <td>{t.user?.contact || "—"}</td>
                    {isAdmin && (
                      <td>
                        <button className="btn btn-secondary btn-sm">Xem chi tiết</button>
                      </td>
                    )}
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
