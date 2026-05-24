/**
 * Trang Nhật ký hệ thống (Chỉ Admin)
 */
import { useState, useEffect } from "react";
import { logsApi } from "../../api";
import { useAuth } from "../../context/AuthContext";
import { Navigate } from "react-router-dom";

export default function LogsPage() {
  const { isAdmin } = useAuth();
  const [reportLogs, setReportLogs] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("report"); // 'report' or 'system'

  if (!isAdmin) return <Navigate to="/dashboard" />;

  useEffect(() => {
    const loadLogs = async () => {
      setLoading(true);
      try {
        if (tab === "report") {
          const res = await logsApi.getReportLogs();
          setReportLogs(res.data);
        } else {
          const res = await logsApi.getSystemLogs();
          setSystemLogs(res.data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadLogs();
  }, [tab]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">📋 Nhật ký hệ thống</h2>
          <p className="page-subtitle">Giám sát hoạt động và lỗi</p>
        </div>
        <div className="flex gap-8">
          <button className={`btn ${tab === "report" ? "btn-primary" : "btn-secondary"}`} 
            onClick={() => setTab("report")}>Lịch sử hoạt động</button>
          <button className={`btn ${tab === "system" ? "btn-primary" : "btn-secondary"}`} 
            onClick={() => setTab("system")}>System Logs</button>
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
                  {tab === "system" && <th>Mã Log</th>}
                  {tab === "system" && <th>Action / Level</th>}
                  <th>Người dùng</th>
                  <th>Nội dung</th>
                  <th>Thời gian</th>
                  {tab === "system" && <th>IP</th>}
                </tr>
              </thead>
              <tbody>
                {(tab === "report" ? reportLogs : systemLogs).map((log, i) => (
                  <tr key={i}>
                    {tab === "system" && <td><span className="badge badge-muted">{log.log_id}</span></td>}
                    {tab === "system" && (
                      <td>
                        <span className={`badge ${log.action === "ERROR" ? "badge-danger" : log.action === "WARN" ? "badge-warning" : "badge-info"}`}>
                          {log.action}
                        </span>
                      </td>
                    )}
                    <td><span className="badge badge-primary">{log.user_id}</span></td>
                    <td style={{ color: "var(--text-secondary)" }}>{log.content || log.action_details}</td>
                    <td style={{ color: "var(--text-muted)", fontSize: 12 }}>
                      {new Date(log.time_log).toLocaleString("vi-VN")}
                    </td>
                    {tab === "system" && <td>{log.ip || "—"}</td>}
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
