/**
 * Trang Thời khóa biểu
 * - TEACHER: Xem lịch dạy của mình (các lớp được gán)
 * - STUDENT: Xem lịch học của mình (các lớp đã đăng ký)
 * Hiển thị dạng lưới: cột = Thứ (2-7), hàng = Tiết (1-12)
 */
import { useState, useEffect } from "react";
import { classesApi } from "../../api";
import { useAuth } from "../../context/AuthContext";

// ── Constants ────────────────────────────────────────────────
const DAYS = ["2", "3", "4", "5", "6", "7"];
const DAY_LABELS = {
  "2": "Thứ Hai",
  "3": "Thứ Ba",
  "4": "Thứ Tư",
  "5": "Thứ Năm",
  "6": "Thứ Sáu",
  "7": "Thứ Bảy",
};

const MORNING_PERIODS = [1, 2, 3, 4, 5, 6];
const AFTERNOON_PERIODS = [7, 8, 9, 10, 11, 12];

// Giờ học theo tiết
const PERIOD_TIMES = {
  1: "7:00 – 7:50",
  2: "7:50 – 8:40",
  3: "8:40 – 9:30",
  4: "9:40 – 10:30",
  5: "10:30 – 11:20",
  6: "11:20 – 12:10",
  7: "13:00 – 13:50",
  8: "13:50 – 14:40",
  9: "14:40 – 15:30",
  10: "15:40 – 16:30",
  11: "16:30 – 17:20",
  12: "17:20 – 18:10",
};

// Màu accent cho từng môn (cycle) - refined warm professional palette
const COLORS = [
  { bg: "#FFF0E6", border: "#EA580C", text: "#9A3412" }, // Orange
  { bg: "#FBE9E7", border: "#9F2D20", text: "#7F1D1D" }, // Brick red
  { bg: "#E8F5EE", border: "#16A34A", text: "#166534" }, // Green
  { bg: "#E8F1FB", border: "#2563EB", text: "#1E40AF" }, // Blue
];

// ── Timetable Grid ────────────────────────────────────────────
function TimetableGrid({ classes }) {
  // Map: day_of_week → list of classes that overlap that day
  const getClassesForCell = (day, period) =>
    classes.filter(
      (c) =>
        c.day_of_week === day &&
        c.start_period <= period &&
        c.end_period >= period
    );

  // Gán màu theo course_id
  const colorMap = {};
  let ci = 0;
  classes.forEach((c) => {
    if (!colorMap[c.course_id]) {
      colorMap[c.course_id] = COLORS[ci % COLORS.length];
      ci++;
    }
  });

  // Determine which cells are "continuation" (not the first period of a class)
  const isFirstPeriod = (cls, period) => cls.start_period === period;

  const renderPeriodRows = (periods) =>
    periods.map((period) => (
      <tr key={period}>
        {/* Tiết label */}
        <td
          style={{
            padding: "8px 12px",
            textAlign: "center",
            whiteSpace: "nowrap",
            borderRight: "1px solid var(--border)",
            borderBottom: "1px solid var(--border)",
            background: "var(--bg-secondary)",
            position: "sticky",
            left: 0,
            zIndex: 1,
            minWidth: 120,
          }}
        >
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>
            Tiết {period}
          </div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>
            {PERIOD_TIMES[period]}
          </div>
        </td>

        {/* Ô cho từng thứ */}
        {DAYS.map((day) => {
          const matches = getClassesForCell(day, period);
          return (
            <td
              key={day}
              style={{
                padding: 4,
                verticalAlign: "top",
                border: "1px solid var(--border)",
                borderBottom: "1px solid var(--border)",
                minWidth: 150,
                minHeight: 60,
                background:
                  matches.length > 0
                    ? colorMap[matches[0].course_id]?.bg
                    : "transparent",
              }}
            >
              {matches
                .filter((c) => isFirstPeriod(c, period))
                .map((c) => {
                  const col = colorMap[c.course_id] || COLORS[0];
                  return (
                    <div
                      key={c.class_id}
                      style={{
                        borderLeft: `4px solid ${col.border}`,
                        padding: "8px 12px",
                        background: col.bg,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 14,
                          fontWeight: 600,
                          color: col.text,
                          lineHeight: 1.3,
                          marginBottom: 4,
                        }}
                      >
                        {c.course_name || c.course_id}
                      </div>
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          color: col.text,
                          opacity: 0.9,
                        }}
                      >
                        {c.class_id}
                      </div>
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          color: col.text,
                          opacity: 0.9,
                          marginTop: 4,
                        }}
                      >
                        Tiết {c.start_period}–{c.end_period}
                        {c.room && `  •  ${c.room}`}
                      </div>
                    </div>
                  );
                })}
            </td>
          );
        })}
      </tr>
    ));

  if (classes.filter((c) => c.day_of_week && c.start_period).length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📅</div>
        <h3>Chưa có lịch học</h3>
        <p style={{ color: "var(--text-secondary)", marginTop: 8 }}>
          Các lớp cần được cài đặt thứ và tiết học bởi Admin.
        </p>
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          minWidth: 900,
          fontSize: 13,
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                padding: "12px 16px",
                textAlign: "center",
                background: "#F5F3F0",
                border: "1px solid var(--border)",
                position: "sticky",
                left: 0,
                zIndex: 2,
                color: "#44403C",
                fontSize: 14,
                fontWeight: 600,
                minWidth: 120,
              }}
            >
              Tiết / Thứ
            </th>
            {DAYS.map((d) => (
              <th
                key={d}
                style={{
                  padding: "12px 16px",
                  textAlign: "center",
                  background: "#F5F3F0",
                  border: "1px solid var(--border)",
                  color: "#44403C",
                  fontWeight: 600,
                  fontSize: 14,
                }}
              >
                {DAY_LABELS[d]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* BUỔI SÁNG */}
          <tr>
            <td
              colSpan={DAYS.length + 1}
              style={{
                padding: "10px 16px",
                background: "#FFF7ED",
                color: "#C2410C",
                fontWeight: 600,
                fontSize: 14,
                letterSpacing: "0.5px",
                borderTop: "2px solid #EA580C",
                borderBottom: "1px solid var(--border)",
                borderLeft: "1px solid var(--border)",
                borderRight: "1px solid var(--border)",
              }}
            >
              BUỔI SÁNG — Tiết 1 đến 6
            </td>
          </tr>
          {renderPeriodRows(MORNING_PERIODS)}

          {/* BUỔI CHIỀU */}
          <tr>
            <td
              colSpan={DAYS.length + 1}
              style={{
                padding: "10px 16px",
                background: "#F5F1EC",
                color: "#9F2D20",
                fontWeight: 600,
                fontSize: 14,
                letterSpacing: "0.5px",
                borderTop: "2px solid #9F2D20",
                borderBottom: "1px solid var(--border)",
                borderLeft: "1px solid var(--border)",
                borderRight: "1px solid var(--border)",
              }}
            >
              BUỔI CHIỀU — Tiết 7 đến 12
            </td>
          </tr>
          {renderPeriodRows(AFTERNOON_PERIODS)}
        </tbody>
      </table>
    </div>
  );
}

// ── Legend ────────────────────────────────────────────────────
function ClassLegend({ classes }) {
  const unique = [];
  const seen = new Set();
  for (const c of classes) {
    if (!seen.has(c.class_id)) {
      seen.add(c.class_id);
      unique.push(c);
    }
  }
  if (unique.length === 0) return null;

  const colorMap = {};
  let ci = 0;
  classes.forEach((c) => {
    if (!colorMap[c.course_id]) {
      colorMap[c.course_id] = COLORS[ci % COLORS.length];
      ci++;
    }
  });

  const DAY_LABELS_SHORT = { "2":"T2","3":"T3","4":"T4","5":"T5","6":"T6","7":"T7" };

  return (
    <div
      className="card"
      style={{ padding: "16px 20px", marginBottom: 24 }}
    >
      <h4 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 16 }}>
         Danh sách lớp học
      </h4>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {unique.map((c) => {
          const col = colorMap[c.course_id] || COLORS[0];
          return (
            <div
              key={c.class_id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                background: col.bg,
                border: `1px solid ${col.border}`,
                borderRadius: 8,
                padding: "10px 16px",
                minHeight: 44,
              }}
            >
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: col.border,
                  flexShrink: 0,
                }}
              />
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: col.text }}>
                  {c.course_name || c.course_id}
                </div>
                <div style={{ color: col.text, opacity: 0.9, fontSize: 13, marginTop: 4 }}>
                  {c.class_id}
                  {c.day_of_week && c.start_period
                    ? ` · ${DAY_LABELS_SHORT[c.day_of_week]} Tiết ${c.start_period}–${c.end_period}`
                    : " · Chưa có lịch"}
                  {c.room && ` · Phòng ${c.room}`}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────
export default function TimetablePage() {
  const { isTeacher, isStudent, isAdmin } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState("grid"); // "grid" | "list"

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        let res;
        if (isTeacher) {
          res = await classesApi.getTeacherTimetable();
        } else if (isStudent) {
          res = await classesApi.getStudentTimetable();
        } else if (isAdmin) {
          // Admin xem tất cả lớp
          res = await classesApi.list(null, null, 1, 100);
        }
        setClasses(res?.data || []);
      } catch {
        setError("Không thể tải thời khóa biểu");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isTeacher, isStudent, isAdmin]);

  const title = isTeacher
    ? " Lịch dạy của tôi"
    : isStudent
    ? " Lịch học của tôi"
    : " Thời khóa biểu";

  const subtitle = isTeacher
    ? "Lịch giảng dạy theo thứ và tiết"
    : isStudent
    ? "Lịch học theo thứ và tiết"
    : "Tổng quan thời khóa biểu";

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">{title}</h1>
          <p className="page-subtitle">{subtitle}</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className={`btn ${viewMode === "grid" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setViewMode("grid")}
          >
            ⊞ Dạng lưới
          </button>
          <button
            className={`btn ${viewMode === "list" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setViewMode("list")}
          >
            ☰ Danh sách
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error"> {error}</div>}

      {loading ? (
        <div className="loading-page">
          <div className="spinner" /> Đang tải thời khóa biểu...
        </div>
      ) : (
        <>
          <ClassLegend classes={classes} />

          {viewMode === "grid" ? (
            <div className="card" style={{ padding: 0, overflow: "hidden" }}>
              <TimetableGrid classes={classes} />
            </div>
          ) : (
            /* Chế độ danh sách */
            <div className="card" style={{ padding: 0 }}>
              {classes.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon">📅</div>
                  <h3>Chưa có lớp học nào</h3>
                </div>
              ) : (
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Mã lớp</th>
                        <th>Môn học</th>
                        <th>Học kỳ</th>
                        <th style={{ textAlign: "center" }}>Thứ</th>
                        <th style={{ textAlign: "center" }}>Tiết</th>
                        <th style={{ textAlign: "center" }}>Giờ học</th>
                        <th style={{ textAlign: "center" }}>Phòng</th>
                        <th style={{ textAlign: "center" }}>Sĩ số</th>
                      </tr>
                    </thead>
                    <tbody>
                      {classes.map((c) => {
                        const startTime = c.start_period ? PERIOD_TIMES[c.start_period]?.split("–")[0]?.trim() : null;
                        const endTime = c.end_period ? PERIOD_TIMES[c.end_period]?.split("–")[1]?.trim() : null;
                        return (
                          <tr key={c.class_id}>
                            <td>
                              <span className="badge badge-primary">{c.class_id}</span>
                            </td>
                            <td>
                              <div style={{ fontWeight: 500 }}>{c.course_name || c.course_id}</div>
                              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{c.course_id}</div>
                            </td>
                            <td style={{ color: "var(--text-secondary)" }}>
                              {c.semester || "—"}
                            </td>
                            <td style={{ textAlign: "center" }}>
                              {c.day_of_week ? (
                                <span className="badge badge-info">
                                  {DAY_LABELS[c.day_of_week]}
                                </span>
                              ) : (
                                <span style={{ color: "var(--text-muted)" }}>—</span>
                              )}
                            </td>
                            <td style={{ textAlign: "center" }}>
                              {c.start_period ? (
                                <span>
                                  {c.start_period === c.end_period
                                    ? `Tiết ${c.start_period}`
                                    : `Tiết ${c.start_period} – ${c.end_period}`}
                                </span>
                              ) : (
                                <span style={{ color: "var(--text-muted)" }}>—</span>
                              )}
                            </td>
                            <td style={{ textAlign: "center", fontSize: 12, color: "var(--text-secondary)" }}>
                              {startTime && endTime ? `${startTime} – ${endTime}` : "—"}
                            </td>
                            <td style={{ textAlign: "center", fontSize: 12 }}>
                              {c.room
                                ? <span className="badge" style={{ background: "rgba(16,185,129,0.15)", color: "#6ee7b7", border: "1px solid #10b981" }}>{c.room}</span>
                                : <span style={{ color: "var(--text-muted)" }}>—</span>}
                            </td>
                            <td style={{ textAlign: "center" }}>
                              {c.capacity ?? "—"}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
