/**
 * Sidebar - Thanh điều hướng bên trái
 *
 * Menu hiển thị theo role:
 *   ADMIN   → Quản lý hệ thống + Chương trình đào tạo
 *   TEACHER → Quản lý lớp (nhập điểm, điểm danh) + Tài nguyên
 *   STUDENT → Học tập (đăng ký, điểm danh) + Tài nguyên
 */
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../api";

// ── Định nghĩa menu theo section ─────────────────────────────────
const ALL_NAV_ITEMS = [
  // ── Chung (tất cả roles) ─────────────────────────────────────
  {
    section: "Tổng quan",
    items: [
      { path: "/dashboard", icon: "📊", label: "Dashboard", roles: [] },
      { path: "/profile",   icon: "👤", label: "Hồ sơ",    roles: [] },
      { path: "/timetable", icon: "🗓️", label: "Thời khóa biểu", roles: ["TEACHER", "STUDENT"] },
    ],
  },

  // ── Admin: Quản lý hệ thống ──────────────────────────────────
  {
    section: "Quản lý hệ thống",
    items: [
      { path: "/users",    icon: "👥",   label: "Người dùng", roles: ["ADMIN"] },
      { path: "/students", icon: "🎓",   label: "Sinh viên",  roles: ["ADMIN"] },
      { path: "/teachers", icon: "👨‍🏫", label: "Giáo viên",  roles: ["ADMIN"] },
      { path: "/logs",     icon: "📋",   label: "Nhật ký HT", roles: ["ADMIN"] },
    ],
  },

  // ── Admin: Chương trình đào tạo ──────────────────────────────
  {
    section: "Chương trình đào tạo",
    items: [
      { path: "/curriculum",  icon: "📚", label: "Chương trình", roles: ["ADMIN"] },
      { path: "/courses",     icon: "📖", label: "Môn học",       roles: ["ADMIN"] },
      { path: "/classes",     icon: "🏛️", label: "Lớp học",      roles: ["ADMIN"] },
    ],
  },


  // ── Teacher: Quản lý sinh viên ───────────────────────────────
  {
    section: "Quản lý sinh viên",
    items: [
      { path: "/students", icon: "🎓", label: "Danh sách SV", roles: ["TEACHER"] },
    ],
  },

  // ── Teacher: Quản lý lớp ─────────────────────────────────────
  {
    section: "Quản lý lớp học",
    items: [
      { path: "/classes",   icon: "🏛️", label: "Lớp học",   roles: ["TEACHER"] },
      { path: "/grading",   icon: "✏️", label: "Nhập điểm", roles: ["TEACHER"] },
      { path: "/attendance", icon: "✅", label: "Điểm danh", roles: ["TEACHER"] },
    ],
  },

  // ── Teacher: Tài nguyên ──────────────────────────────────────
  {
    section: "Tài nguyên",
    items: [
      { path: "/documents",   icon: "📄", label: "Tài liệu", roles: ["TEACHER"] },
      { path: "/assignments", icon: "📌", label: "Bài tập",  roles: ["TEACHER"] },
    ],
  },

  // ── Student: Học tập ─────────────────────────────────────────
  {
    section: "Học tập",
    items: [
      { path: "/enrollments", icon: "📝", label: "Kết quả & Đăng ký", roles: ["STUDENT"] },
      { path: "/attendance",  icon: "✅", label: "Điểm danh",   roles: ["STUDENT"] },
    ],
  },

  // ── Student: Tài nguyên ──────────────────────────────────────
  {
    section: "Tài nguyên học tập",
    items: [
      { path: "/documents",   icon: "📄", label: "Tài liệu", roles: ["STUDENT"] },
      { path: "/assignments", icon: "📌", label: "Bài tập",  roles: ["STUDENT"] },
    ],
  },
];


export default function Sidebar() {
  const { user, roles, logout } = useAuth();
  const navigate = useNavigate();

  // Xử lý đăng xuất
  const handleLogout = async () => {
    try { await authApi.logout(); } catch { /* ignore */ }
    logout();
  };

  // Avatar và role label
  const avatarLetter = user?.name?.charAt(0)?.toUpperCase() || "U";
  const mainRole     = roles[0] || "USER";
  const roleLabel    = { ADMIN: "Quản trị viên", TEACHER: "Giáo viên", STUDENT: "Sinh viên" }[mainRole] || mainRole;

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🎓</div>
        <div className="sidebar-logo-text">
          <h2>EMS</h2>
          <span>Quản lý đào tạo</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {ALL_NAV_ITEMS.map((section) => {
          // Lọc items theo role của user hiện tại
          const visibleItems = section.items.filter(
            (item) => item.roles.length === 0 || item.roles.some((r) => roles.includes(r))
          );
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.section}>
              <div className="nav-section-title">{section.section}</div>
              {visibleItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                >
                  <span className="nav-item-icon">{item.icon}</span>
                  {item.label}
                </NavLink>
              ))}
            </div>
          );
        })}
      </nav>

      {/* User info & Logout */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-avatar">{avatarLetter}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.name || "User"}</div>
            <div className="sidebar-user-role">{roleLabel}</div>
          </div>
          <button onClick={handleLogout} title="Đăng xuất" className="topbar-btn" style={{ marginLeft: "auto" }}>
            🚪
          </button>
        </div>
      </div>
    </aside>
  );
}
