import React from "react";
import { Box, Typography, Button } from "@mui/material";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#09333E", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 3 }}>
      <Box sx={{ width: 64, height: 64, borderRadius: 3, backgroundColor: "#C07D32", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <AdminPanelSettingsIcon sx={{ color: "#FFFFFF", fontSize: 32 }} />
      </Box>
      <Typography variant="h4" sx={{ color: "#FFFFFF", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        Admin Panel
      </Typography>
      <Typography variant="body1" sx={{ color: "rgba(255,255,255,0.7)" }}>
        {user?.email}
      </Typography>
      <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.45)", fontStyle: "italic" }}>
        Full admin panel (Group 4) — coming next.
      </Typography>
      <Button variant="outlined" sx={{ color: "#FFFFFF", borderColor: "rgba(255,255,255,0.3)", "&:hover": { borderColor: "#FFFFFF" } }} onClick={handleLogout}>
        Sign Out
      </Button>
    </Box>
  );
};
