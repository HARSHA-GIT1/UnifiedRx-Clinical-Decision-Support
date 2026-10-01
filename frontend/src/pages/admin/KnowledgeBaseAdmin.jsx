import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Card, Tabs, Tab, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, Skeleton, Chip, TextField, MenuItem, Dialog,
  DialogTitle, DialogContent, DialogActions, InputAdornment, Grid
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AddIcon from "@mui/icons-material/Add";
import SearchIcon from "@mui/icons-material/Search";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import AssignmentLateIcon from "@mui/icons-material/AssignmentLate";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import RefreshIcon from "@mui/icons-material/Refresh";
import { adminApi } from "../../api/admin";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const SEVERITY_COLORS = {
  Major: { bg: "#FEE2E2", text: CRIMSON, border: "#FCA5A5" },
  Moderate: { bg: "#FEF3C7", text: AMBER, border: "#FCD34D" },
  Minor: { bg: "#EBF5F3", text: SAGE, border: "#B8DFD8" },
};

export const KnowledgeBaseAdmin = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);

  // Drug Interactions state
  const [interactions, setInteractions] = useState([]);
  const [interactionsLoading, setInteractionsLoading] = useState(true);
  const [interactionFilter, setInteractionFilter] = useState("");
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newInteraction, setNewInteraction] = useState({
    medicine_a: "",
    medicine_b: "",
    severity: "Major",
    evidence: "",
    clinical_reference: "",
  });

  // Unmatched Medicines state
  const [unmatched, setUnmatched] = useState([]);
  const [unmatchedLoading, setUnmatchedLoading] = useState(true);
  const [normDialogOpen, setNormDialogOpen] = useState(false);
  const [normTarget, setNormTarget] = useState({
    brand_name: "",
    generic_name: "",
    drug_class: "",
    system_of_medicine: "Allopathy",
  });

  const [feedback, setFeedback] = useState(null); // { type: 'success'|'error', msg: '' }
  const [submitting, setSubmitting] = useState(false);

  const fetchInteractions = useCallback(async () => {
    setInteractionsLoading(true);
    try {
      const data = await adminApi.getInteractions(0, 100);
      setInteractions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load interactions:", err);
      setFeedback({ type: "error", msg: "Failed to load drug interaction rules." });
    } finally {
      setInteractionsLoading(false);
    }
  }, []);

  const fetchUnmatched = useCallback(async () => {
    setUnmatchedLoading(true);
    try {
      const data = await adminApi.getUnmatchedMedicines();
      setUnmatched(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load unmatched medicines:", err);
      setFeedback({ type: "error", msg: "Failed to load unmatched medicines queue." });
    } finally {
      setUnmatchedLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInteractions();
    fetchUnmatched();
  }, [fetchInteractions, fetchUnmatched]);

  // Handle Add Interaction
  const handleAddInteraction = async (e) => {
    e.preventDefault();
    if (!newInteraction.medicine_a.trim() || !newInteraction.medicine_b.trim() || !newInteraction.evidence.trim()) {
      return;
    }
    setSubmitting(true);
    try {
      await adminApi.addInteraction({
        medicine_a: newInteraction.medicine_a.trim().toLowerCase(),
        medicine_b: newInteraction.medicine_b.trim().toLowerCase(),
        severity: newInteraction.severity,
        evidence: newInteraction.evidence.trim(),
        clinical_reference: newInteraction.clinical_reference.trim() || null,
      });
      setFeedback({ type: "success", msg: "Interaction rule added successfully to knowledge base." });
      setAddDialogOpen(false);
      setNewInteraction({ medicine_a: "", medicine_b: "", severity: "Major", evidence: "", clinical_reference: "" });
      fetchInteractions();
    } catch (err) {
      console.error("Add interaction error:", err);
      setFeedback({ type: "error", msg: err.response?.data?.detail || "Failed to add interaction rule." });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle Open Normalization Dialog
  const handleOpenNorm = (item) => {
    setNormTarget({
      brand_name: item.medicine_name,
      generic_name: "",
      drug_class: "",
      system_of_medicine: "Allopathy",
    });
    setNormDialogOpen(true);
  };

  // Handle Submit Normalization
  const handleAddNormalization = async (e) => {
    e.preventDefault();
    if (!normTarget.brand_name.trim() || !normTarget.generic_name.trim()) return;
    setSubmitting(true);
    try {
      await adminApi.addNormalization({
        brand_name: normTarget.brand_name.trim(),
        generic_name: normTarget.generic_name.trim(),
        drug_class: normTarget.drug_class.trim() || null,
        system_of_medicine: normTarget.system_of_medicine || null,
      });
      setFeedback({ type: "success", msg: `Mapped "${normTarget.brand_name}" → "${normTarget.generic_name}" in normalization database.` });
      setNormDialogOpen(false);
      fetchUnmatched();
    } catch (err) {
      console.error("Normalization error:", err);
      setFeedback({ type: "error", msg: err.response?.data?.detail || "Failed to add normalization mapping." });
    } finally {
      setSubmitting(false);
    }
  };

  const filteredInteractions = interactions.filter((item) => {
    const q = interactionFilter.toLowerCase();
    return (
      (item.medicine_a || "").toLowerCase().includes(q) ||
      (item.medicine_b || "").toLowerCase().includes(q) ||
      (item.evidence || "").toLowerCase().includes(q) ||
      (item.severity || "").toLowerCase().includes(q)
    );
  });

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
          <Typography variant="h5" sx={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: TEAL }}>
            Knowledge Base & Medicine Normalization
          </Typography>
          <Typography variant="body2" sx={{ color: "#5A677D", mt: 0.5 }}>
            Maintain cross-system drug-drug interactions and resolve unmapped brand names identified during document OCR.
          </Typography>
        </Container>
      </Box>

      {/* ── Main Content ────────────────────────────────────────────────────── */}
      <Container maxWidth="lg">
        {feedback && (
          <Alert severity={feedback.type} onClose={() => setFeedback(null)} sx={{ mb: 3 }}>
            {feedback.msg}
          </Alert>
        )}

        <Card sx={{ borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none", overflow: "hidden" }}>
          <Box sx={{ borderBottom: `1px solid ${BORDER}`, backgroundColor: "#FFFFFF", px: 2 }}>
            <Tabs
              value={tab}
              onChange={(_, v) => setTab(v)}
              sx={{
                "& .MuiTab-root": {
                  fontWeight: 700,
                  fontSize: "0.95rem",
                  textTransform: "none",
                  minHeight: 52,
                  color: "#5A677D",
                  "&.Mui-selected": { color: TEAL },
                },
                "& .MuiTabs-indicator": { backgroundColor: TEAL, height: 3 },
              }}
            >
              <Tab
                icon={<AutoStoriesIcon />}
                iconPosition="start"
                label={
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <span>Drug Interactions Rules</span>
                    <Chip label={interactions.length} size="small" sx={{ height: 20, fontSize: "0.75rem", backgroundColor: "#EBF5F3", color: TEAL, fontWeight: 700 }} />
                  </Box>
                }
              />
              <Tab
                icon={<AssignmentLateIcon />}
                iconPosition="start"
                label={
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <span>Unmatched Medicines Queue</span>
                    {unmatched.length > 0 && (
                      <Chip label={unmatched.length} size="small" sx={{ height: 20, fontSize: "0.75rem", backgroundColor: "#FEF3C7", color: AMBER, fontWeight: 700 }} />
                    )}
                  </Box>
                }
              />
            </Tabs>
          </Box>

          {/* ── Tab 0: Drug Interactions ────────────────────────────────────── */}
          {tab === 0 && (
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2, mb: 3 }}>
                <TextField
                  size="small"
                  placeholder="Search interactions by medicine or keyword..."
                  value={interactionFilter}
                  onChange={(e) => setInteractionFilter(e.target.value)}
                  sx={{ width: { xs: "100%", sm: 360 } }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon sx={{ color: "#718096" }} />
                      </InputAdornment>
                    ),
                  }}
                />
                <Box sx={{ display: "flex", gap: 1.5 }}>
                  <Button
                    startIcon={<RefreshIcon />}
                    onClick={fetchInteractions}
                    variant="outlined"
                    size="small"
                    sx={{ borderColor: BORDER, color: "#5A677D", fontWeight: 600 }}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setAddDialogOpen(true)}
                    sx={{ backgroundColor: TEAL, color: "#FFFFFF", fontWeight: 700, textTransform: "none", "&:hover": { backgroundColor: "#0B3844" } }}
                  >
                    Add Interaction Rule
                  </Button>
                </Box>
              </Box>

              {interactionsLoading ? (
                <Box sx={{ py: 2 }}>
                  <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
                  <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
                  <Skeleton variant="rectangular" height={52} sx={{ borderRadius: 2 }} />
                </Box>
              ) : filteredInteractions.length === 0 ? (
                <Box sx={{ textAlign: "center", py: 5, backgroundColor: "#F8FAFC", borderRadius: 2, border: `1px dashed ${BORDER}` }}>
                  <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                    No drug interaction rules match your filter
                  </Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table sx={{ minWidth: 800 }}>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, width: "20%" }}>Medicine Pair</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, width: "12%" }}>Severity</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, width: "48%" }}>Clinical Evidence</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL, width: "20%" }}>Reference</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredInteractions.map((row, idx) => {
                        const sevStyle = SEVERITY_COLORS[row.severity] || SEVERITY_COLORS.Moderate;
                        return (
                          <TableRow key={row.interaction_id || idx} sx={{ "&:hover": { backgroundColor: "#F7FAFC" } }}>
                            <TableCell sx={{ fontWeight: 700, color: "#2D3748" }}>
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <span style={{ textTransform: "capitalize" }}>{row.medicine_a}</span>
                                <span style={{ color: "#A0AEC0" }}>↔</span>
                                <span style={{ textTransform: "capitalize" }}>{row.medicine_b}</span>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={row.severity}
                                size="small"
                                sx={{
                                  backgroundColor: sevStyle.bg,
                                  color: sevStyle.text,
                                  border: `1px solid ${sevStyle.border}`,
                                  fontWeight: 800,
                                  fontSize: "0.75rem",
                                }}
                              />
                            </TableCell>
                            <TableCell sx={{ color: "#4A5568", fontSize: "0.9rem", lineHeight: 1.5 }}>
                              {row.evidence}
                            </TableCell>
                            <TableCell sx={{ color: "#718096", fontSize: "0.85rem", fontStyle: "italic" }}>
                              {row.clinical_reference || "—"}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {/* ── Tab 1: Unmatched Medicines Queue ────────────────────────────── */}
          {tab === 1 && (
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
                <Box>
                  <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700 }}>
                    Unmatched Medicines Awaiting Normalization
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D" }}>
                    These brand names were extracted from clinical prescriptions or reports but have no corresponding generic or AYUSH entry.
                  </Typography>
                </Box>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={fetchUnmatched}
                  variant="outlined"
                  size="small"
                  sx={{ borderColor: BORDER, color: "#5A677D", fontWeight: 600 }}
                >
                  Refresh Queue
                </Button>
              </Box>

              {unmatchedLoading ? (
                <Box sx={{ py: 2 }}>
                  <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
                  <Skeleton variant="rectangular" height={52} sx={{ borderRadius: 2 }} />
                </Box>
              ) : unmatched.length === 0 ? (
                <Box sx={{ textAlign: "center", py: 5, backgroundColor: "#F8FAFC", borderRadius: 2, border: `1px dashed ${BORDER}` }}>
                  <CheckCircleIcon sx={{ fontSize: 44, color: SAGE, mb: 1 }} />
                  <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                    No unmatched medicines pending curation
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#718096", mt: 0.5 }}>
                    All recognized brand names have active generic mappings in the normalization database.
                  </Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table sx={{ minWidth: 700 }}>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                        <TableCell sx={{ fontWeight: 700, color: TEAL }}>Extracted Brand Name</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL }}>Document Occurrences</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: TEAL }}>Sample Document ID</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700, color: TEAL }}>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {unmatched.map((item, idx) => (
                        <TableRow key={item.medicine_name || idx} sx={{ "&:hover": { backgroundColor: "#F7FAFC" } }}>
                          <TableCell sx={{ fontWeight: 700, color: TEAL }}>
                            {item.medicine_name}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`${item.occurrences} prescription${item.occurrences > 1 ? "s" : ""}`}
                              size="small"
                              sx={{ backgroundColor: "#FEF3C7", color: AMBER, fontWeight: 700 }}
                            />
                          </TableCell>
                          <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.8rem", color: "#718096" }}>
                            {item.sample_document_id ? item.sample_document_id.substring(0, 18) + "..." : "—"}
                          </TableCell>
                          <TableCell align="right">
                            <Button
                              variant="contained"
                              size="small"
                              startIcon={<AddIcon />}
                              onClick={() => handleOpenNorm(item)}
                              sx={{ backgroundColor: SAGE, color: "#FFFFFF", fontWeight: 700, textTransform: "none", "&:hover": { backgroundColor: "#246F5E" } }}
                            >
                              Add to Knowledge Base
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </Card>
      </Container>

      {/* ── Dialog: Add Drug Interaction ────────────────────────────────────── */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <Box component="form" onSubmit={handleAddInteraction}>
          <DialogTitle sx={{ color: TEAL, fontWeight: 700 }}>Add Drug Interaction Pair</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  required
                  label="Medicine A (Generic)"
                  placeholder="e.g. warfarin"
                  value={newInteraction.medicine_a}
                  onChange={(e) => setNewInteraction({ ...newInteraction, medicine_a: e.target.value })}
                  helperText="Lowercase standard generic name"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  required
                  label="Medicine B (Generic / AYUSH)"
                  placeholder="e.g. withania somnifera"
                  value={newInteraction.medicine_b}
                  onChange={(e) => setNewInteraction({ ...newInteraction, medicine_b: e.target.value })}
                  helperText="Lowercase standard generic name"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  required
                  label="Interaction Severity"
                  value={newInteraction.severity}
                  onChange={(e) => setNewInteraction({ ...newInteraction, severity: e.target.value })}
                >
                  <MenuItem value="Major">Major — Critical contraindication / severe toxicity</MenuItem>
                  <MenuItem value="Moderate">Moderate — Significant interaction requiring monitoring</MenuItem>
                  <MenuItem value="Minor">Minor — Mild pharmacokinetic effect</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  multiline
                  rows={3}
                  label="Clinical Evidence & Mechanism"
                  placeholder="Describe the pharmacological interaction, toxicity risks, or synergistic mechanism..."
                  value={newInteraction.evidence}
                  onChange={(e) => setNewInteraction({ ...newInteraction, evidence: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Clinical Reference / Journal Citation (Optional)"
                  placeholder="e.g. Lexicomp Drug Interactions; CCRAS Pharmacovigilance Manual 2022"
                  value={newInteraction.clinical_reference}
                  onChange={(e) => setNewInteraction({ ...newInteraction, clinical_reference: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setAddDialogOpen(false)} disabled={submitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting}
              sx={{ backgroundColor: TEAL, color: "#FFFFFF", fontWeight: 700, "&:hover": { backgroundColor: "#0B3844" } }}
            >
              {submitting ? "Saving..." : "Add Interaction"}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      {/* ── Dialog: Add Medicine Normalization ──────────────────────────────── */}
      <Dialog open={normDialogOpen} onClose={() => setNormDialogOpen(false)} maxWidth="sm" fullWidth>
        <Box component="form" onSubmit={handleAddNormalization}>
          <DialogTitle sx={{ color: TEAL, fontWeight: 700 }}>Map Unmatched Brand Name</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Brand Name"
                  value={normTarget.brand_name}
                  onChange={(e) => setNormTarget({ ...normTarget, brand_name: e.target.value })}
                  helperText="Exact brand name extracted from document"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Standard Generic / Active Ingredient"
                  placeholder="e.g. Paracetamol, Amoxicillin, Withania somnifera"
                  value={normTarget.generic_name}
                  onChange={(e) => setNormTarget({ ...normTarget, generic_name: e.target.value })}
                  helperText="Standard active molecule used for interaction screening"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Drug Class (Optional)"
                  placeholder="e.g. Analgesic, Beta Blocker"
                  value={normTarget.drug_class}
                  onChange={(e) => setNormTarget({ ...normTarget, drug_class: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="System of Medicine"
                  value={normTarget.system_of_medicine}
                  onChange={(e) => setNormTarget({ ...normTarget, system_of_medicine: e.target.value })}
                >
                  <MenuItem value="Allopathy">Allopathy</MenuItem>
                  <MenuItem value="Ayurveda">Ayurveda</MenuItem>
                  <MenuItem value="Homeopathy">Homeopathy</MenuItem>
                  <MenuItem value="Unani">Unani</MenuItem>
                  <MenuItem value="Siddha">Siddha</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setNormDialogOpen(false)} disabled={submitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting}
              sx={{ backgroundColor: SAGE, color: "#FFFFFF", fontWeight: 700, "&:hover": { backgroundColor: "#246F5E" } }}
            >
              {submitting ? "Saving..." : "Save Mapping"}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
};
