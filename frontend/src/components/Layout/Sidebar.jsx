import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, User, Calendar, Users, GraduationCap, 
  UserCog, BookOpen, Library, School, UserCheck, 
  PenTool, CheckSquare, FileText, ClipboardList, Settings, LogOut 
} from 'lucide-react';

const NAV_CONFIG = [
  {
    title: "Chính",
    items: [
      { path: "/dashboard", label: "Tổng quan", icon: LayoutDashboard },
      { path: "/profile", label: "Hồ sơ cá nhân", icon: User },
      { path: "/timetable", label: "Thời khóa biểu", icon: Calendar },
    ]
  },
  {
    title: "Quản lý",
    items: [
      { path: "/users", label: "Quản lý người dùng", roles: ["ADMIN"], icon: Users },
      { path: "/students", label: "Quản lý sinh viên", roles: ["ADMIN", "TEACHER"], icon: GraduationCap },
      { path: "/teachers", label: "Quản lý giáo viên", roles: ["ADMIN"], icon: UserCog },
    ]
  },
  {
    title: "Học tập",
    items: [
      { path: "/curriculum", label: "Chương trình đào tạo", icon: BookOpen },
      { path: "/courses", label: "Môn học", icon: Library },
      { path: "/classes", label: "Lớp học", icon: School },
      { path: "/enrollments", label: "Đăng ký học tập", roles: ["STUDENT", "ADMIN"], icon: UserCheck },
    ]
  },
  {
    title: "Đánh giá & Theo dõi",
    items: [
      { path: "/grading", label: "Nhập điểm", roles: ["TEACHER"], icon: PenTool },
      { path: "/grading", label: "Bảng điểm", roles: ["ADMIN"], icon: PenTool },
      { path: "/attendance", label: "Điểm danh", roles: ["ADMIN", "TEACHER", "STUDENT"], icon: CheckSquare },
    ]
  },
  {
    title: "Tài nguyên",
    items: [
      { path: "/documents", label: "Tài liệu học tập", icon: FileText },
      { path: "/assignments", label: "Bài tập", icon: ClipboardList },
    ]
  },
  {
    title: "Hệ thống",
    items: [
      { path: "/logs", label: "Nhật ký hệ thống", roles: ["ADMIN"], icon: Settings },
    ]
  }
];

export default function Sidebar() {
  const { user, hasRole, logout } = useAuth();
  
  // Avatar initial
  const userInitial = user?.name ? user.name.charAt(0).toUpperCase() : "U";
  
  // Display role mapping
  let displayRole = "User";
  if (hasRole("ADMIN")) displayRole = "Administrator";
  else if (hasRole("TEACHER")) displayRole = "Giảng viên";
  else if (hasRole("STUDENT")) displayRole = "Sinh viên";

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">P</div>
        <div className="sidebar-logo-text">
          <h2>Paradis</h2>
          <span>Quản lý Đào tạo</span>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        {NAV_CONFIG.map((section, idx) => {
          // Filter items based on user roles if required
          const visibleItems = section.items.filter(item => {
            if (!item.roles) return true;
            return item.roles.some(role => hasRole(role));
          });

          if (visibleItems.length === 0) return null;

          return (
            <div key={idx}>
              <div className="nav-section-title">{section.title}</div>
              {visibleItems.map(item => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                >
                  <item.icon size={24} strokeWidth={2} />
                  {item.label}
                </NavLink>
              ))}
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-avatar">{userInitial}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name" title={user?.name || user?.email || "User"}>
              {user?.name || user?.email || "User"}
            </div>
            <div className="sidebar-user-role">{displayRole}</div>
          </div>
        </div>
        <button 
          className="btn btn-secondary w-full" style={{ marginTop: 24 }}
          onClick={logout}
        >
          <LogOut size={18} style={{ marginRight: 8 }} /> Đăng xuất
        </button>
      </div>
    </aside>
  );
}
