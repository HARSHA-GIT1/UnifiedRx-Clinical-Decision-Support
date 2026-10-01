import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
} from "@mui/material";
import AdminPanelSettingsOutlinedIcon from "@mui/icons-material/AdminPanelSettingsOutlined";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuth } from "../../context/AuthContext";

/**
 * AdminLogin — accessible at /admin/login.
 * Intentionally NOT linked from the public Navbar or any public-facing page.
 * Restricted to system administrators only.
 */
export const AdminLogin = () => {
  const { adminLogin } = useAuth();
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
      await adminLogin(email, password);
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.message || "Invalid administrator credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #09333E 0%, #0F4C5C 60%, #165E71 100%)",
      }}
    >
      <Container maxWidth="xs">
        <Card sx={{ p: 5, borderRadius: 3, border: "1px solid #D6E4E2" }}>
          <Box sx={{ textAlign: "center", mb: 4 }}>
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                backgroundColor: "#EBF5F3",
                color: "#0F4C5C",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 1.5,
              }}
            >
              <AdminPanelSettingsOutlinedIcon fontSize="medium" />
            </Box>
            <Typography variant="h5" sx={{ color: "#0F4C5C", fontWeight: 700, mb: 0.5 }}>
              Administrator Access
            </Typography>
            <Typography variant="body2" sx={{ color: "#5A677D" }}>
              This portal is restricted to UnifiedRx system administrators.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} id="admin-login-form">
            <Stack spacing={2.5}>
              <TextField
                id="admin-email"
                label="Administrator Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
                required
                autoComplete="email"
              />

              <TextField
                id="admin-password"
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                required
                autoComplete="current-password"
              />

              <Button
                id="admin-login-submit"
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={loading}
                endIcon={!loading && <ArrowForwardIcon />}
                sx={{ py: 1.4, mt: 1 }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: "#FFFFFF" }} />
                ) : (
                  "Sign In as Administrator"
                )}
              </Button>
            </Stack>
          </Box>
        </Card>

        <Typography
          variant="caption"
          sx={{ display: "block", textAlign: "center", color: "rgba(255,255,255,0.45)", mt: 3 }}
        >
          UnifiedRx — Restricted System Access
        </Typography>
      </Container>
    </Box>
  );
};
