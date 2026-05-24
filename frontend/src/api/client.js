/**
 * Axios HTTP Client
 * Cấu hình tập trung cho tất cả API calls đến backend
 *
 * Cách hoạt động:
 * 1. Mọi request đều tự động thêm Authorization header (nếu có token)
 * 2. Nếu nhận 401 (hết hạn token), tự động chuyển về trang login
 */
import axios from "axios";

// Đọc từ biến môi trường VITE_API_URL:
//   - Local dev : "/api/v1"  → Vite proxy forward đến http://localhost:8000
//   - Vercel    : "https://<your-backend>.onrender.com/api/v1"
// Tạo file frontend/.env.local (không commit) để override khi dev.
const BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

// Tạo axios instance với config mặc định
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 giây timeout
});

// ── Request Interceptor ──────────────────────────────────────
// Chạy TRƯỚC mỗi request: tự động thêm token vào header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("ems_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor ─────────────────────────────────────
// Chạy SAU mỗi response: xử lý lỗi tập trung
apiClient.interceptors.response.use(
  (response) => response, // Thành công: trả về nguyên
  (error) => {
    if (error.response?.status === 401) {
      // Token hết hạn — nhưng KHÔNG redirect nếu đang ở trang login
      // (tránh loop: login → 401 từ /auth/me → redirect /login → loop)
      const isLoginPage = window.location.pathname === "/login";
      const isLoginRequest = error.config?.url?.includes("/auth/login");

      if (!isLoginPage && !isLoginRequest) {
        localStorage.removeItem("ems_token");
        localStorage.removeItem("ems_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
