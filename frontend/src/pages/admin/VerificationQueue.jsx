import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Card, Button, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, Skeleton, Chip, Accordion, AccordionSummary, AccordionDetails,
  CircularProgress, Dialog, DialogTitle, DialogContent, DialogContentText,
  DialogActions
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";
import RefreshIcon from "@mui/icons-material/Refresh";
import { adminApi } from "../../api/admin";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

export const VerificationQueue = () => {
  const navigate = useNavigate();

  const [pending, setPending] = useState([]);
  const [rejected, setRejected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null); // professional_id currently processing
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({ open: false, id: null, name: null, status: null });

  const loadQueues = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [pendingData, rejectedData] = await Promise.all([
        adminApi.getPendingProfessionals(),
        adminApi.getRejectedProfessionals(),
      ]);
      setPending(Array.isArray(pendingData) ? pendingData : []);
      setRejected(Array.isArray(rejectedData) ? rejectedData : []);
    } catch (err) {
      console.error("Failed to load verification queues:", err);
      setError("Unable to load professional verification queues.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadQueues();
  }, [loadQueues]);

  const handleVerify = async (profId, newStatus) => {
    setActionLoading(profId);
    setError(null);
    setSuccessMsg(null);
    try {
      await adminApi.verifyProfessional(profId, newStatus);
      setSuccessMsg(`Professional account has been ${newStatus === "verified" ? "approved" : "rejected"} successfully.`);
      await loadQueues();
    } catch (err) {
      console.error("Verification update error:", err);
      setError(err.response?.data?.detail || "Failed to update professional status.");
    } finally {
      setActionLoading(null);
      setConfirmDialog({ open: false, id: null, name: null, status: null });
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#F6F8FA", pb: 8 }}>
      {/* ── Top Bar ─────────────────────────────────────────────────────────── */}
      <Box sx={{ backgroundColor: "#FFFFFF", borderBottom: `1px solid ${BORDER}`, py: 2 }}>
        <Container maxWidth="lg">
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate("/admin/dashboard")}
            sx={{
              color: TEAL,
              fontWeight: 700,
              textTransform: "none",
              fontSize: "0.95rem",
              "&:hover": { backgroundColor: "#EBF5F3" },
            }}
          >
            Back to Admin Dashboard
          </Button>
        </Container>
      </Box>

      {/* ── Page Header ────────────────────────────────────────────────────── */}
      <Box sx={{ backgroundColor: "#FFFFFF", borderBottom: `1px solid ${BORDER}`, py: 3, mb: 4 }}>
        <Container maxWidth="lg">
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
            <Box>
              <Typography variant="h5" sx={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: TEAL }}>
                Clinician Credential Verification
              </Typography>
              <Typography variant="body2" sx={{ color: "#5A677D", mt: 0.5 }}>
                Review medical practitioner registrations and grant access to patient search and cross-system records.
              </Typography>
            </Box>
            <Button
              startIcon={<RefreshIcon />}
              onClick={loadQueues}
              variant="outlined"
              size="small"
              sx={{ borderColor: BORDER, color: "#5A677D", fontWeight: 600 }}
            >
              Refresh Queue
            </Button>
          </Box>
        </Container>
      </Box>

      {/* ── Content ─────────────────────────────────────────────────────────── */}
      <Container maxWidth="lg">
        {successMsg && (
          <Alert severity="success" onClose={() => setSuccessMsg(null)} sx={{ mb: 3 }}>
            {successMsg}
          </Alert>
        )}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* ── Pending Verification Section ──────────────────────────────────── */}
        <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none", mb: 4 }}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2.5 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <HourglassEmptyIcon sx={{ color: AMBER, fontSize: 24 }} />
              <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700 }}>
                Pending Review ({pending.length})
              </Typography>
            </Box>
            {pending.length > 0 && (
              <Chip
                label="Action Required"
                size="small"
                sx={{ backgroundColor: "#FEF3C7", color: AMBER, fontWeight: 800, fontSize: "0.75rem" }}
              />
            )}
          </Box>

          {loading ? (
            <Box sx={{ py: 2 }}>
              <Skeleton variant="rectangular" height={56} sx={{ mb: 1.5, borderRadius: 2 }} />
              <Skeleton variant="rectangular" height={56} sx={{ mb: 1.5, borderRadius: 2 }} />
              <Skeleton variant="rectangular" height={56} sx={{ borderRadius: 2 }} />
            </Box>
          ) : pending.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 5, backgroundColor: "#F8FAFC", borderRadius: 2, border: `1px dashed ${BORDER}` }}>
              <CheckCircleIcon sx={{ fontSize: 44, color: SAGE, mb: 1 }} />
              <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                No pending verification requests
              </Typography>
              <Typography variant="body2" sx={{ color: "#718096", mt: 0.5 }}>
                All registered healthcare professional accounts have been reviewed.
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table sx={{ minWidth: 750 }}>
                <TableHead>
                  <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Professional Code</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Doctor Name</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Medical License</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Specialization</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Hospital Affiliation</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700, color: TEAL }}>Review Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pending.map((doc) => (
                    <TableRow key={doc.professional_id} sx={{ "&:hover": { backgroundColor: "#F7FAFC" } }}>
                      <TableCell>
                        <Chip
                          label={doc.professional_code}
                          size="small"
                          sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, backgroundColor: "#EBF5F3", color: TEAL }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: "#2D3748" }}>{doc.full_name}</TableCell>
                      <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.85rem", color: "#4A5568" }}>
                        {doc.license_number}
                      </TableCell>
                      <TableCell sx={{ color: "#4A5568" }}>{doc.specialization}</TableCell>
                      <TableCell sx={{ color: "#4A5568" }}>{doc.hospital_affiliation}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: "inline-flex", gap: 1 }}>
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={actionLoading === doc.professional_id ? <CircularProgress size={16} color="inherit" /> : <CheckCircleIcon />}
                            disabled={actionLoading !== null}
                            onClick={() => handleVerify(doc.professional_id, "verified")}
                            sx={{ backgroundColor: SAGE, color: "#FFFFFF", fontWeight: 700, textTransform: "none", "&:hover": { backgroundColor: "#246F5E" } }}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="outlined"
                            size="small"
                            color="error"
                            startIcon={<CancelIcon />}
                            disabled={actionLoading !== null}
                            onClick={() => setConfirmDialog({ open: true, id: doc.professional_id, name: doc.full_name, status: "rejected" })}
                            sx={{ fontWeight: 700, textTransform: "none" }}
                          >
                            Reject
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Card>

        {/* ── Rejected Professionals Collapsible Section ────────────────────── */}
        <Accordion
          sx={{
            borderRadius: 3,
            border: `1px solid ${BORDER}`,
            boxShadow: "none",
            "&:before": { display: "none" },
            overflow: "hidden",
          }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ backgroundColor: "#F8FAFC", px: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <CancelIcon sx={{ color: CRIMSON, fontSize: 20 }} />
              <Typography variant="subtitle1" sx={{ color: TEAL, fontWeight: 700 }}>
                Rejected Accounts ({rejected.length})
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 3 }}>
            {rejected.length === 0 ? (
              <Typography variant="body2" sx={{ color: "#718096" }}>
                No accounts currently marked as rejected.
              </Typography>
            ) : (
              <TableContainer>
                <Table sx={{ minWidth: 700 }}>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: "#FFF5F5" }}>
                      <TableCell sx={{ fontWeight: 700, color: CRIMSON }}>Code</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: CRIMSON }}>Name</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: CRIMSON }}>License Number</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: CRIMSON }}>Specialization</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: CRIMSON }}>Hospital</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700, color: CRIMSON }}>Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rejected.map((doc) => (
                      <TableRow key={doc.professional_id}>
                        <TableCell>
                          <Chip label={doc.professional_code} size="small" sx={{ fontFamily: "'JetBrains Mono', monospace" }} />
                        </TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>{doc.full_name}</TableCell>
                        <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace" }}>{doc.license_number}</TableCell>
                        <TableCell>{doc.specialization}</TableCell>
                        <TableCell>{doc.hospital_affiliation}</TableCell>
                        <TableCell align="right">
                          <Button
                            variant="outlined"
                            size="small"
                            disabled={actionLoading !== null}
                            onClick={() => handleVerify(doc.professional_id, "verified")}
                            sx={{ color: SAGE, borderColor: SAGE, fontWeight: 700, textTransform: "none", "&:hover": { backgroundColor: "#EBF5F3" } }}
                          >
                            Re-Approve
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </AccordionDetails>
        </Accordion>
      </Container>

      {/* ── Confirmation Dialog ─────────────────────────────────────────────── */}
      <Dialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false, id: null, name: null, status: null })}>
        <DialogTitle sx={{ color: CRIMSON, fontWeight: 700 }}>Confirm Account Rejection</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to reject the credentials for <strong>{confirmDialog.name}</strong>? The user will not be allowed to access patient data.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmDialog({ open: false, id: null, name: null, status: null })}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => handleVerify(confirmDialog.id, "rejected")}
            sx={{ fontWeight: 700 }}
          >
            Confirm Rejection
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
