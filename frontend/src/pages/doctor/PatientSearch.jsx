import React, { useState } from "react";
import {
  Box, Card, TextField, Button, Typography, Alert,
  CircularProgress, InputAdornment
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import SendIcon from "@mui/icons-material/Send";
import { accessApi } from "../../api/access";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const BORDER = "#E2E8F0";

export const PatientSearch = ({ disabled = false, onRequestSuccess }) => {
  const [healthCode, setHealthCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success'|'info'|'warning'|'error', message: string }

  const handleRequest = async (e) => {
    e.preventDefault();
    const code = healthCode.trim().toUpperCase();
    if (!code) return;

    setLoading(true);
    setFeedback(null);

    try {
      const res = await accessApi.requestAccess(code);
      setFeedback({
        type: "success",
        message: `Access request sent to ${code}. The patient will receive a notification to approve your request.`,
      });
      setHealthCode("");
      if (onRequestSuccess) {
        onRequestSuccess(res);
      }
    } catch (err) {
      const status = err.status || err.response?.status;
      const detail = typeof err.detail === "string" ? err.detail : (typeof err.response?.data?.detail === "string" ? err.response.data.detail : err.message || "");

      if (status === 409) {
        if (detail.toLowerCase().includes("pending")) {
          setFeedback({
            type: "warning",
            message: "You already have a pending access request for this patient.",
          });
        } else if (detail.toLowerCase().includes("approved")) {
          setFeedback({
            type: "info",
            message: "You already have approved access to this patient — they appear in your My Patients list.",
          });
        } else {
          setFeedback({
            type: "warning",
            message: detail || "You already have a request or access for this patient.",
          });
        }
      } else if (status === 404) {
        setFeedback({
          type: "error",
          message: detail || `No patient found with Health ID "${code}". Please check the code and try again.`,
        });
      } else {
        setFeedback({
          type: "error",
          message: detail || "Failed to submit access request. Please verify your credentials and try again.",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      sx={{
        p: 3,
        borderRadius: 3,
        border: `1px solid ${BORDER}`,
        boxShadow: "none",
        backgroundColor: "#FFFFFF",
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700, mb: 0.5 }}>
          Request Patient Access
        </Typography>
        <Typography variant="body2" sx={{ color: "#5A677D" }}>
          Enter the patient's unique Health ID to send a secure consent request. Access is granted once the patient approves.
        </Typography>
      </Box>

      <Box
        component="form"
        onSubmit={handleRequest}
        sx={{
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          gap: 1.5,
          alignItems: "stretch",
        }}
      >
        <TextField
          fullWidth
          size="medium"
          label="Enter Patient Health ID"
          placeholder="e.g. URX-P-GTKUF8DF"
          value={healthCode}
          onChange={(e) => setHealthCode(e.target.value.toUpperCase())}
          disabled={disabled || loading}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: "#718096" }} />
                </InputAdornment>
              ),
              sx: {
                fontFamily: "'JetBrains Mono', monospace",
                fontWeight: 600,
                letterSpacing: "0.05em",
              },
            },
          }}
          helperText="Format: URX-P-XXXXXXXX (exact match)"
        />
        <Button
          type="submit"
          variant="contained"
          disabled={disabled || loading || !healthCode.trim()}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
          sx={{
            px: 3.5,
            py: { xs: 1.5, sm: 0 },
            backgroundColor: TEAL,
            color: "#FFFFFF",
            fontWeight: 700,
            whiteSpace: "nowrap",
            height: 56,
            "&:hover": {
              backgroundColor: "#0B3844",
            },
            "&:disabled": {
              backgroundColor: "#CBD5E0",
              color: "#718096",
            },
          }}
        >
          {loading ? "Sending..." : "Request Access"}
        </Button>
      </Box>

      {feedback && (
        <Alert
          severity={feedback.type}
          onClose={() => setFeedback(null)}
          sx={{
            mt: 2.5,
            borderRadius: 2,
            fontWeight: 500,
            "& .MuiAlert-message": {
              fontSize: "0.95rem",
              lineHeight: 1.5,
            },
          }}
        >
          {feedback.message}
        </Alert>
      )}
    </Card>
  );
};
