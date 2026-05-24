/**
 * AuthContext - Quản lý trạng thái đăng nhập toàn app
 *
 * Fix race condition: Dùng loading state để ProtectedRoute
 * không redirect trước khi AuthProvider đọc xong localStorage.
 */
import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [token,   setToken]   = useState(null);
  const [loading, setLoading] = useState(true); // ← Chờ khởi tạo xong

  // Khởi tạo từ localStorage khi app load lần đầu (async với useEffect)
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("ems_token");
      const savedUser  = localStorage.getItem("ems_user");

      if (savedToken) {
        setToken(savedToken);
        if (savedUser) {
          setUser(JSON.parse(savedUser));
        }
      }
    } catch {
      // Dữ liệu localStorage bị hỏng → xóa đi
      localStorage.removeItem("ems_token");
      localStorage.removeItem("ems_user");
    } finally {
      setLoading(false); // ← Đã xong, ProtectedRoute có thể kiểm tra
    }
  }, []);

  // Lấy role_id từ user_roles (ADMIN / TEACHER / STUDENT)
  const roles = user?.user_roles?.map((ur) => ur.role_id).filter(Boolean) || [];

  /**
   * Đăng nhập: lưu token và thông tin user
   */
  const login = (newToken, newUser) => {
    localStorage.setItem("ems_token", newToken);
    localStorage.setItem("ems_user", JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  /**
   * Đăng xuất: xóa tất cả dữ liệu đăng nhập
   */
  const logout = () => {
    localStorage.removeItem("ems_token");
    localStorage.removeItem("ems_user");
    setToken(null);
    setUser(null);
    window.location.href = "/login";
  };

  /**
   * Kiểm tra user có role cụ thể không
   */
  const hasRole = (role) => roles.includes(role);

  const isAdmin   = hasRole("ADMIN");
  const isTeacher = hasRole("TEACHER");
  const isStudent = hasRole("STUDENT");

  const value = {
    user,
    token,
    roles,
    loading,       // ← Expose để ProtectedRoute dùng
    login,
    logout,
    hasRole,
    isAdmin,
    isTeacher,
    isStudent,
    isLoggedIn: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth phải được dùng bên trong <AuthProvider>");
  }
  return context;
}
