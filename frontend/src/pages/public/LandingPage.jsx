import React from "react";
import { Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack,
  Divider,
} from "@mui/material";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import TimelineIcon from "@mui/icons-material/Timeline";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SummarizeIcon from "@mui/icons-material/Summarize";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import BiotechIcon from "@mui/icons-material/Biotech";
import { Navbar } from "../../components/common/Navbar";
import { Footer } from "../../components/common/Footer";

export const LandingPage = () => {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      {/* ── 1. Hero Section ─────────────────────────────────────────────── */}
      <Box
        sx={{
          backgroundColor: "#FFFFFF",
          borderBottom: "1px solid #E2E8F0",
          pt: { xs: 8, md: 12 },
          pb: { xs: 8, md: 12 },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={7}>
              <Box
                sx={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 1,
                  px: 1.8,
                  py: 0.6,
                  borderRadius: 20,
                  backgroundColor: "#EBF5F3",
                  color: "#0F4C5C",
                  mb: 3,
                }}
              >
                <BiotechIcon sx={{ fontSize: 16 }} />
                <Typography variant="caption" sx={{ fontWeight: 700, letterSpacing: "0.02em" }}>
                  EVIDENCE-GROUNDED CROSS-SYSTEM HEALTH PLATFORM
                </Typography>
              </Box>

              <Typography
                variant="h1"
                sx={{
                  fontSize: { xs: "2.4rem", md: "3.5rem" },
                  lineHeight: 1.15,
                  mb: 3,
                }}
              >
                Connecting Allopathy & AYUSH Therapies on One Longitudinal Record
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  fontSize: { xs: "1.05rem", md: "1.2rem" },
                  color: "#5A677D",
                  mb: 4.5,
                  lineHeight: 1.65,
                  maxWidth: 620,
                }}
              >
                Patients often consult multiple doctors across modern medicine and Ayurvedic traditions without a unified record. UnifiedRx automatically extracts your prescriptions, checks for cross-system drug interactions, tracks lab trends before they become critical, and gives your healthcare team a single, evidence-backed summary.
              </Typography>

              <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 4 }}>
                <Button
                  component={RouterLink}
                  to="/register/patient"
                  variant="contained"
                  color="primary"
                  size="large"
                  endIcon={<ArrowForwardIcon />}
                  sx={{ py: 1.5, px: 3, fontSize: "1rem" }}
                >
                  Register as a Patient
                </Button>
                <Button
                  component={RouterLink}
                  to="/register/doctor"
                  variant="outlined"
                  size="large"
                  sx={{
                    py: 1.5,
                    px: 3,
                    fontSize: "1rem",
                    borderColor: "#2E8B75",
                    color: "#2E8B75",
                    "&:hover": { borderColor: "#1E6554", backgroundColor: "#EBF5F3" },
                  }}
                >
                  Register as a Doctor / Healthcare Team
                </Button>
              </Stack>

              <Typography variant="body2" sx={{ color: "#718096" }}>
                Already registered?{" "}
                <RouterLink to="/login" style={{ color: "#0F4C5C", fontWeight: 600, textDecoration: "none" }}>
                  Log in to your portal
                </RouterLink>
              </Typography>
            </Grid>

            {/* Hero Right Visual Representation */}
            <Grid item xs={12} md={5}>
              <Card
                sx={{
                  p: 3.5,
                  borderRadius: 3,
                  backgroundColor: "#F8FAFB",
                  border: "1px solid #D6E4E2",
                  boxShadow: "0 12px 30px rgba(15, 76, 92, 0.08)",
                }}
              >
                <Typography variant="caption" sx={{ fontWeight: 700, color: "#0F4C5C", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  Active Longitudinal Stream Preview
                </Typography>

                <Box sx={{ mt: 2.5, display: "flex", flexDirection: "column", gap: 2 }}>
                  {/* Stream item 1 */}
                  <Box sx={{ p: 2, borderRadius: 2, backgroundColor: "#FFFFFF", borderLeft: "4px solid #0F4C5C", border: "1px solid #E2E8F0" }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#0F4C5C" }}>
                        Allopathy Prescription
                      </Typography>
                      <Typography variant="caption" sx={{ color: "#718096" }}>
                        Sep 06
                      </Typography>
                    </Stack>
                    <Typography variant="body2" sx={{ color: "#1A2230", fontWeight: 500 }}>
                      Augmentin 625mg (Amoxicillin / Clavulanate)
                    </Typography>
                  </Box>

                  {/* Stream item 2 */}
                  <Box sx={{ p: 2, borderRadius: 2, backgroundColor: "#FFFFFF", borderLeft: "4px solid #C07D32", border: "1px solid #E2E8F0" }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#C07D32" }}>
                        Ayurvedic Formulation
                      </Typography>
                      <Typography variant="caption" sx={{ color: "#718096" }}>
                        Sep 06
                      </Typography>
                    </Stack>
                    <Typography variant="body2" sx={{ color: "#1A2230", fontWeight: 500 }}>
                      Ashwagandha Churna (Withania somnifera)
                    </Typography>
                  </Box>

                  {/* Safety Cross-Check Badge */}
                  <Box sx={{ p: 2, borderRadius: 2, backgroundColor: "#EBF5F3", border: "1px solid #B8DFD8" }}>
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <VerifiedUserIcon sx={{ color: "#2E8B75", fontSize: 22 }} />
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#0F4C5C" }}>
                          Cross-System Safety Evaluated
                        </Typography>
                        <Typography variant="caption" sx={{ color: "#2E8B75", fontWeight: 600 }}>
                          Concurrent active window validated against Pharmacopoeia KB
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ── 2. The Problem Section ──────────────────────────────────────── */}
      <Box id="problem" sx={{ py: 10, backgroundColor: "#F6F8FA", borderBottom: "1px solid #E2E8F0" }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: "center", mb: 5 }}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: "#C07D32", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              The Clinical Challenge
            </Typography>
            <Typography variant="h2" sx={{ mt: 1, mb: 2.5 }}>
              Fragmented Care Across Medicine Systems Creates Blind Spots
            </Typography>
            <Typography variant="body1" sx={{ fontSize: "1.15rem", color: "#4A5568", lineHeight: 1.7 }}>
              Millions of patients concurrently take allopathic medications alongside traditional Ayurvedic remedies prescribed by different clinicians who have no visibility into each other's treatments. Without a shared longitudinal view, dangerous herb-drug pharmacokinetic interactions, duplicate therapeutic classes, and subtle metabolic shifts go unnoticed until complications arise.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* ── 3. What UnifiedRx Does (User-Language Features) ─────────────── */}
      <Box id="features" sx={{ py: 11, backgroundColor: "#FFFFFF", borderBottom: "1px solid #E2E8F0" }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: "center", mb: 8 }}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: "#0F4C5C", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Patient & Clinician Capabilities
            </Typography>
            <Typography variant="h2" sx={{ mt: 1, mb: 2 }}>
              What You Get with UnifiedRx
            </Typography>
            <Typography variant="body1" sx={{ color: "#5A677D", maxWidth: 640, mx: "auto" }}>
              A clinically rigorous decision support system designed to bring clarity, transparency, and safety to every consultation.
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {/* Feature 1 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: "100%", p: 2 }}>
                <CardContent>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#EBF5F3", color: "#0F4C5C", display: "flex", alignItems: "center", justifyContent: "center", mb: 2.5 }}>
                    <TimelineIcon />
                  </Box>
                  <Typography variant="h5" sx={{ fontSize: "1.15rem", mb: 1.5 }}>
                    Unified Health Timeline
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.6 }}>
                    Every prescription, herbal formulation, lab report, and clinical diagnosis merged into one clear, chronological ribbon.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Feature 2 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: "100%", p: 2 }}>
                <CardContent>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#FDF3E7", color: "#C07D32", display: "flex", alignItems: "center", justifyContent: "center", mb: 2.5 }}>
                    <WarningAmberIcon />
                  </Box>
                  <Typography variant="h5" sx={{ fontSize: "1.15rem", mb: 1.5 }}>
                    Cross-System Safety Checks
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.6 }}>
                    Immediate safety flags when an allopathic medicine and an Ayurvedic herb have documented adverse metabolic interactions.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Feature 3 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: "100%", p: 2 }}>
                <CardContent>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#EBF5F3", color: "#2E8B75", display: "flex", alignItems: "center", justifyContent: "center", mb: 2.5 }}>
                    <TrendingUpIcon />
                  </Box>
                  <Typography variant="h5" sx={{ fontSize: "1.15rem", mb: 1.5 }}>
                    Early Lab Trend Warnings
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.6 }}>
                    Statistical drift tracking flags when your organ function or blood counts are trending anomalously before they breach standard reference boundaries.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Feature 4 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: "100%", p: 2 }}>
                <CardContent>
                  <Box sx={{ width: 44, height: 44, borderRadius: 2, backgroundColor: "#F3E8FF", color: "#6B21A8", display: "flex", alignItems: "center", justifyContent: "center", mb: 2.5 }}>
                    <SummarizeIcon />
                  </Box>
                  <Typography variant="h5" sx={{ fontSize: "1.15rem", mb: 1.5 }}>
                    Evidence-Backed Briefings
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.6 }}>
                    Grounded AI clinical summaries prepared for your doctor, detailing concurrent therapies, flagged associations, and peer-reviewed safety evidence.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ── 4. How It Works (Numbered Sequential Steps) ─────────────────── */}
      <Box id="how-it-works" sx={{ py: 11, backgroundColor: "#F6F8FA", borderBottom: "1px solid #E2E8F0" }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: "center", mb: 8 }}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: "#2E8B75", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Simple 4-Step Clinical Process
            </Typography>
            <Typography variant="h2" sx={{ mt: 1, mb: 2 }}>
              How UnifiedRx Works
            </Typography>
            <Typography variant="body1" sx={{ color: "#5A677D", maxWidth: 640, mx: "auto" }}>
              From physical prescription photo to evidence-backed decision support in minutes.
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {[
              {
                step: "01",
                title: "Upload Prescriptions & Reports",
                desc: "Upload PDFs or scanned prescription slips from your Allopathic or Ayurvedic consultations. Files are processed locally under strict session security.",
              },
              {
                step: "02",
                title: "Extract & Standardize Ingredients",
                desc: "Medical NLP extracts brand names, standardized active ingredients, botanical names, dosage intervals, and laboratory biomarker values.",
              },
              {
                step: "03",
                title: "Evaluate Safety & Temporal Links",
                desc: "The cross-system engine scans the active co-prescription window against the interaction knowledge base and evaluates longitudinal biomarker trends.",
              },
              {
                step: "04",
                title: "Physician Reviews Grounded Summary",
                desc: "Your doctor enters your Health ID, reviews the unified timeline and reference-cited warnings, and makes informed clinical adjustments.",
              },
            ].map((item) => (
              <Grid item xs={12} sm={6} md={3} key={item.step}>
                <Box
                  sx={{
                    p: 3.5,
                    borderRadius: 3,
                    backgroundColor: "#FFFFFF",
                    border: "1px solid #E2E8F0",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{
                      fontSize: "2rem",
                      fontWeight: 800,
                      color: "#2E8B75",
                      fontFamily: "'JetBrains Mono', monospace",
                      mb: 2,
                    }}
                  >
                    {item.step}
                  </Typography>
                  <Typography variant="h6" sx={{ fontSize: "1.1rem", mb: 1.5, color: "#0F4C5C" }}>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", lineHeight: 1.6 }}>
                    {item.desc}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ── 5. Trust & Credibility Section ─────────────────────────────── */}
      <Box id="credibility" sx={{ py: 11, backgroundColor: "#FFFFFF" }}>
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#0F4C5C", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                Rigorous Clinical Grounding
              </Typography>
              <Typography variant="h2" sx={{ mt: 1, mb: 3 }}>
                Evidence-Based Citations on Every Alert
              </Typography>
              <Typography variant="body1" sx={{ color: "#5A677D", mb: 3.5, lineHeight: 1.7 }}>
                Unlike conversational AI tools that speculate on diagnoses, UnifiedRx strictly enforces zero-hallucination decision support. Every interaction alert is grounded in peer-reviewed clinical citations (Indian Pharmacopoeia 2022, FDA communications, Lancet clinical pharmacology studies).
              </Typography>

              <Stack spacing={2}>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>
                  <CheckCircleOutlineIcon sx={{ color: "#2E8B75", mt: 0.3 }} />
                  <Typography variant="body2" sx={{ color: "#1A2230" }}>
                    <strong>Peer-Reviewed Sources:</strong> Full academic citations and pharmacological mechanisms shown inline with every alert.
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>
                  <CheckCircleOutlineIcon sx={{ color: "#2E8B75", mt: 0.3 }} />
                  <Typography variant="body2" sx={{ color: "#1A2230" }}>
                    <strong>Non-Causal Decision Support:</strong> Temporal associations explicitly framed as correlations for physician review, never autonomous diagnosis.
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>
                  <CheckCircleOutlineIcon sx={{ color: "#2E8B75", mt: 0.3 }} />
                  <Typography variant="body2" sx={{ color: "#1A2230" }}>
                    <strong>Explicit Consent & Access Control:</strong> Doctors can only review your records after you explicitly share your Health ID and approve access.
                  </Typography>
                </Box>
              </Stack>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ p: 4, borderRadius: 3, backgroundColor: "#F8FAFB", border: "1px solid #D6E4E2" }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "#0F4C5C", mb: 2 }}>
                  Sample Real-World Cross-System Interaction
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: "#C07D32", fontWeight: 700, textTransform: "uppercase" }}>
                    Moderate Interaction · Co-Prescription Alert
                  </Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mt: 0.5 }}>
                    Amoxicillin-Clavulanate + Commiphora Mukul (Guggulu)
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#5A677D", mt: 1 }}>
                    Guggulsterones are potent inducers of hepatic CYP3A4 and P-glycoprotein. Concurrent administration may reduce systemic bioavailability of co-prescribed aminopenicillins.
                  </Typography>
                  <Typography variant="caption" sx={{ display: "block", color: "#0F4C5C", fontWeight: 600, mt: 1.5 }}>
                    Clinical Reference: Dandekar et al. J Ethnopharmacol 1992; IP 2022
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ── 6. Bottom Call to Action ───────────────────────────────────── */}
      <Box sx={{ py: 8, backgroundColor: "#0F4C5C", color: "#FFFFFF", textAlign: "center" }}>
        <Container maxWidth="md">
          <Typography variant="h2" sx={{ color: "#FFFFFF", mb: 2 }}>
            Take Control of Your Cross-System Health Record
          </Typography>
          <Typography variant="body1" sx={{ color: "#DCEEEA", mb: 4, maxWidth: 560, mx: "auto" }}>
            Join thousands of patients and clinicians building safe, evidence-grounded continuity of care across all healing traditions.
          </Typography>
          <Button
            component={RouterLink}
            to="/register"
            variant="contained"
            size="large"
            sx={{
              backgroundColor: "#2E8B75",
              color: "#FFFFFF",
              px: 4,
              py: 1.5,
              fontSize: "1.05rem",
              "&:hover": { backgroundColor: "#267764" },
            }}
          >
            Create Your Account Today
          </Button>
        </Container>
      </Box>

      <Footer />
    </Box>
  );
};
