import React from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Chip,
} from "@mui/material";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import LogoutIcon from "@mui/icons-material/Logout";
import { useAuth } from "../../context/AuthContext";
import { HealthIdBadge } from "./HealthIdBadge";

export const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <AppBar position="sticky" elevation={0}>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: "space-between", minHeight: 70 }}>
          {/* Brand Logo */}
          <Box
            component={RouterLink}
            to={
              !isAuthenticated
                ? "/"
                : user?.role === "patient"
                ? "/patient/dashboard"
                : user?.role === "healthcare_professional"
                ? "/doctor/dashboard"
                : "/admin/dashboard"
            }
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.2,
              textDecoration: "none",
              color: "#0F4C5C",
            }}
          >
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 2,
                backgroundColor: "#0F4C5C",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#FFFFFF",
              }}
            >
              <LocalHospitalIcon fontSize="small" />
            </Box>
            <Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  lineHeight: 1.1,
                  color: "#0F4C5C",
                  letterSpacing: "-0.01em",
                }}
              >
                UnifiedRx
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  fontSize: "0.68rem",
                  color: "#2E8B75",
                  fontWeight: 600,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                  display: "block",
                }}
              >
                Cross-System Safety
              </Typography>
            </Box>
          </Box>

          {/* Navigation / Actions */}
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {!isAuthenticated ? (
              <>
                <Button
                  component={RouterLink}
                  to="/#features"
                  sx={{ color: "#1A2230", display: { xs: "none", md: "inline-flex" } }}
                >
                  Features
                </Button>
                <Button
                  component={RouterLink}
                  to="/#how-it-works"
                  sx={{ color: "#1A2230", display: { xs: "none", md: "inline-flex" } }}
                >
                  How It Works
                </Button>
                <Button
                  component={RouterLink}
                  to="/#credibility"
                  sx={{ color: "#1A2230", display: { xs: "none", md: "inline-flex" } }}
                >
                  Clinical Safety
                </Button>
                <Button
                  component={RouterLink}
                  to="/login"
                  variant="outlined"
                  sx={{
                    borderColor: "#0F4C5C",
                    color: "#0F4C5C",
                    "&:hover": { borderColor: "#09333E", backgroundColor: "#F0F7F6" },
                  }}
                >
                  Log In
                </Button>
                <Button
                  component={RouterLink}
                  to="/register"
                  variant="contained"
                  color="primary"
                >
                  Get Started
                </Button>
              </>
            ) : (
              <>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: "#1A2230" }}>
                    {user?.full_name || "User"}
                  </Typography>

                  <Chip
                    label={
                      user?.role === "patient"
                        ? "Patient"
                        : user?.role === "healthcare_professional"
                        ? "Clinician"
                        : "Admin"
                    }
                    size="small"
                    sx={{
                      backgroundColor:
                        user?.role === "patient"
                          ? "#EBF5F3"
                          : user?.role === "healthcare_professional"
                          ? "#FDF3E7"
                          : "#F3E8FF",
                      color:
                        user?.role === "patient"
                          ? "#0F4C5C"
                          : user?.role === "healthcare_professional"
                          ? "#C07D32"
                          : "#6B21A8",
                      fontWeight: 600,
                      fontSize: "0.75rem",
                    }}
                  />

                  {user?.health_code && (
                    <HealthIdBadge id={user.health_code} label="Health ID" />
                  )}

                  {user?.professional_code && (
                    <HealthIdBadge id={user.professional_code} label="Prof ID" />
                  )}

                  <Button
                    onClick={handleLogout}
                    variant="text"
                    startIcon={<LogoutIcon />}
                    size="small"
                    sx={{ color: "#5A677D", ml: 1 }}
                  >
                    Log Out
                  </Button>
                </Box>
              </>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};
