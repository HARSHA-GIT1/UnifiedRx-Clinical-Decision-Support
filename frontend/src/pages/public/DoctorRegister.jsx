import React, { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Stack,
  Divider,
} from "@mui/material";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuth } from "../../context/AuthContext";
import { Navbar } from "../../components/common/Navbar";
import { Footer } from "../../components/common/Footer";
import { HealthIdBadge } from "../../components/common/HealthIdBadge";

export const DoctorRegister = () => {
  const { registerDoctor } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    license_number: "",
    specialization: "",
    hospital_affiliation: "",
    phone: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [registeredResult, setRegisteredResult] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (
      !formData.full_name ||
      !formData.license_number ||
      !formData.specialization ||
      !formData.hospital_affiliation ||
      !formData.email ||
      !formData.password ||
      !formData.phone
    ) {
      setError("Please fill in all clinical registration fields.");
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long with letters and numbers.");
      setLoading(false);
      return;
    }

    try {
      const res = await registerDoctor(formData);
      setRegisteredResult(res);
    } catch (err) {
      setError(err.message || "Clinician registration failed. Please verify your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <Container maxWidth="sm" sx={{ py: 8, flex: 1 }}>
        {!registeredResult ? (
          <Card sx={{ p: { xs: 2.5, sm: 4 }, borderRadius: 3, border: "1px solid #E2E8F0" }}>
            <Box sx={{ textAlign: "center", mb: 4 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: "#FDF3E7",
                  color: "#C07D32",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mb: 1.5,
                }}
              >
                <MedicalServicesIcon fontSize="medium" />
              </Box>
              <Typography variant="h4" sx={{ color: "#0F4C5C", mb: 1 }}>
                Healthcare Team Registration
              </Typography>
              <Typography variant="body2" sx={{ color: "#5A677D" }}>
                Register as a licensed medical doctor or clinical specialist.
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <Grid container spacing={2.5}>
                <Grid item xs={12}>
                  <TextField
                    label="Full Name & Title"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="e.g. Dr. Meera Iyer, MD"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Medical License / Registration No."
                    name="license_number"
                    value={formData.license_number}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="e.g. MCI-2018-9481"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Specialization / Department"
                    name="specialization"
                    value={formData.specialization}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="e.g. Internal Medicine"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    label="Hospital / Clinic Affiliation"
                    name="hospital_affiliation"
                    value={formData.hospital_affiliation}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="e.g. Apollo Multi-Specialty Hospital"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Contact Phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="+919876543210"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Official Email Address"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="dr.meera@hospital.org"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    label="Password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    fullWidth
                    required
                    helperText="Minimum 8 characters with at least one letter and one number."
                  />
                </Grid>
              </Grid>

              <Button
                type="submit"
                variant="contained"
                color="secondary"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 4, py: 1.5 }}
              >
                {loading ? <CircularProgress size={24} sx={{ color: "#FFFFFF" }} /> : "Register as Clinician"}
              </Button>

              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Typography variant="body2" sx={{ color: "#718096" }}>
                  Already registered?{" "}
                  <RouterLink to="/login" style={{ color: "#0F4C5C", fontWeight: 600, textDecoration: "none" }}>
                    Log in to portal
                  </RouterLink>
                </Typography>
              </Box>
            </Box>
          </Card>
        ) : (
          /* ── Post-Registration Doctor ID + Prominent Verification Notice ── */
          <Card
            sx={{
              p: { xs: 3, sm: 5 },
              borderRadius: 3,
              border: "2px solid #C07D32",
              boxShadow: "0 12px 32px rgba(192, 125, 50, 0.12)",
              textAlign: "center",
            }}
          >
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                backgroundColor: "#FDF3E7",
                color: "#C07D32",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 2,
              }}
            >
              <PendingActionsIcon sx={{ fontSize: 40 }} />
            </Box>

            <Typography variant="h3" sx={{ color: "#0F4C5C", mb: 1 }}>
              Clinician Account Created
            </Typography>
            <Typography variant="body1" sx={{ color: "#5A677D", mb: 3 }}>
              Welcome, <strong>{registeredResult.full_name}</strong>. Your professional account has been created and you are automatically signed in.
            </Typography>

            {/* Prominent Professional ID */}
            <Box
              sx={{
                p: 2.5,
                my: 2.5,
                borderRadius: 2.5,
                backgroundColor: "#F8FAFB",
                border: "1px dashed #C07D32",
              }}
            >
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#C07D32", textTransform: "uppercase", letterSpacing: "0.06em", display: "block", mb: 1 }}>
                Your Assigned Professional ID
              </Typography>
              <Box sx={{ my: 1 }}>
                <HealthIdBadge id={registeredResult.professional_code} label="" size="large" />
              </Box>
            </Box>

            {/* Prominent Verification Alert Banner (Mandatory per spec) */}
            <Alert
              severity="warning"
              icon={<PendingActionsIcon fontSize="inherit" />}
              sx={{
                my: 3,
                textAlign: "left",
                backgroundColor: "#FDF3E7",
                border: "1px solid #ECC94B",
                color: "#744210",
                "& .MuiAlert-icon": { color: "#C07D32" },
              }}
            >
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
                Account Under Verification
              </Typography>
              <Typography variant="body2" sx={{ fontSize: "0.88rem", lineHeight: 1.5 }}>
                Your medical registration is pending administrative credential verification. You can navigate your portal and familiarize yourself with the platform immediately; full clinical records access and patient consent requests will become active once your credentials are confirmed by our clinical governance team.
              </Typography>
            </Alert>

            <Button
              variant="contained"
              color="secondary"
              size="large"
              fullWidth
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate("/doctor/dashboard")}
              sx={{ py: 1.5, fontSize: "1.05rem" }}
            >
              Proceed to Clinician Portal
            </Button>
          </Card>
        )}
      </Container>

      <Footer />
    </Box>
  );
};
