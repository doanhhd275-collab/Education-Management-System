/**
 * ProtectedRoute - Bảo vệ route cần đăng nhập / cần role
 *
 * Đợi AuthContext loading xong mới quyết định redirect hay không.
 * Tránh race condition: ProtectedRoute không redirect khi chưa biết
 * trạng thái đăng nhập (loading = true).
 */
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, roles = [] }) {
  const { isLoggedIn, hasRole, loading } = useAuth();

  // ← Quan trọng: chờ AuthContext đọc xong localStorage
  if (loading) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--bg-primary)",
        gap: "12px",
        color: "var(--text-muted)",
        fontSize: "14px",
      }}>
        <div style={{
          width: "24px", height: "24px",
          border: "2px solid var(--border-light)",
          borderTopColor: "var(--accent)",
          borderRadius: "50%",
          animation: "spin 0.7s linear infinite",
        }} />
        Đang tải...
      </div>
    );
  }

  // Chưa đăng nhập → về login
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  // Kiểm tra role nếu route yêu cầu
  if (roles.length > 0 && !roles.some((r) => hasRole(r))) {
    return (
      <div style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center", color: "var(--text-muted)" }}>
          <div style={{ fontSize: "40px", marginBottom: "12px" }}>🚫</div>
          <h3 style={{ fontSize: "16px", color: "var(--text-secondary)", marginBottom: "6px" }}>
            Không có quyền truy cập
          </h3>
          <p style={{ fontSize: "13px" }}>Bạn không có quyền xem trang này.</p>
        </div>
      </div>
    );
  }

  return children;
}
