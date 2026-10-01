import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Grid, Card, Button,
  Chip, Skeleton, Alert, Avatar, IconButton, Tooltip
} from "@mui/material";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LogoutIcon from "@mui/icons-material/Logout";
import RefreshIcon from "@mui/icons-material/Refresh";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import DescriptionIcon from "@mui/icons-material/Description";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import ScienceIcon from "@mui/icons-material/Science";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";
import { useAuth } from "../../context/AuthContext";
import { adminApi } from "../../api/admin";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const StatCard = ({ label, value, subtext, icon, accent = TEAL, loading }) => (
  <Card sx={{ p: 2.5, height: "100%", borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none" }}>
    {loading ? (
      <>
        <Skeleton variant="circular" width={40} height={40} sx={{ mb: 1 }} />
        <Skeleton variant="text" width="60%" sx={{ mb: 0.5 }} />
        <Skeleton variant="text" width="40%" />
      </>
    ) : (
      <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
        <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: `${accent}18`, color: accent, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          {icon}
        </Box>
        <Box sx={{ width: "100%" }}>
          <Typography variant="h4" sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: TEAL, lineHeight: 1.1 }}>
            {value}
          </Typography>
          <Typography variant="caption" sx={{ color: "#5A677D", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", display: "block", mt: 0.5 }}>
            {label}
          </Typography>
          {subtext && (
            <Box sx={{ mt: 1 }}>{subtext}</Box>
          )}
        </Box>
      </Box>
    )}
  </Card>
);

export const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to load admin stats:", err);
      setError("Unable to load system metrics. Please verify administrator authorization.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#F6F8FA", pb: 8 }}>
      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <Box sx={{ backgroundColor: "#0F4C5C", color: "#FFFFFF", py: 3, mb: 4, borderBottom: "3px solid #2E8B75" }}>
        <Container maxWidth="lg">
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Avatar sx={{ width: 50, height: 50, backgroundColor: "#C07D32", color: "#FFFFFF" }}>
                <AdminPanelSettingsIcon sx={{ fontSize: 30 }} />
              </Avatar>
              <Box>
                <Typography variant="h5" sx={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800 }}>
                  UnifiedRx System Administration
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
                  Signed in as <strong>{user?.email || "Super Administrator"}</strong>
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <Tooltip title="Refresh metrics">
                <IconButton onClick={fetchStats} size="small" sx={{ color: "rgba(255,255,255,0.8)", "&:hover": { color: "#FFFFFF" } }}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button
                variant="outlined"
                color="inherit"
                startIcon={<LogoutIcon />}
                onClick={handleLogout}
                sx={{
                  borderColor: "rgba(255,255,255,0.4)",
                  color: "#FFFFFF",
                  fontWeight: 600,
                  "&:hover": { borderColor: "#FFFFFF", backgroundColor: "rgba(255,255,255,0.08)" }
                }}
              >
                Sign Out
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* ── Content ─────────────────────────────────────────────────────────── */}
      <Container maxWidth="lg">
        {error && (
          <Alert severity="error" sx={{ mb: 3.5 }}>
            {error}
          </Alert>
        )}

        {/* ── Stat Cards ────────────────────────────────────────────────────── */}
        <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 2 }}>
          Platform Overview
        </Typography>

        <Grid container spacing={2.5} sx={{ mb: 4.5 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              label="Registered Patients"
              value={stats?.total_patients ?? 0}
              icon={<PeopleAltIcon />}
              accent={TEAL}
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              label="Healthcare Professionals"
              value={stats?.total_doctors ?? 0}
              subtext={
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  <Chip
                    icon={<VerifiedUserIcon sx={{ fontSize: "14px !important" }} />}
                    label={`${stats?.doctors_verified ?? 0} verified`}
                    size="small"
                    sx={{ backgroundColor: "#EBF5F3", color: SAGE, fontSize: "0.7rem", height: 22, fontWeight: 700 }}
                  />
                  <Chip
                    icon={<HourglassEmptyIcon sx={{ fontSize: "14px !important" }} />}
                    label={`${stats?.doctors_pending ?? 0} pending`}
                    size="small"
                    sx={{ backgroundColor: "#FEF3C7", color: AMBER, fontSize: "0.7rem", height: 22, fontWeight: 700 }}
                  />
                </Box>
              }
              icon={<MedicalServicesIcon />}
              accent={SAGE}
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              label="Uploaded Records"
              value={stats?.total_documents ?? 0}
              icon={<DescriptionIcon />}
              accent={AMBER}
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              label="Interaction Alerts Generated"
              value={stats?.total_alerts ?? 0}
              icon={<WarningAmberIcon />}
              accent={stats?.total_alerts > 0 ? CRIMSON : SAGE}
              loading={loading}
            />
          </Grid>
        </Grid>

        {/* ── Navigation Cards ──────────────────────────────────────────────── */}
        <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 2 }}>
          Administrative Modules
        </Typography>

        <Grid container spacing={3}>
          {/* Module 1: Verification Queue */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                p: 3,
                height: "100%",
                borderRadius: 3,
                border: `1px solid ${BORDER}`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  boxShadow: "0 8px 24px rgba(15, 76, 92, 0.08)",
                  borderColor: SAGE,
                },
              }}
            >
              <Box>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#FFF8E1", color: AMBER, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <HourglassEmptyIcon />
                  </Box>
                  {stats?.doctors_pending > 0 && (
                    <Chip
                      label={`${stats.doctors_pending} Pending`}
                      size="small"
                      sx={{ backgroundColor: "#FEE2E2", color: CRIMSON, fontWeight: 800, fontSize: "0.75rem" }}
                    />
                  )}
                </Box>
                <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 1 }}>
                  Clinician Verification Queue
                </Typography>
                <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.5, mb: 2 }}>
                  Review medical credentials, state license numbers, and hospital affiliations. Approve or reject newly registered doctors.
                </Typography>
              </Box>
              <Button
                variant="contained"
                endIcon={<ArrowForwardIcon />}
                onClick={() => navigate("/admin/verification")}
                sx={{
                  backgroundColor: TEAL,
                  color: "#FFFFFF",
                  fontWeight: 700,
                  py: 1.2,
                  "&:hover": { backgroundColor: "#0B3844" },
                }}
              >
                Open Queue
              </Button>
            </Card>
          </Grid>

          {/* Module 2: Knowledge Base & Normalization */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                p: 3,
                height: "100%",
                borderRadius: 3,
                border: `1px solid ${BORDER}`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  boxShadow: "0 8px 24px rgba(15, 76, 92, 0.08)",
                  borderColor: SAGE,
                },
              }}
            >
              <Box>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#EBF5F3", color: SAGE, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <AutoStoriesIcon />
                  </Box>
                  <Chip
                    label={`${stats?.total_interactions_kb ?? 0} Rules`}
                    size="small"
                    sx={{ backgroundColor: "#EBF5F3", color: SAGE, fontWeight: 700, fontSize: "0.75rem" }}
                  />
                </Box>
                <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 1 }}>
                  Knowledge Base & Normalization
                </Typography>
                <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.5, mb: 2 }}>
                  Curate cross-system drug-drug interactions and map unrecognized brand names from clinical OCR to standardized generic/AYUSH entities.
                </Typography>
              </Box>
              <Button
                variant="contained"
                endIcon={<ArrowForwardIcon />}
                onClick={() => navigate("/admin/knowledge-base")}
                sx={{
                  backgroundColor: TEAL,
                  color: "#FFFFFF",
                  fontWeight: 700,
                  py: 1.2,
                  "&:hover": { backgroundColor: "#0B3844" },
                }}
              >
                Manage Knowledge Base
              </Button>
            </Card>
          </Grid>

          {/* Module 3: Lab References */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                p: 3,
                height: "100%",
                borderRadius: 3,
                border: `1px solid ${BORDER}`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  boxShadow: "0 8px 24px rgba(15, 76, 92, 0.08)",
                  borderColor: SAGE,
                },
              }}
            >
              <Box>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#EDE9FE", color: "#6D28D9", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <ScienceIcon />
                  </Box>
                  <Chip
                    label="Reference Intervals"
                    size="small"
                    sx={{ backgroundColor: "#EDE9FE", color: "#6D28D9", fontWeight: 700, fontSize: "0.75rem" }}
                  />
                </Box>
                <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 1 }}>
                  Laboratory Reference Values
                </Typography>
                <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.5, mb: 2 }}>
                  View the clinical normal reference intervals and standard units used by the statistical anomaly detection and z-score engines.
                </Typography>
              </Box>
              <Button
                variant="contained"
                endIcon={<ArrowForwardIcon />}
                onClick={() => navigate("/admin/lab-references")}
                sx={{
                  backgroundColor: TEAL,
                  color: "#FFFFFF",
                  fontWeight: 700,
                  py: 1.2,
                  "&:hover": { backgroundColor: "#0B3844" },
                }}
              >
                View Reference Tables
              </Button>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};
