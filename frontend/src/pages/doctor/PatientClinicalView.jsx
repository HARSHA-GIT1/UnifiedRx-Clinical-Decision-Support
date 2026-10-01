import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Grid, Card, Tabs, Tab, Chip,
  Skeleton, Button, Alert, Avatar, Divider
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import TimelineIcon from "@mui/icons-material/Timeline";
import ScienceIcon from "@mui/icons-material/Science";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import SummarizeIcon from "@mui/icons-material/Summarize";
import AssignmentIcon from "@mui/icons-material/Assignment";
import MedicationIcon from "@mui/icons-material/Medication";
import PersonIcon from "@mui/icons-material/Person";
import { patientApi } from "../../api/patient";
import { HealthIdBadge } from "../../components/common/HealthIdBadge";
import { TimelineViewer } from "../patient/TimelineViewer";
import { LabTrendsPanel } from "../patient/LabTrendsPanel";
import { SafetyAlertsPanel } from "../patient/SafetyAlertsPanel";
import { AISummaryPanel } from "../patient/AISummaryPanel";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
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

export const PatientClinicalView = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(0);

  const fetchDashboard = useCallback(async () => {
    if (!patientId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await patientApi.getDashboard(patientId);
      setDashboard(data);
    } catch (err) {
      console.error("Failed to load patient clinical view:", err);
      const detail = err.response?.data?.detail;
      setError(detail || "Unable to access patient records. Ensure you have active approved consent.");
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const patient = dashboard?.patient || {};
  const stats = dashboard?.statistics || {};
  const crossSystem = stats.cross_system_regimen || false;

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#F6F8FA", pb: 8 }}>
      {/* ── Top Bar with Back Button ────────────────────────────────────────── */}
      <Box sx={{ backgroundColor: "#FFFFFF", borderBottom: `1px solid ${BORDER}`, py: 2 }}>
        <Container maxWidth="lg">
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate("/doctor/dashboard")}
            sx={{
              color: TEAL,
              fontWeight: 700,
              textTransform: "none",
              fontSize: "0.95rem",
              "&:hover": {
                backgroundColor: "#EBF5F3",
              },
            }}
          >
            Back to Clinician Dashboard
          </Button>
        </Container>
      </Box>

      {/* ── Patient Header ─────────────────────────────────────────────────── */}
      <Box sx={{ backgroundColor: "#FFFFFF", borderBottom: `1px solid ${BORDER}`, py: 3, mb: 3 }}>
        <Container maxWidth="lg">
          {loading ? (
            <Box sx={{ py: 1 }}>
              <Skeleton variant="text" width="40%" height={40} />
              <Skeleton variant="text" width="60%" height={24} />
            </Box>
          ) : error ? (
            <Alert
              severity="error"
              action={
                <Button color="inherit" size="small" onClick={() => navigate("/doctor/dashboard")}>
                  Return to Dashboard
                </Button>
              }
            >
              {error}
            </Alert>
          ) : (
            <Box>
              <Box
                sx={{
                  display: "flex",
                  flexDirection: { xs: "column", md: "row" },
                  alignItems: { xs: "flex-start", md: "center" },
                  justifyContent: "space-between",
                  gap: 2,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 2.5 }}>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      backgroundColor: `${TEAL}15`,
                      color: TEAL,
                      border: `2px solid ${TEAL}30`,
                    }}
                  >
                    <PersonIcon sx={{ fontSize: 36 }} />
                  </Avatar>
                  <Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, flexWrap: "wrap" }}>
                      <Typography
                        variant="h4"
                        sx={{
                          fontFamily: "'Plus Jakarta Sans', sans-serif",
                          fontWeight: 700,
                          color: TEAL,
                        }}
                      >
                        {patient.name || "Patient Record"}
                      </Typography>
                      {crossSystem && (
                        <Chip
                          label="Cross-System Regimen"
                          size="small"
                          sx={{
                            backgroundColor: "#FEF3C7",
                            color: "#92400E",
                            fontWeight: 700,
                            border: "1px solid #FCD34D",
                          }}
                        />
                      )}
                    </Box>

                    {/* Clinical Demographics - NO phone number */}
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 0.8, flexWrap: "wrap" }}>
                      {patient.age && (
                        <Typography variant="body2" sx={{ color: "#5A677D", fontWeight: 500 }}>
                          Age: <strong>{patient.age} yrs</strong>
                        </Typography>
                      )}
                      {patient.gender && (
                        <Typography variant="body2" sx={{ color: "#5A677D", fontWeight: 500 }}>
                          Gender: <strong>{patient.gender}</strong>
                        </Typography>
                      )}
                      {patient.blood_group && (
                        <Typography variant="body2" sx={{ color: "#5A677D", fontWeight: 500 }}>
                          Blood Group: <strong>{patient.blood_group}</strong>
                        </Typography>
                      )}
                      {patient.health_code && (
                        <HealthIdBadge id={patient.health_code} label="Health ID" size="medium" />
                      )}
                    </Box>
                  </Box>
                </Box>
              </Box>

              {/* Cross-system banner if applicable */}
              {crossSystem && (
                <Alert
                  severity="warning"
                  icon={<WarningAmberIcon sx={{ color: AMBER }} />}
                  sx={{
                    mt: 2.5,
                    backgroundColor: "#FFFBEB",
                    border: "1px solid #FDE68A",
                    color: "#92400E",
                    fontWeight: 500,
                  }}
                >
                  <strong>Cross-System Regimen Active:</strong> This patient is concurrently receiving prescriptions across multiple medical philosophies (Allopathy + AYUSH). Cross-system interaction screening and laboratory association monitoring are active.
                </Alert>
              )}
            </Box>
          )}
        </Container>
      </Box>

      {/* ── Main Clinical Content ─────────────────────────────────────────── */}
      {!error && (
        <Container maxWidth="lg">
          {/* Quick Clinical Metrics */}
          <Grid container spacing={2.5} sx={{ mb: 4 }}>
            <Grid item xs={6} sm={3}>
              <StatCard
                label="Clinical Documents"
                value={stats.total_documents ?? 0}
                icon={<AssignmentIcon />}
                loading={loading}
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard
                label="Active Medicines"
                value={stats.total_medicines ?? 0}
                icon={<MedicationIcon />}
                loading={loading}
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard
                label="Safety Alerts"
                value={stats.total_alerts ?? 0}
                icon={<WarningAmberIcon />}
                accent={stats.total_alerts > 0 ? CRIMSON : SAGE}
                loading={loading}
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard
                label="Flagged Labs"
                value={stats.flagged_labs_count ?? 0}
                icon={<ScienceIcon />}
                accent={stats.flagged_labs_count > 0 ? AMBER : SAGE}
                loading={loading}
              />
            </Grid>
          </Grid>

          {/* Clinical Panels Navigation Tabs */}
          <Card sx={{ borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none", overflow: "hidden" }}>
            <Box sx={{ borderBottom: `1px solid ${BORDER}`, backgroundColor: "#FFFFFF", px: 2 }}>
              <Tabs
                value={tab}
                onChange={(_, v) => setTab(v)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  "& .MuiTab-root": {
                    fontWeight: 700,
                    fontSize: "0.95rem",
                    textTransform: "none",
                    minHeight: 52,
                    color: "#5A677D",
                    "&.Mui-selected": {
                      color: TEAL,
                    },
                  },
                  "& .MuiTabs-indicator": {
                    backgroundColor: TEAL,
                    height: 3,
                  },
                }}
              >
                <Tab icon={<TimelineIcon />} iconPosition="start" label="Longitudinal Timeline" />
                <Tab icon={<ScienceIcon />} iconPosition="start" label="Laboratory Trends" />
                <Tab
                  icon={<WarningAmberIcon />}
                  iconPosition="start"
                  label={
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <span>Safety Alerts</span>
                      {stats.total_alerts > 0 && (
                        <Chip
                          label={stats.total_alerts}
                          size="small"
                          sx={{
                            height: 20,
                            fontSize: "0.75rem",
                            backgroundColor: CRIMSON,
                            color: "#FFFFFF",
                            fontWeight: 700,
                          }}
                        />
                      )}
                    </Box>
                  }
                />
                <Tab icon={<SummarizeIcon />} iconPosition="start" label="AI Clinical Summary" />
              </Tabs>
            </Box>

            <Box sx={{ p: { xs: 2, sm: 3 } }}>
              <TabPanel value={tab} index={0}>
                <TimelineViewer
                  patientId={patientId}
                  initialData={dashboard?.recent_timeline}
                />
              </TabPanel>
              <TabPanel value={tab} index={1}>
                <LabTrendsPanel
                  patientId={patientId}
                  initialData={dashboard?.lab_trends}
                />
              </TabPanel>
              <TabPanel value={tab} index={2}>
                <SafetyAlertsPanel
                  patientId={patientId}
                  initialData={dashboard?.safety_alerts}
                />
              </TabPanel>
              <TabPanel value={tab} index={3}>
                <AISummaryPanel
                  patientId={patientId}
                  initialData={dashboard?.latest_summary}
                />
              </TabPanel>
            </Box>
          </Card>
        </Container>
      )}
    </Box>
  );
};
