/**
 * Layout - Bố cục chính của app (Sidebar + Topbar + Content)
 */
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";

// Map path → tên trang hiển thị trên Topbar
const PAGE_TITLES = {
  "/dashboard":  "Tổng quan",
  "/profile":    "Hồ sơ cá nhân",
  "/users":      "Quản lý người dùng",
  "/students":   "Quản lý sinh viên",
  "/teachers":   "Quản lý giáo viên",
  "/curriculum": "Chương trình đào tạo",
  "/courses":    "Quản lý môn học",
  "/classes":    "Quản lý lớp học",
  "/enrollments":"Đăng ký học tập",
  "/grading":    "Nhập điểm",
  "/attendance": "Điểm danh",
  "/documents":  "Tài liệu học tập",
  "/assignments":"Bài tập",
  "/logs":       "Nhật ký hệ thống",
};

export default function Layout() {
  const location = useLocation();

  // Tìm tên trang từ path hiện tại
  const pageTitle = Object.entries(PAGE_TITLES).find(([path]) =>
    location.pathname.startsWith(path)
  )?.[1] || "EMS";

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <h1 className="topbar-title">{pageTitle}</h1>
          <div className="topbar-actions">
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Hệ Thống Quản Lý Đào Tạo
            </span>
          </div>
        </header>

        {/* Page content - Outlet render page component tương ứng */}
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
