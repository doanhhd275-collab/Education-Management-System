/**
 * Trang đăng nhập
 *
 * Sau khi login thành công, dùng window.location.replace('/dashboard')
 * thay vì React navigate() để tránh race condition hoàn toàn.
 * Full page reload → AuthContext đọc lại từ localStorage ngay từ đầu.
 */
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../api";
import apiClient from "../../api/client";

export default function LoginPage() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Bước 1: Xóa token cũ (nếu có) trước khi login mới
      localStorage.removeItem("ems_token");
      localStorage.removeItem("ems_user");

      // Bước 2: Đăng nhập → lấy token
      const loginRes = await authApi.login(email, password);
      const token    = loginRes.data.access_token;

      // Bước 3: Lưu token vào localStorage VÀ set vào axios header
      localStorage.setItem("ems_token", token);
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      // Bước 4: Lấy thông tin user đầy đủ
      let user = { email, name: email, user_id: "", user_roles: [] };
      try {
        const meRes = await authApi.getMe();
        user = meRes.data;
      } catch (meErr) {
        console.warn("Lỗi /auth/me (dùng user tối giản):", meErr.message);
      }

      // Bước 5: Lưu vào localStorage
      localStorage.setItem("ems_user", JSON.stringify(user));

      // Bước 6: Chuyển hướng bằng window.location (full reload)
      // → tránh hoàn toàn race condition React state vs navigate()
      window.location.replace("/dashboard");

    } catch (err) {
      console.error("Login error:", err.response?.status, err.message);
      const status = err.response?.status;
      if (status === 401 || status === 422) {
        setError("Email hoặc mật khẩu không đúng.");
      } else if (!err.response) {
        setError("Không kết nối được server. Kiểm tra backend có đang chạy không.");
      } else {
        setError(err.response?.data?.detail || "Đăng nhập thất bại. Vui lòng thử lại.");
      }
      setLoading(false);
    }
    // Không setLoading(false) khi thành công vì page sẽ reload
  };

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon">🎓</div>
          <h1>Hệ Thống Quản Lý Đào Tạo</h1>
          <p>Đăng nhập để tiếp tục</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="alert alert-error">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="example@ems.edu.vn"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Mật khẩu</label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg w-full"
            disabled={loading}
            style={{ marginTop: "8px" }}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: 16, height: 16 }} />
                Đang đăng nhập...
              </>
            ) : "Đăng nhập"}
          </button>
        </form>

        {/* Gợi ý tài khoản test */}
        <div style={{
          marginTop: "24px",
          padding: "16px",
          background: "var(--bg-tertiary)",
          borderRadius: "var(--radius)",
          fontSize: "12px",
        }}>
          <div style={{ color: "var(--text-muted)", marginBottom: "8px", fontWeight: 600 }}>
            🔑 Tài khoản test (click để điền):
          </div>
          {[
            { role: "Admin",     email: "admin@ems.edu.vn"    },
            { role: "Giáo viên", email: "teacher1@ems.edu.vn" },
            { role: "Sinh viên", email: "student1@ems.edu.vn"  },
          ].map((acc) => (
            <div
              key={acc.email}
              style={{ color: "var(--text-secondary)", marginBottom: "4px", cursor: "pointer" }}
              onClick={() => { setEmail(acc.email); setPassword("Admin@123"); }}
            >
              <span className="badge badge-primary" style={{ marginRight: 6 }}>{acc.role}</span>
              {acc.email}
            </div>
          ))}
          <div style={{ color: "var(--text-muted)", marginTop: "6px" }}>
            Mật khẩu: <strong style={{ color: "var(--accent)" }}>Admin@123</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
