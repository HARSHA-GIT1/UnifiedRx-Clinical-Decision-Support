import React from "react";
import { Box, Container, Typography, Grid, Link, Divider } from "@mui/material";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import SecurityIcon from "@mui/icons-material/Security";

export const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: "#FFFFFF",
        borderTop: "1px solid #E2E8F0",
        pt: 6,
        pb: 5,
        mt: "auto",
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} sx={{ mb: 4 }}>
          {/* Col 1: Platform Overview */}
          <Grid item xs={12} md={5}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
              <Box
                sx={{
                  width: 28,
                  height: 28,
                  borderRadius: 1.5,
                  backgroundColor: "#0F4C5C",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#FFFFFF",
                }}
              >
                <LocalHospitalIcon sx={{ fontSize: 16 }} />
              </Box>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 700,
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  color: "#0F4C5C",
                }}
              >
                UnifiedRx
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: "#5A677D", maxWidth: 380, mb: 2 }}>
              An evidence-driven clinical decision support platform bridging Allopathy and AYUSH systems through longitudinal health timelines, cross-system drug safety checks, and grounded clinical intelligence.
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, color: "#2E8B75" }}>
              <SecurityIcon fontSize="small" />
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                In-Memory Session Security · Deterministic Evidence Base
              </Typography>
            </Box>
          </Grid>

          {/* Col 2: Platform Links */}
          <Grid item xs={6} md={3}>
            <Typography
              variant="subtitle2"
              sx={{ fontWeight: 700, color: "#1A2230", mb: 2, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Platform
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              <Link href="/#problem" underline="hover" color="text.secondary" variant="body2">
                Why UnifiedRx
              </Link>
              <Link href="/#features" underline="hover" color="text.secondary" variant="body2">
                Clinical Safety Features
              </Link>
              <Link href="/#how-it-works" underline="hover" color="text.secondary" variant="body2">
                How It Works
              </Link>
              <Link href="/#credibility" underline="hover" color="text.secondary" variant="body2">
                Evidence Standards
              </Link>
            </Box>
          </Grid>

          {/* Col 3: Access & Portals */}
          <Grid item xs={6} md={4}>
            <Typography
              variant="subtitle2"
              sx={{ fontWeight: 700, color: "#1A2230", mb: 2, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Access Portals
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              <Link href="/register/patient" underline="hover" color="text.secondary" variant="body2">
                Patient Self-Registration (Health ID)
              </Link>
              <Link href="/register/doctor" underline="hover" color="text.secondary" variant="body2">
                Doctor / Clinical Team Registration
              </Link>
              <Link href="/login" underline="hover" color="text.secondary" variant="body2">
                Patient & Clinician Portal Login
              </Link>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* Clinical Disclaimer & Data Privacy */}
        <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, justifyContent: "space-between", alignItems: { xs: "flex-start", sm: "center" }, gap: 2 }}>
          <Typography variant="caption" sx={{ color: "#718096", maxWidth: 760 }}>
            <strong>Clinical Decision Support Notice:</strong> UnifiedRx provides algorithmic correlation alerts and reference-backed interaction warnings to assist licensed healthcare professionals. It does not provide autonomous medical diagnoses or prescription modifications. Always consult your treating physician before altering any therapeutic regimen.
          </Typography>
          <Typography variant="caption" sx={{ color: "#A0AEC0", whiteSpace: "nowrap" }}>
            © {new Date().getFullYear()} UnifiedRx. Capstone Research.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};
