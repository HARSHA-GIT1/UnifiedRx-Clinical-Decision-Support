code = """import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Card, Grid, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, AlertTitle, Skeleton, Avatar, Chip, Tooltip, IconButton
} from "@mui/material";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import LogoutIcon from "@mui/icons-material/Logout";
import VisibilityIcon from "@mui/icons-material/Visibility";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import RefreshIcon from "@mui/icons-material/Refresh";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import { useAuth } from "../../context/AuthContext";
import { accessApi } from "../../api/access";
import { HealthIdBadge } from "../../components/common/HealthIdBadge";
import { PatientSearch } from "./PatientSearch";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const BORDER = "#E2E8F0";

export const DoctorDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const isPending = user?.verification_status === "pending";
  const isVerified = user?.verification_status === "verified";

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPatients = useCallback(async () => {
    if (isPending) return;
    setLoading(true);
    setError(null);
    try {
      const data = await accessApi.getMyPatients();
      setPatients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load approved patients:", err);
      setError("Unable to load approved patients list. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [isPending]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleViewRecords = (patientId) => {
    navigate(`/doctor/patients/${patientId}`);
  };

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#F6F8FA", pb: 8 }}>
      {/* ── Prominent Verification Warning Banner ──────────────────────────── */}
      {isPending && (
        <Box
          sx={{
            width: "100%",
            backgroundColor: "#FFF8E1",
            borderBottom: "2px solid #FFE082",
            py: 2.5,
            px: { xs: 2, sm: 4 },
            boxShadow: "0 4px 12px rgba(192, 125, 50, 0.08)",
          }}
        >
          <Container maxWidth="lg">
            <Alert
              severity="warning"
              icon={<HourglassEmptyIcon sx={{ fontSize: 32, color: AMBER }} />}
              sx={{
                backgroundColor: "transparent",
                p: 0,
                alignItems: "center",
                "& .MuiAlert-message": { width: "100%" },
              }}
            >
              <Typography
                variant="h6"
                sx={{
                  color: "#7B4B0A",
                  fontWeight: 800,
                  fontSize: { xs: "1rem", sm: "1.15rem" },
                  mb: 0.5,
                }}
              >
                ACCOUNT UNDER VERIFICATION
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: "#8D5400",
                  fontWeight: 500,
                  fontSize: { xs: "0.9rem", sm: "0.98rem" },
                  lineHeight: 1.5,
                }}
              >
                Your account is under verification. You can log in but cannot search for patients until an administrator approves your credentials. This typically takes 24–48 hours.
              </Typography>
            </Alert>
          </Container>
        </Box>
      )}

      {/* ── Top Header ──────────────────────────────────────────────────────── */}
      <Box
        sx={{
          backgroundColor: "#FFFFFF",
          borderBottom: `1px solid ${BORDER}`,
          py: 3,
          mb: 4,
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              alignItems: { xs: "flex-start", md: "center" },
              justifyContent: "space-between",
              gap: 2,
            }}
          >
            {/* Doctor Identity */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Avatar
                sx={{
                  width: 56,
                  height: 56,
                  backgroundColor: `${TEAL}15`,
                  color: TEAL,
                  border: `2px solid ${TEAL}30`,
                }}
              >
                <MedicalServicesIcon sx={{ fontSize: 30 }} />
              </Avatar>
              <Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, flexWrap: "wrap" }}>
                  <Typography
                    variant="h5"
                    sx={{
                      fontFamily: "'Plus Jakarta Sans', sans-serif",
                      fontWeight: 700,
                      color: TEAL,
                    }}
                  >
                    Dr. {user?.full_name || "Healthcare Professional"}
                  </Typography>
                  {isVerified ? (
                    <Chip
                      icon={<VerifiedUserIcon sx={{ fontSize: "16px !important", color: `${SAGE} !important` }} />}
                      label="Verified Clinician"
                      size="small"
                      sx={{
                        backgroundColor: "#EBF5F3",
                        color: SAGE,
                        fontWeight: 600,
                        fontSize: "0.75rem",
                      }}
                    />
                  ) : (
                    <Chip
                      label="Pending Verification"
                      size="small"
                      sx={{
                        backgroundColor: "#FEF3C7",
                        color: "#92400E",
                        fontWeight: 600,
                        fontSize: "0.75rem",
                      }}
                    />
                  )}
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 0.5, flexWrap: "wrap" }}>
                  {user?.specialization && (
                    <Typography variant="body2" sx={{ color: "#5A677D", fontWeight: 500 }}>
                      Specialization: <strong>{user.specialization}</strong>
                    </Typography>
                  )}
                  {user?.professional_code && (
                    <HealthIdBadge id={user.professional_code} label="Professional ID" size="medium" />
                  )}
                </Box>
              </Box>
            </Box>

            {/* Actions */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, alignSelf: { xs: "flex-end", md: "center" } }}>
              <Button
                variant="outlined"
                color="inherit"
                startIcon={<LogoutIcon />}
                onClick={handleLogout}
                sx={{
                  borderColor: BORDER,
                  color: "#5A677D",
                  fontWeight: 600,
                  "&:hover": {
                    borderColor: "#CBD5E0",
                    backgroundColor: "#F7FAFC",
                  },
                }}
              >
                Sign Out
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* ── Main Dashboard Content ──────────────────────────────────────────── */}
      <Container maxWidth="lg">
        <Grid container spacing={3.5}>
          {/* Patient Search Section */}
          <Grid item xs={12}>
            <PatientSearch
              disabled={isPending}
              onRequestSuccess={() => {
                // If the user requests access, they can refresh patient list anytime
                fetchPatients();
              }}
            />
          </Grid>

          {/* My Patients List Section */}
          <Grid item xs={12}>
            <Card
              sx={{
                p: { xs: 2, sm: 3 },
                borderRadius: 3,
                border: `1px solid ${BORDER}`,
                boxShadow: "none",
                backgroundColor: "#FFFFFF",
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 2.5,
                  flexWrap: "wrap",
                  gap: 1.5,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                  <PeopleAltIcon sx={{ color: TEAL, fontSize: 26 }} />
                  <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700 }}>
                    My Patients ({patients.length})
                  </Typography>
                </Box>
                <Tooltip title="Refresh patient list">
                  <span>
                    <IconButton
                      onClick={fetchPatients}
                      disabled={loading || isPending}
                      size="small"
                      sx={{ color: "#718096" }}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </span>
                </Tooltip>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2.5 }}>
                  {error}
                </Alert>
              )}

              {loading ? (
                <Box sx={{ py: 3 }}>
                  <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
                  <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
                  <Skeleton variant="rectangular" height={52} sx={{ borderRadius: 2 }} />
                </Box>
              ) : isPending ? (
                <Box
                  sx={{
                    textAlign: "center",
                    py: 5,
                    px: 2,
                    backgroundColor: "#F8FAFC",
                    borderRadius: 2,
                    border: `1px dashed ${BORDER}`,
                  }}
                >
                  <HourglassEmptyIcon sx={{ fontSize: 44, color: "#A0AEC0", mb: 1 }} />
                  <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                    Patient records locked pending verification
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#718096", maxWidth: 500, mx: "auto", mt: 0.5 }}>
                    Once an administrator verifies your medical license and credentials, your active patient roster and clinical records will appear here.
                  </Typography>
                </Box>
              ) : patients.length === 0 ? (
                <Box
                  sx={{
                    textAlign: "center",
                    py: 5,
                    px: 2,
                    backgroundColor: "#F8FAFC",
                    borderRadius: 2,
                    border: `1px dashed ${BORDER}`,
                  }}
                >
                  <PeopleAltIcon sx={{ fontSize: 44, color: "#CBD5E0", mb: 1 }} />
                  <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                    No approved patients yet
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#718096", maxWidth: 500, mx: "auto", mt: 0.5 }}>
                    Enter a patient's Health ID in the search box above to request consent. Once approved, their clinical profile and timeline will appear here.
                  </Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table sx={{ minWidth: 600 }}>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, py: 1.5 }}>Health ID</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, py: 1.5 }}>Patient Name</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, py: 1.5 }}>Access Approved Date</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700, color: TEAL, py: 1.5 }}>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {patients.map((pat) => (
                        <TableRow
                          key={pat.patient_id}
                          sx={{
                            "&:hover": { backgroundColor: "#F7FAFC" },
                            borderBottom: `1px solid ${BORDER}`,
                          }}
                        >
                          <TableCell sx={{ py: 2 }}>
                            <Chip
                              label={pat.health_code}
                              size="small"
                              sx={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontWeight: 700,
                                backgroundColor: "#EBF5F3",
                                color: TEAL,
                                border: "1px solid #B8DFD8",
                              }}
                            />
                          </TableCell>
                          <TableCell sx={{ py: 2, fontWeight: 600, color: "#2D3748" }}>
                            {pat.patient_name}
                          </TableCell>
                          <TableCell sx={{ py: 2, color: "#5A677D" }}>
                            {pat.approved_date
                              ? new Date(pat.approved_date).toLocaleDateString("en-IN", {
                                  day: "2-digit",
                                  month: "short",
                                  year: "numeric",
                                })
                              : "—"}
                          </TableCell>
                          <TableCell align="right" sx={{ py: 2 }}>
                            <Button
                              variant="contained"
                              size="small"
                              startIcon={<VisibilityIcon />}
                              onClick={() => handleViewRecords(pat.patient_id)}
                              sx={{
                                backgroundColor: SAGE,
                                color: "#FFFFFF",
                                fontWeight: 700,
                                textTransform: "none",
                                px: 2,
                                "&:hover": {
                                  backgroundColor: "#246F5E",
                                },
                              }}
                            >
                              View Records
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};
"""

with open(r"E:\Capstone\Projectwork\frontend\src\pages\doctor\DoctorDashboard.jsx", "w", encoding="utf-8") as f:
    f.write(code)
print("Created DoctorDashboard.jsx successfully")