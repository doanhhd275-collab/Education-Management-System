/**
 * Dashboard - Trang tổng quan
 * Hiển thị thống kê và truy cập nhanh theo role.
 *
 * Sinh viên: thêm bảng "Trạng thái học tập" gồm CPA, GPA, cảnh báo, số môn đang học.
 */
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { studentsApi, teachersApi, enrollmentsApi } from "../../api";
import apiClient from "../../api/client";
import { 
  Users, GraduationCap, UserCog, BookOpen, Library, School, 
  UserCheck, PenTool, CheckSquare, FileText, ClipboardList, 
  Settings, LayoutDashboard, TrendingUp, TrendingDown 
} from 'lucide-react';

function StatCard({ icon: Icon, value, label, color = "var(--accent)", bg = "var(--accent-light)", trend }) {
  return (
    <div className="stat-card" style={{ flexDirection: 'row', alignItems: 'center', gap: '24px', padding: '32px' }}>
      <div 
        style={{ 
          width: 64, height: 64, borderRadius: 16, background: bg, color: color,
          display: 'flex', alignItems: 'center', justifyContent: 'center' 
        }}
      >
        <Icon size={32} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 52, fontWeight: 700, color: "var(--text-primary)", lineHeight: 1.1 }}>{value ?? "—"}</div>
        <div style={{ fontSize: 18, color: "var(--text-secondary)", marginTop: 8 }}>{label}</div>
        {trend && (
          <div style={{ fontSize: 15, color: trend > 0 ? "var(--success)" : "var(--danger)", marginTop: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
            {trend > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{trend > 0 ? '+' : ''}{trend}% so với tháng trước</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Quick link ────────────────────────────────────────────────────
function QuickLink({ icon: Icon, label, to, color = "var(--accent)" }) {
  return (
    <Link
      to={to}
      style={{
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        gap: "16px", padding: "20px 12px", borderRadius: "16px", height: "150px", minWidth: "180px",
        background: "var(--bg-secondary)", border: "1px solid var(--border-light)",
        textDecoration: "none", transition: "all 0.18s ease",
        boxShadow: "var(--shadow)"
      }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "var(--shadow-lg)"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border-light)"; e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "var(--shadow)"; }}
    >
      <div style={{ color: color }}>
        <Icon size={40} />
      </div>
      <span style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-secondary)", textAlign: "center", lineHeight: 1.3 }}>{label}</span>
    </Link>
  );
}

// ── Bảng trạng thái học tập cho Sinh viên ────────────────────────
function StudentStatusPanel({ userId }) {
  const [info, setInfo]     = useState(null);
  const [loading, setLoad]  = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        // Gọi song song: thông tin student + danh sách enrollment
        const [svRes, enrollRes] = await Promise.allSettled([
          apiClient.get(`/students/${userId}`),
          apiClient.get(`/enrollments`, { params: { student_id: userId, page_size: 100 } }),
        ]);

        const sv      = svRes.status      === "fulfilled" ? svRes.value.data      : null;
        const enrolls = enrollRes.status  === "fulfilled" ? enrollRes.value.data  : [];

        setInfo({
          gpa:        sv?.GPA           ?? sv?.gpa           ?? null,
          cpa:        sv?.CPA           ?? sv?.cpa           ?? null,
          warning:    sv?.warning_level ?? sv?.warning       ?? "Bình thường",
          program_id: sv?.program_id    ?? "",
          studying:   enrolls.filter(e => e.status === "STUDYING").length,
          passed:     enrolls.filter(e => e.status === "PASSED").length,
          failed:     enrolls.filter(e => e.status === "FAILED").length,
          total:      enrolls.length,
        });
      } catch (err) {
        console.error("Lỗi tải trạng thái học tập:", err);
      } finally {
        setLoad(false);
      }
    };
    if (userId) load();
  }, [userId]);

  // Màu cảnh báo
  const warningColor = {
    "Bình thường": "var(--success)",
    "Cảnh báo 1":  "var(--warning)",
    "Cảnh báo 2":  "var(--danger)",
    "Buộc thôi học": "var(--danger)",
  };

  if (loading) return (
    <div className="card" style={{ marginBottom: 24 }}>
      <div className="card-header"><h3 className="card-title">📈 Trạng thái học tập</h3></div>
      <div style={{ padding: "20px 0", display: "flex", gap: 10, alignItems: "center", color: "var(--text-muted)" }}>
        <div className="spinner" style={{ width: 18, height: 18 }} /> Đang tải...
      </div>
    </div>
  );

  return (
    <div className="card" style={{ marginBottom: 24 }}>
      <div className="card-header">
        <h3 className="card-title">📈 Trạng thái học tập</h3>
        {info?.program_id && (
          <span className="badge badge-primary" style={{ marginLeft: 8 }}>
            {info.program_id}
          </span>
        )}
      </div>

      {/* Thống kê chính */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap: 16, marginBottom: 20,
      }}>
        {/* GPA */}
        <div style={{
          padding: "16px 20px", background: "var(--bg-tertiary)", borderRadius: "var(--radius)",
          border: "1px solid var(--border-light)", textAlign: "center",
        }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>GPA (Kỳ này)</div>
          <div style={{
            fontSize: 32, fontWeight: 800,
            color: info?.gpa >= 3.5 ? "var(--success)" : info?.gpa >= 2.5 ? "var(--accent)" : "var(--warning)",
          }}>
            {info?.gpa != null ? Number(info.gpa).toFixed(2) : "—"}
          </div>
        </div>

        {/* CPA */}
        <div style={{
          padding: "16px 20px", background: "var(--bg-tertiary)", borderRadius: "var(--radius)",
          border: "1px solid var(--border-light)", textAlign: "center",
        }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>CPA (Tích lũy)</div>
          <div style={{
            fontSize: 32, fontWeight: 800,
            color: info?.cpa >= 3.5 ? "var(--success)" : info?.cpa >= 2.5 ? "var(--accent)" : "var(--warning)",
          }}>
            {info?.cpa != null ? Number(info.cpa).toFixed(2) : "—"}
          </div>
        </div>

        {/* Mức cảnh báo */}
        <div style={{
          padding: "16px 20px", background: "var(--bg-tertiary)", borderRadius: "var(--radius)",
          border: `1px solid ${warningColor[info?.warning] || "var(--border-light)"}33`,
          textAlign: "center",
        }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>Mức cảnh báo</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: warningColor[info?.warning] || "var(--text-secondary)" }}>
            {info?.warning === "Bình thường" ? " Bình thường" :
             info?.warning === "Cảnh báo 1"  ? " Cảnh báo 1" :
             info?.warning === "Cảnh báo 2"  ? "🔴 Cảnh báo 2" :
             info?.warning === "Buộc thôi học" ? "🚫 Buộc thôi học" :
             info?.warning || "—"}
          </div>
        </div>

        {/* Đang học */}
        <div style={{
          padding: "16px 20px", background: "var(--bg-tertiary)", borderRadius: "var(--radius)",
          border: "1px solid var(--border-light)", textAlign: "center",
        }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>Đang học</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: "var(--accent)" }}>
            {info?.studying ?? "—"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>môn học</div>
        </div>
      </div>

      {/* Thanh tiến độ */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {[
          { label: "Đã qua",    count: info?.passed,   color: "var(--success)", icon: "" },
          { label: "Đang học",  count: info?.studying, color: "var(--accent)",  icon: "" },
          { label: "Chưa qua",  count: info?.failed,   color: "var(--danger)",  icon: "" },
          { label: "Tổng cộng", count: info?.total,    color: "var(--text-muted)", icon: "" },
        ].map((item) => (
          <div key={item.label} style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "6px 12px", background: "var(--bg-secondary)", borderRadius: 20,
            fontSize: 13, color: "var(--text-secondary)",
          }}>
            {item.icon}
            <strong style={{ color: item.color }}>{item.count ?? "—"}</strong>
            {item.label}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { user, isAdmin, isTeacher, isStudent, roles } = useAuth();
  const [stats, setStats]   = useState({});
  const [loading, setLoad]  = useState(true);

  const firstName = user?.name?.split(" ").pop() || "bạn";
  const roleLabel = { ADMIN: "Quản trị viên", TEACHER: "Giáo viên", STUDENT: "Sinh viên" }[roles[0]] || "Người dùng";
  const today = new Date().toLocaleDateString("vi-VN", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  useEffect(() => {
    let cancelled = false;
    const loadStats = async () => {
      try {
        const results = {};
        if (isAdmin) {
          const [sv, gv] = await Promise.allSettled([
            studentsApi.list(),
            teachersApi.list(),
          ]);
          results.students = sv.status === "fulfilled" ? sv.value.data.length : "?";
          results.teachers = gv.status === "fulfilled" ? gv.value.data.length : "?";
        } else if (isTeacher) {
          try {
            const tcRes = await teachersApi.getMyInfo();
            const clsRes = await teachersApi.getClasses(tcRes.data.teacher_id);
            results.classes = clsRes.data.length;
          } catch { results.classes = "?"; }
          const sv = await studentsApi.list().catch(() => ({ data: [] }));
          results.students = sv.data.length;
        }
        if (!cancelled) setStats(results);
      } catch (err) {
        console.error("Lỗi tải thống kê:", err);
      } finally {
        if (!cancelled) setLoad(false);
      }
    };
    loadStats();
    return () => { cancelled = true; };
  }, [isAdmin, isTeacher, isStudent]); // eslint-disable-line

  // Quick links theo role
  const adminLinks = [
    { icon: Users, label: "Người dùng", to: "/users", color: "#E8590C" },
    { icon: GraduationCap, label: "Sinh viên", to: "/students", color: "#16A34A" },
    { icon: UserCog, label: "Giáo viên", to: "/teachers", color: "#2563EB" },
    { icon: BookOpen, label: "Chương trình đào tạo", to: "/curriculum", color: "#8B5CF6" },
    { icon: Library, label: "Môn học", to: "/courses", color: "#D97706" },
    { icon: School, label: "Lớp học", to: "/classes", color: "#059669" },
    { icon: PenTool, label: "Bảng điểm", to: "/grading", color: "#EA580C" },
    { icon: Settings, label: "Nhật ký hệ thống", to: "/logs", color: "#4B5563" },
  ];
  const teacherLinks = [
    { icon: School, label: "Lớp học", to: "/classes", color: "#2563EB" },
    { icon: BookOpen, label: "CT Đào tạo", to: "/curriculum", color: "#8B5CF6" },
    { icon: Library, label: "Môn học", to: "/courses", color: "#D97706" },
    { icon: PenTool, label: "Nhập điểm", to: "/grading", color: "#E8590C" },
    { icon: CheckSquare, label: "Điểm danh", to: "/attendance", color: "#16A34A" },
    { icon: FileText, label: "Tài liệu", to: "/documents", color: "#0284C7" },
    { icon: ClipboardList, label: "Bài tập", to: "/assignments", color: "#DC2626" },
  ];
  const studentLinks = [
    { icon: BookOpen, label: "CT Đào tạo", to: "/curriculum", color: "#8B5CF6" },
    { icon: Library, label: "Môn học", to: "/courses", color: "#D97706" },
    { icon: School, label: "Lớp học", to: "/classes", color: "#2563EB" },
    { icon: UserCheck, label: "Đăng ký học", to: "/enrollments", color: "#E8590C" },
    { icon: CheckSquare, label: "Điểm danh", to: "/attendance", color: "#16A34A" },
    { icon: FileText, label: "Tài liệu", to: "/documents", color: "#0284C7" },
    { icon: ClipboardList, label: "Bài tập", to: "/assignments", color: "#DC2626" },
  ];
  const quickLinks = isAdmin ? adminLinks : isTeacher ? teacherLinks : studentLinks;

  return (
    <div>
      {/* ── Header ─────────────────────────────────────────── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Xin chào, {user?.name || firstName}!
          </h1>
          <p className="page-subtitle">
            Vai trò: <span style={{ color: "var(--accent)", fontWeight: 600 }}>{roleLabel}</span>
            {" · "}{today}
          </p>
        </div>
      </div>

      {/* ── Bảng trạng thái học tập (chỉ Sinh viên) ─────── */}
      {isStudent && <StudentStatusPanel userId={user?.user_id} />}

      {/* ── Thống kê (Admin & Teacher) ───────────────────── */}
      {!isStudent && (
        loading ? (
          <div style={{ display: "flex", alignItems: "center", gap: 10, color: "var(--text-muted)", marginBottom: 24 }}>
            <div className="spinner" style={{ width: 18, height: 18 }} /> Đang tải thống kê...
          </div>
        ) : (
          <div className="stats-grid" style={{ marginBottom: 28 }}>
            {isAdmin && (
              <>
                <StatCard icon={GraduationCap} value={stats.students} label="Tổng sinh viên" color="var(--accent)" bg="var(--accent-light)" trend={12} />
                <StatCard icon={UserCog} value={stats.teachers} label="Tổng giáo viên" color="var(--info)" bg="var(--info-bg)" trend={5} />
                <StatCard icon={School} value={142} label="Tổng số lớp học" color="var(--success)" bg="var(--success-bg)" trend={2} />
                <StatCard icon={BookOpen} value={45} label="Chương trình đào tạo" color="#8B5CF6" bg="#EDE9FE" trend={0} />
              </>
            )}
            {isTeacher && (
              <>
                <StatCard icon={School} value={stats.classes}  label="Lớp đang dạy" color="var(--accent)" bg="var(--accent-light)" />
                <StatCard icon={GraduationCap} value={stats.students} label="Tổng sinh viên" color="var(--success)" bg="var(--success-bg)" />
              </>
            )}
          </div>
        )
      )}

      {/* ── Truy cập nhanh ───────────────────────────────── */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">⚡ Truy cập nhanh</h3>
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: "24px", padding: "4px 0",
        }}>
          {quickLinks.map((item) => (
            <QuickLink key={item.to} icon={item.icon} label={item.label} to={item.to} color={item.color} />
          ))}
        </div>
      </div>
    </div>
  );
}
