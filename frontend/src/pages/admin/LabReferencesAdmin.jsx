import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Container, Typography, Card, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, Skeleton, Chip, TextField, InputAdornment
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SearchIcon from "@mui/icons-material/Search";
import ScienceIcon from "@mui/icons-material/Science";
import RefreshIcon from "@mui/icons-material/Refresh";
import { adminApi } from "../../api/admin";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const BORDER = "#E2E8F0";

export const LabReferencesAdmin = () => {
  const navigate = useNavigate();
  const [references, setReferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState(null);

  const fetchReferences = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getLabReferences();
      setReferences(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load lab references:", err);
      setError("Unable to load laboratory reference intervals.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReferences();
  }, [fetchReferences]);

  const filtered = references.filter((item) =>
    (item.test_name || "").toLowerCase().includes(filter.toLowerCase()) ||
    (item.unit || "").toLowerCase().includes(filter.toLowerCase())
  );

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
                Laboratory Reference Intervals
              </Typography>
              <Typography variant="body2" sx={{ color: "#5A677D", mt: 0.5 }}>
                Standard normal physiological ranges used for longitudinal trend analysis, z-score flagging, and drug toxicity correlation.
              </Typography>
            </Box>
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchReferences}
              variant="outlined"
              size="small"
              sx={{ borderColor: BORDER, color: "#5A677D", fontWeight: 600 }}
            >
              Refresh Table
            </Button>
          </Box>
        </Container>
      </Box>

      {/* ── Content ─────────────────────────────────────────────────────────── */}
      <Container maxWidth="lg">
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${BORDER}`, boxShadow: "none" }}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2, mb: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <ScienceIcon sx={{ color: TEAL, fontSize: 26 }} />
              <Typography variant="h6" sx={{ color: TEAL, fontWeight: 700 }}>
                Reference Ranges ({references.length})
              </Typography>
            </Box>

            <TextField
              size="small"
              placeholder="Search by test name or unit..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              sx={{ width: { xs: "100%", sm: 320 } }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: "#718096" }} />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {loading ? (
            <Box sx={{ py: 2 }}>
              <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
              <Skeleton variant="rectangular" height={52} sx={{ mb: 1.5, borderRadius: 2 }} />
              <Skeleton variant="rectangular" height={52} sx={{ borderRadius: 2 }} />
            </Box>
          ) : filtered.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 5, backgroundColor: "#F8FAFC", borderRadius: 2, border: `1px dashed ${BORDER}` }}>
              <Typography variant="subtitle1" sx={{ color: "#4A5568", fontWeight: 600 }}>
                No laboratory tests found matching "{filter}"
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Biomarker / Test Name</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Lower Limit</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Upper Limit</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Standard Interval</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: TEAL }}>Measurement Unit</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filtered.map((item) => (
                    <TableRow key={item.reference_id} sx={{ "&:hover": { backgroundColor: "#F7FAFC" } }}>
                      <TableCell sx={{ fontWeight: 700, color: "#2D3748" }}>
                        {item.test_name}
                      </TableCell>
                      <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, color: "#4A5568" }}>
                        {item.lower_limit}
                      </TableCell>
                      <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, color: "#4A5568" }}>
                        {item.upper_limit}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${item.lower_limit} – ${item.upper_limit} ${item.unit}`}
                          size="small"
                          sx={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: "0.8rem",
                            backgroundColor: "#EBF5F3",
                            color: TEAL,
                            border: "1px solid #B8DFD8",
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: "#5A677D", fontWeight: 500 }}>
                        {item.unit}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Card>
      </Container>
    </Box>
  );
};
