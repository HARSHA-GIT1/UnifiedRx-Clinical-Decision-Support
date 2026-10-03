import React, { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  Stack,
  Divider,
} from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuth } from "../../context/AuthContext";
import { Navbar } from "../../components/common/Navbar";
import { Footer } from "../../components/common/Footer";
import { HealthIdBadge } from "../../components/common/HealthIdBadge";

export const PatientRegister = () => {
  const { registerPatient } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    date_of_birth: "",
    gender: "Male",
    phone: "",
    email: "",
    password: "",
    blood_group: "O+",
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

    // Validation
    if (!formData.full_name || !formData.date_of_birth || !formData.email || !formData.password || !formData.phone) {
      setError("Please fill in all required fields.");
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long and contain at least one letter and one number.");
      setLoading(false);
      return;
    }

    try {
      const res = await registerPatient(formData);
      setRegisteredResult(res);
    } catch (err) {
      setError(err.message || "Registration failed. Please check your inputs.");
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
                  backgroundColor: "#EBF5F3",
                  color: "#0F4C5C",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mb: 1.5,
                }}
              >
                <PersonIcon fontSize="medium" />
              </Box>
              <Typography variant="h4" sx={{ color: "#0F4C5C", mb: 1 }}>
                Patient Registration
              </Typography>
              <Typography variant="body2" sx={{ color: "#5A677D" }}>
                Create your patient profile to receive your auto-generated Health ID.
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
                            <Grid container spacing={3} alignItems="flex-start">
                <Grid item xs={12}>
                  <TextField
                    label="Full Name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="e.g. Aarav Sharma"
                    slotProps={{ inputLabel: { shrink: true } }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Date of Birth"
                    name="date_of_birth"
                    type={formData.date_of_birth ? "date" : "text"}
                    onFocus={(e) => (e.target.type = "date")}
                    onBlur={(e) => {
                      if (!formData.date_of_birth) e.target.type = "text";
                    }}
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    fullWidth
                    required
                    sx={{
                      '& input[type="date"]::-webkit-calendar-picker-indicator': {
                        cursor: 'pointer',
                        mr: 1
                      }
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Gender"
                    name="gender"
                    select
                    value={formData.gender}
                    onChange={handleChange}
                    fullWidth
                    required
                    slotProps={{ inputLabel: { shrink: true } }}
                  >
                    <MenuItem value="Male">Male</MenuItem>
                    <MenuItem value="Female">Female</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
                    <MenuItem value="Prefer not to say">Prefer not to say</MenuItem>
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Phone Number"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="+919876543210"
                    slotProps={{ inputLabel: { shrink: true } }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Blood Group"
                    name="blood_group"
                    select
                    value={formData.blood_group}
                    onChange={handleChange}
                    fullWidth
                    slotProps={{ inputLabel: { shrink: true } }}
                  >
                    <MenuItem value=""><em>None</em></MenuItem>
                    {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map((bg) => (
                      <MenuItem key={bg} value={bg}>
                        {bg}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    label="Email Address"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    fullWidth
                    required
                    placeholder="aarav@example.com"
                    slotProps={{ inputLabel: { shrink: true } }}
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
                    placeholder="Min. 8 characters"
                    helperText="Must include at least one letter and one number."
                    slotProps={{ inputLabel: { shrink: true } }}
                  />
                </Grid>
              </Grid>

              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 4, py: 1.5 }}
              >
                {loading ? <CircularProgress size={24} sx={{ color: "#FFFFFF" }} /> : "Register as Patient"}
              </Button>

              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Typography variant="body2" sx={{ color: "#718096" }}>
                  Already registered?{" "}
                  <RouterLink to="/login" style={{ color: "#0F4C5C", fontWeight: 600, textDecoration: "none" }}>
                    Log in here
                  </RouterLink>
                </Typography>
              </Box>
            </Box>
          </Card>
        ) : (
          /* ── Post-Registration Prominent Health ID Display ───────────── */
          <Card
            sx={{
              p: { xs: 3, sm: 5 },
              borderRadius: 3,
              border: "2px solid #2E8B75",
              boxShadow: "0 12px 32px rgba(46, 139, 117, 0.12)",
              textAlign: "center",
            }}
          >
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                backgroundColor: "#EBF5F3",
                color: "#2E8B75",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 2,
              }}
            >
              <CheckCircleOutlineIcon sx={{ fontSize: 40 }} />
            </Box>

            <Typography variant="h3" sx={{ color: "#0F4C5C", mb: 1 }}>
              Registration Successful!
            </Typography>
            <Typography variant="body1" sx={{ color: "#5A677D", mb: 3 }}>
              Welcome, <strong>{registeredResult.full_name}</strong>. Your account has been initialized and you are automatically signed in.
            </Typography>

            {/* Prominent Health ID Box */}
            <Box
              sx={{
                p: 3,
                my: 3,
                borderRadius: 2.5,
                backgroundColor: "#F8FAFB",
                border: "1px dashed #2E8B75",
              }}
            >
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#2E8B75", textTransform: "uppercase", letterSpacing: "0.06em", display: "block", mb: 1 }}>
                Your Permanent Patient Health ID
              </Typography>
              <Box sx={{ my: 1.5 }}>
                <HealthIdBadge id={registeredResult.health_code} label="" size="large" />
              </Box>
              <Typography variant="caption" sx={{ color: "#718096", display: "block", maxWidth: 440, mx: "auto" }}>
                Doctors require this Health ID to request access to your prescriptions and lab history. You will approve or reject each request from your dashboard.
              </Typography>
            </Box>

            <Button
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate("/patient/dashboard")}
              sx={{ py: 1.5, fontSize: "1.05rem" }}
            >
              Go to Patient Dashboard
            </Button>
          </Card>
        )}
      </Container>

      <Footer />
    </Box>
  );
};



