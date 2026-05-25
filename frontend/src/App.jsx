import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

// Components
import Layout from "./components/Layout/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import LoginPage from "./pages/Login/LoginPage";
import DashboardPage from "./pages/Dashboard/DashboardPage";
import UsersPage from "./pages/Users/UsersPage";
import StudentsPage from "./pages/Students/StudentsPage";
import TeachersPage from "./pages/Teachers/TeachersPage";
import CurriculumPage from "./pages/Curriculum/CurriculumPage";
import CoursesPage from "./pages/Courses/CoursesPage";
import ClassesPage from "./pages/Classes/ClassesPage";
import EnrollmentsPage from "./pages/Enrollment/EnrollmentsPage";
import GradingPage from "./pages/Grading/GradingPage";
import DocumentsPage from "./pages/Documents/DocumentsPage";
import AssignmentsPage from "./pages/Assignments/AssignmentsPage";
import AttendancePage from "./pages/Attendance/AttendancePage";
import LogsPage from "./pages/Logs/LogsPage";
import ProfilePage from "./pages/Profile/ProfilePage";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Protected routes wrapped in Layout */}
          <Route element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            {/* Dashboard (All users) */}
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/profile" element={<ProfilePage />} />

          {/* ── Admin only ── */}
            <Route path="/users" element={
              <ProtectedRoute roles={["ADMIN"]}><UsersPage /></ProtectedRoute>
            } />
            <Route path="/teachers" element={
              <ProtectedRoute roles={["ADMIN"]}><TeachersPage /></ProtectedRoute>
            } />
            <Route path="/curriculum" element={
              <ProtectedRoute roles={["ADMIN"]}><CurriculumPage /></ProtectedRoute>
            } />
            <Route path="/courses" element={
              <ProtectedRoute roles={["ADMIN"]}><CoursesPage /></ProtectedRoute>
            } />
            <Route path="/logs" element={
              <ProtectedRoute roles={["ADMIN"]}><LogsPage /></ProtectedRoute>
            } />

            {/* ── Admin + Teacher ── */}
            <Route path="/students" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER"]}><StudentsPage /></ProtectedRoute>
            } />
            <Route path="/grading" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER"]}><GradingPage /></ProtectedRoute>
            } />

            {/* ── Teacher + Student + Admin ── */}
            <Route path="/classes" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER", "STUDENT"]}><ClassesPage /></ProtectedRoute>
            } />
            <Route path="/documents" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER", "STUDENT"]}><DocumentsPage /></ProtectedRoute>
            } />
            <Route path="/assignments" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER", "STUDENT"]}><AssignmentsPage /></ProtectedRoute>
            } />
            <Route path="/attendance" element={
              <ProtectedRoute roles={["ADMIN", "TEACHER", "STUDENT"]}><AttendancePage /></ProtectedRoute>
            } />

            {/* ── Student only ── */}
            <Route path="/enrollments" element={
              <ProtectedRoute roles={["STUDENT", "ADMIN"]}><EnrollmentsPage /></ProtectedRoute>
            } />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
