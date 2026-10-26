/**
 * Layout - Bố cục chính của app (Sidebar + Topbar + Content)
 */
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import { Search, Bell, User as UserIcon } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

// Map path → tên trang hiển thị trên Topbar
const PAGE_TITLES = {
  "/dashboard":  "Tổng quan",
  "/profile":    "Hồ sơ cá nhân",
  "/timetable":  "Thời khóa biểu",
  "/users":      "Quản lý người dùng",
  "/students":   "Quản lý sinh viên",
  "/teachers":   "Quản lý giáo viên",
  "/curriculum": "Chương trình đào tạo",
  "/courses":    "Môn học",
  "/classes":    "Lớp học",
  "/enrollments":"Đăng ký học tập",
  "/grading":    "Nhập điểm",
  "/attendance": "Điểm danh",
  "/documents":  "Tài liệu học tập",
  "/assignments":"Bài tập",
  "/logs":       "Nhật ký hệ thống",
};

export default function Layout() {
  const location = useLocation();
  const { isTeacher } = useAuth();

  // Tìm tên trang từ path hiện tại
  let pageTitle = Object.entries(PAGE_TITLES).find(([path]) =>
    location.pathname.startsWith(path)
  )?.[1] || "Paradis";

  if (location.pathname.startsWith("/grading") && !isTeacher) {
    pageTitle = "Bảng điểm";
  }

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <h1 className="topbar-title">{pageTitle}</h1>
          <div className="topbar-actions">
            <div className="search-input-wrapper" style={{ margin: 0, minWidth: 200, width: 400, position: 'relative' }}>
              <Search className="search-icon" size={20} />
              <input type="text" className="form-input" placeholder="Tìm kiếm..." style={{ height: 48, paddingLeft: 44, borderRadius: 24, fontSize: 16 }} />
            </div>
            <button className="topbar-btn" style={{ width: 44, height: 44 }}>
              <Bell size={22} />
            </button>
            <button className="topbar-btn" style={{ width: 44, height: 44, background: "var(--accent-light)", color: "var(--accent)" }}>
              <UserIcon size={22} />
            </button>
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
