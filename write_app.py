code = """import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { LandingPage } from "./pages/public/LandingPage";
import { RegisterChoice } from "./pages/public/RegisterChoice";
import { PatientRegister } from "./pages/public/PatientRegister";
import { DoctorRegister } from "./pages/public/DoctorRegister";
import { LoginPage } from "./pages/public/LoginPage";
import { AdminLogin } from "./pages/public/AdminLogin";
import { PatientDashboard } from "./pages/patient/PatientDashboard";
import { DoctorDashboard } from "./pages/doctor/DoctorDashboard";
import { PatientClinicalView } from "./pages/doctor/PatientClinicalView";
import { AdminDashboard } from "./pages/admin/AdminDashboard";

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    if (user.role === "patient") return <Navigate to="/patient/dashboard" replace />;
    if (user.role === "healthcare_professional") return <Navigate to="/doctor/dashboard" replace />;
    if (user.role === "admin") return <Navigate to="/admin/dashboard" replace />;
    return <Navigate to="/" replace />;
  }
  return children;
};

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/register" element={<RegisterChoice />} />
      <Route path="/register/patient" element={<PatientRegister />} />
      <Route path="/register/doctor" element={<DoctorRegister />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/patient/dashboard"
        element={
          <ProtectedRoute allowedRoles={["patient"]}>
            <PatientDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctor/dashboard"
        element={
          <ProtectedRoute allowedRoles={["healthcare_professional"]}>
            <DoctorDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctor/patients/:patientId"
        element={
          <ProtectedRoute allowedRoles={["healthcare_professional"]}>
            <PatientClinicalView />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute allowedRoles={["admin"]}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
"""

with open(r"E:\Capstone\Projectwork\frontend\src\App.jsx", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated App.jsx successfully")