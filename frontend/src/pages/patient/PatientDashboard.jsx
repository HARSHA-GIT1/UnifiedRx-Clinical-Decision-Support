import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Grid, Card, Tabs, Tab, Chip,
  Skeleton, IconButton, Tooltip, Snackbar, Alert as MuiAlert,
  Avatar, Divider,
} from "@mui/material";
import LogoutIcon from "@mui/icons-material/Logout";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import TimelineIcon from "@mui/icons-material/Timeline";
import ScienceIcon from "@mui/icons-material/Science";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import SummarizeIcon from "@mui/icons-material/Summarize";
import PeopleOutlineIcon from "@mui/icons-material/PeopleOutlined";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import AssignmentIcon from "@mui/icons-material/Assignment";
import MedicationIcon from "@mui/icons-material/Medication";
import { useAuth } from "../../context/AuthContext";
import { patientApi } from "../../api/patient";
import { DocumentUpload } from "./DocumentUpload";
import { TimelineViewer } from "./TimelineViewer";
import { LabTrendsPanel } from "./LabTrendsPanel";
import { SafetyAlertsPanel } from "./SafetyAlertsPanel";
import { AISummaryPanel } from "./AISummaryPanel";
import { AccessGrantsPanel } from "./AccessGrantsPanel";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const SLATE = "#F6F8FA";
const BORDER = "#E2E8F0";

// ── Stat Card ────────────────────────────────────────────────────────────────
const StatCard = ({ label, value, icon, accent = TEAL, loading }) => (
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
        <Box>
          <Typography variant="h4" sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: TEAL, lineHeight: 1.1 }}>
            {value}
          </Typography>
          <Typography variant="caption" sx={{ color: "#5A677D", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            {label}
          </Typography>
        </Box>
      </Box>
    )}
  </Card>
);

// ── Tab Panel ────────────────────────────────────────────────────────────────
const TabPanel = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

// ── Main Dashboard ───────────────────────────────────────────────────────────
export const PatientDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(0);
  const [copied, setCopied] = useState(false);

  const patientId = dashboard?.patient?.patient_id || null;

  const fetchDashboard = useCallback(async (pid) => {
    if (!pid) return;
    setLoading(true);
    try {
      const data = await patientApi.getDashboard(pid);
      setDashboard(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // On mount: get patient_id from /patients/me, then fetch dashboard
  useEffect(() => {
    (async () => {
      try {
        const profile = await patientApi.getMe();
        await fetchDashboard(profile.patient_id);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    })();
  }, [fetchDashboard]);

  const handleCopy = () => {
    if (dashboard?.patient?.health_code) {
      navigator.clipboard.writeText(dashboard.patient.health_code);
      setCopied(true);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const stats = dashboard?.statistics || {};
  const patient = dashboard?.patient || {};

  const TABS = [
    { label: "Upload", icon: <UploadFileIcon fontSize="small" /> },
    { label: "Timeline", icon: <TimelineIcon fontSize="small" /> },
    { label: "Lab Trends", icon: <ScienceIcon fontSize="small" /> },
    { label: "Safety Alerts", icon: <WarningAmberIcon fontSize="small" />, badge: stats.total_alerts > 0 ? stats.total_alerts : null },
    { label: "AI Summary", icon: <SummarizeIcon fontSize="small" /> },
    { label: "Access", icon: <PeopleOutlineIcon fontSize="small" /> },
  ];

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: SLATE }}>
      {/* ── Header Bar ── */}
      <Box sx={{ backgroundColor: TEAL, color: "#fff", px: { xs: 2, md: 4 }, py: 2.5 }}>
        <Container maxWidth="xl" disableGutters>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Avatar sx={{ backgroundColor: SAGE, width: 44, height: 44, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 }}>
                {loading ? "…" : (patient.name?.[0] || "P")}
              </Avatar>
              <Box>
                {loading ? (
                  <>
                    <Skeleton variant="text" width={160} sx={{ bgcolor: "rgba(255,255,255,0.15)" }} />
                    <Skeleton variant="text" width={100} sx={{ bgcolor: "rgba(255,255,255,0.1)" }} />
                  </>
                ) : (
                  <>
                    <Typography variant="h6" sx={{ color: "#fff", fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, lineHeight: 1.2 }}>
                      {patient.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.65)" }}>
                      {patient.gender && `${patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1)}`}
                      {patient.age && ` · ${patient.age} yrs`}
                      {patient.blood_group && ` · ${patient.blood_group}`}
                    </Typography>
                  </>
                )}
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              {/* Health ID Badge */}
              {loading ? (
                <Skeleton variant="rounded" width={180} height={36} sx={{ bgcolor: "rgba(255,255,255,0.15)" }} />
              ) : (
                <Box sx={{ display: "flex", alignItems: "center", gap: 1, backgroundColor: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)", borderRadius: 2, px: 2, py: 0.75 }}>
                  <VerifiedUserIcon sx={{ fontSize: 16, color: "rgba(255,255,255,0.7)" }} />
                  <Typography sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, fontSize: "0.9rem", color: "#fff", letterSpacing: "0.05em" }}>
                    {patient.health_code}
                  </Typography>
                  <Tooltip title="Copy Health ID">
                    <IconButton size="small" onClick={handleCopy} sx={{ color: "rgba(255,255,255,0.7)", p: 0.3, "&:hover": { color: "#fff" } }}>
                      <ContentCopyIcon sx={{ fontSize: 14 }} />
                    </IconButton>
                  </Tooltip>
                </Box>
              )}
              <Tooltip title="Sign out">
                <IconButton onClick={handleLogout} sx={{ color: "rgba(255,255,255,0.7)", "&:hover": { color: "#fff" } }}>
                  <LogoutIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {error && (
          <MuiAlert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</MuiAlert>
        )}

        {/* ── Stats Row ── */}
        <Grid container spacing={2.5} sx={{ mb: 4 }}>
          {[
            { label: "Documents", value: stats.total_documents ?? 0, icon: <AssignmentIcon />, accent: TEAL },
            { label: "Medicines Tracked", value: stats.total_medicines ?? 0, icon: <MedicationIcon />, accent: SAGE },
            {
              label: "Cross-System Regimen",
              value: loading ? "—" : stats.cross_system_regimen ? "YES" : "NO",
              icon: <TimelineIcon />,
              accent: stats.cross_system_regimen ? AMBER : SAGE,
            },
            { label: "Flagged Labs", value: stats.flagged_labs_count ?? 0, icon: <ScienceIcon />, accent: stats.flagged_labs_count > 0 ? CRIMSON : SAGE },
            { label: "Active Alerts", value: stats.total_alerts ?? 0, icon: <WarningAmberIcon />, accent: stats.total_alerts > 0 ? CRIMSON : SAGE },
          ].map((s) => (
            <Grid item xs={6} sm={4} md={2.4} key={s.label}>
              <StatCard {...s} loading={loading} />
            </Grid>
          ))}
        </Grid>

        {/* ── Cross-System Banner ── */}
        {!loading && stats.cross_system_regimen && (
          <MuiAlert
            severity="warning"
            sx={{ mb: 3, borderRadius: 2, backgroundColor: "#FDF3E7", border: "1px solid #ECC94B", "& .MuiAlert-icon": { color: AMBER } }}
          >
            <strong>Cross-System Regimen Detected.</strong> This patient is concurrently prescribed medicines from {stats.prescribed_systems?.join(" + ")}. Check the Safety Alerts tab for any interaction warnings.
          </MuiAlert>
        )}

        {/* ── Tab Navigation ── */}
        <Card sx={{ borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none", overflow: "hidden" }}>
          <Box sx={{ borderBottom: `1px solid ${BORDER}`, backgroundColor: "#FFFFFF" }}>
            <Tabs
              value={tab}
              onChange={(_, v) => setTab(v)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                "& .MuiTab-root": { textTransform: "none", fontWeight: 600, fontFamily: "'Plus Jakarta Sans', sans-serif", minHeight: 52, fontSize: "0.88rem" },
                "& .Mui-selected": { color: TEAL },
                "& .MuiTabs-indicator": { backgroundColor: TEAL },
              }}
            >
              {TABS.map((t, i) => (
                <Tab
                  key={t.label}
                  icon={t.icon}
                  iconPosition="start"
                  label={
                    t.badge ? (
                      <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                        {t.label}
                        <Chip label={t.badge} size="small" sx={{ height: 18, fontSize: "0.7rem", backgroundColor: CRIMSON, color: "#fff" }} />
                      </Box>
                    ) : t.label
                  }
                  id={`tab-${i}`}
                />
              ))}
            </Tabs>
          </Box>

          <Box sx={{ p: { xs: 2, md: 3 }, backgroundColor: "#FFFFFF" }}>
            <TabPanel value={tab} index={0}>
              <DocumentUpload patientId={patientId} onUploadComplete={() => fetchDashboard(patientId)} />
            </TabPanel>
            <TabPanel value={tab} index={1}>
              <TimelineViewer patientId={patientId} initialData={dashboard?.recent_timeline} />
            </TabPanel>
            <TabPanel value={tab} index={2}>
              <LabTrendsPanel patientId={patientId} initialData={dashboard?.lab_trends} />
            </TabPanel>
            <TabPanel value={tab} index={3}>
              <SafetyAlertsPanel patientId={patientId} initialData={dashboard?.safety_alerts} />
            </TabPanel>
            <TabPanel value={tab} index={4}>
              <AISummaryPanel patientId={patientId} initialData={dashboard?.latest_summary} />
            </TabPanel>
            <TabPanel value={tab} index={5}>
              <AccessGrantsPanel patientId={patientId} />
            </TabPanel>
          </Box>
        </Card>
      </Container>

      <Snackbar open={copied} autoHideDuration={2000} onClose={() => setCopied(false)} message="Health ID copied to clipboard" anchorOrigin={{ vertical: "bottom", horizontal: "center" }} />
    </Box>
  );
};
