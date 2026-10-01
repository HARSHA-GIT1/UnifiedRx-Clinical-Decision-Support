import React from "react";
import { Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Stack,
} from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { Navbar } from "../../components/common/Navbar";
import { Footer } from "../../components/common/Footer";

export const RegisterChoice = () => {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <Container maxWidth="md" sx={{ py: { xs: 6, md: 10 }, flex: 1 }}>
        <Box sx={{ textAlign: "center", mb: 6 }}>
          <Typography variant="caption" sx={{ fontWeight: 700, color: "#0F4C5C", textTransform: "uppercase", letterSpacing: "0.04em" }}>
            Get Started with UnifiedRx
          </Typography>
          <Typography variant="h2" sx={{ mt: 1, mb: 2 }}>
            Choose Your Account Type
          </Typography>
          <Typography variant="body1" sx={{ color: "#5A677D", maxWidth: 520, mx: "auto" }}>
            Select how you will be using the platform. Each portal is tailored with specialized clinical tools and privacy controls.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* Option 1: Patient */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                border: "2px solid #E2E8F0",
                transition: "all 0.2s ease-in-out",
                "&:hover": {
                  borderColor: "#0F4C5C",
                  boxShadow: "0 8px 24px rgba(15, 76, 92, 0.1)",
                },
              }}
            >
              <CardContent sx={{ p: 4, flex: 1, display: "flex", flexDirection: "column" }}>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2.5,
                    backgroundColor: "#EBF5F3",
                    color: "#0F4C5C",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 3,
                  }}
                >
                  <PersonIcon sx={{ fontSize: 32 }} />
                </Box>

                <Typography variant="h4" sx={{ fontSize: "1.45rem", mb: 1.5, color: "#0F4C5C" }}>
                  I am a Patient
                </Typography>
                <Typography variant="body2" sx={{ color: "#5A677D", mb: 3 }}>
                  Store all your Allopathic and Ayurvedic prescriptions in one place, receive automated drug interaction warnings, and track lab trends.
                </Typography>

                <Stack spacing={1.5} sx={{ mb: 4, flex: 1 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Instant unique <strong>Health ID (URX-P-XXXXXXXX)</strong>
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Unified longitudinal prescription timeline
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Automated cross-system interaction alerts
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      You control which doctors can view your records
                    </Typography>
                  </Box>
                </Stack>

                <Button
                  component={RouterLink}
                  to="/register/patient"
                  variant="contained"
                  color="primary"
                  size="large"
                  fullWidth
                  endIcon={<ArrowForwardIcon />}
                  sx={{ py: 1.4 }}
                >
                  Register as a Patient
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Option 2: Doctor */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                border: "2px solid #E2E8F0",
                transition: "all 0.2s ease-in-out",
                "&:hover": {
                  borderColor: "#2E8B75",
                  boxShadow: "0 8px 24px rgba(46, 139, 117, 0.12)",
                },
              }}
            >
              <CardContent sx={{ p: 4, flex: 1, display: "flex", flexDirection: "column" }}>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2.5,
                    backgroundColor: "#EBF5F3",
                    color: "#2E8B75",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 3,
                  }}
                >
                  <MedicalServicesIcon sx={{ fontSize: 32 }} />
                </Box>

                <Typography variant="h4" sx={{ fontSize: "1.45rem", mb: 1.5, color: "#0F4C5C" }}>
                  I am a Doctor / Clinician
                </Typography>
                <Typography variant="body2" sx={{ color: "#5A677D", mb: 3 }}>
                  Access patient records across care episodes, search by Health ID, view longitudinal lab trajectories, and review peer-reviewed interaction evidence.
                </Typography>

                <Stack spacing={1.5} sx={{ mb: 4, flex: 1 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Unique <strong>Professional ID (URX-D-XXXXXXXX)</strong>
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Search patient by Health ID & request access
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      View evidence-backed clinical summary briefings
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 18, color: "#2E8B75" }} />
                    <Typography variant="body2" sx={{ color: "#1A2230" }}>
                      Longitudinal lab drift charts with normal bands
                    </Typography>
                  </Box>
                </Stack>

                <Button
                  component={RouterLink}
                  to="/register/doctor"
                  variant="contained"
                  color="secondary"
                  size="large"
                  fullWidth
                  endIcon={<ArrowForwardIcon />}
                  sx={{ py: 1.4 }}
                >
                  Register as a Healthcare Professional
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ textAlign: "center", mt: 5 }}>
          <Typography variant="body2" sx={{ color: "#718096" }}>
            Already have an account?{" "}
            <RouterLink to="/login" style={{ color: "#0F4C5C", fontWeight: 600, textDecoration: "none" }}>
              Log in here
            </RouterLink>
          </Typography>
        </Box>
      </Container>

      <Footer />
    </Box>
  );
};
