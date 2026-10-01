import React, { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Stack,
  Divider,
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuth } from "../../context/AuthContext";
import { Navbar } from "../../components/common/Navbar";
import { Footer } from "../../components/common/Footer";

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await login(email, password);
      // Route based on role
      if (res.role === "patient") {
        navigate("/patient/dashboard");
      } else if (res.role === "healthcare_professional") {
        navigate("/doctor/dashboard");
      } else if (res.role === "admin") {
        navigate("/admin/dashboard");
      } else {
        navigate("/");
      }
    } catch (err) {
      setError(err.message || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <Container maxWidth="xs" sx={{ py: 10, flex: 1, display: "flex", alignItems: "center" }}>
        <Card sx={{ p: 4, width: "100%", borderRadius: 3, border: "1px solid #E2E8F0" }}>
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
              <LockOutlinedIcon fontSize="medium" />
            </Box>
            <Typography variant="h4" sx={{ color: "#0F4C5C", mb: 0.8 }}>
              Portal Sign In
            </Typography>
            <Typography variant="body2" sx={{ color: "#5A677D" }}>
              Access your patient health record or clinician portal.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              <TextField
                label="Registered Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
                required
                autoComplete="email"
                placeholder="name@example.com"
              />

              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                required
                autoComplete="current-password"
              />

              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={loading}
                endIcon={!loading && <ArrowForwardIcon />}
                sx={{ py: 1.4, mt: 1 }}
              >
                {loading ? <CircularProgress size={24} sx={{ color: "#FFFFFF" }} /> : "Sign In to Portal"}
              </Button>
            </Stack>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ textAlign: "center" }}>
              <Typography variant="body2" sx={{ color: "#718096" }}>
                New to UnifiedRx?{" "}
                <RouterLink to="/register" style={{ color: "#0F4C5C", fontWeight: 600, textDecoration: "none" }}>
                  Create an account
                </RouterLink>
              </Typography>
            </Box>
          </Box>
        </Card>
      </Container>

      <Footer />
    </Box>
  );
};
