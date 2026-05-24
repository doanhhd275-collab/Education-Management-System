/**
 * Trang Hồ sơ cá nhân
 */
import { useAuth } from "../../context/AuthContext";

export default function ProfilePage() {
  const { user, roles } = useAuth();

  if (!user) return null;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">👤 Hồ sơ cá nhân</h2>
          <p className="page-subtitle">Thông tin tài khoản của bạn</p>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 600 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 32 }}>
          <div style={{ 
            width: 80, height: 80, borderRadius: "50%", 
            background: "linear-gradient(135deg, var(--accent), #818cf8)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 32, color: "white", fontWeight: "bold"
          }}>
            {user.name?.charAt(0)?.toUpperCase()}
          </div>
          <div>
            <h3 style={{ fontSize: 24, color: "var(--text-primary)" }}>{user.name}</h3>
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              {roles.map(r => <span key={r} className="badge badge-primary">{r}</span>)}
            </div>
          </div>
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">User ID</label>
            <input className="form-input" value={user.user_id} readOnly />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Email</label>
            <input className="form-input" value={user.email} readOnly />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Số điện thoại</label>
            <input className="form-input" value={user.contact || "Chưa cập nhật"} readOnly />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Ngày sinh</label>
            <input className="form-input" value={user.birth || "Chưa cập nhật"} readOnly />
          </div>
        </div>
      </div>
    </div>
  );
}
