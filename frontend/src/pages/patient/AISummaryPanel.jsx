import React, { useState, useEffect } from "react";
import {
  Box, Typography, Button, CircularProgress, Alert, Divider, Chip,
} from "@mui/material";
import SummarizeIcon from "@mui/icons-material/Summarize";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import ReactMarkdown from "react-markdown";
import { patientApi } from "../../api/patient";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const BORDER = "#E2E8F0";

export const AISummaryPanel = ({ patientId, initialData }) => {
  const [summary, setSummary] = useState(initialData || null);
  const [loading, setLoading] = useState(!initialData);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!patientId || initialData) return;
    (async () => {
      setLoading(true);
      try {
        const data = await patientApi.getSummary(patientId);
        setSummary(data);
      } catch (err) {
        if (!err.message?.includes("404")) setError(err.message);
      }
      setLoading(false);
    })();
  }, [patientId, initialData]);

  const handleGenerate = async (forceRefresh = false) => {
    setGenerating(true);
    setError(null);
    try {
      const data = await patientApi.generateSummary(patientId, forceRefresh);
      setSummary(data);
    } catch (err) {
      setError(err.message);
    }
    setGenerating(false);
  };

  if (loading) return <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}><CircularProgress sx={{ color: TEAL }} /></Box>;

  if (!summary) return (
    <Box sx={{ textAlign: "center", py: 8 }}>
      <SummarizeIcon sx={{ fontSize: 48, color: "#B2C5CC", mb: 2 }} />
      <Typography variant="h6" sx={{ color: TEAL, mb: 1 }}>Clinical Summary</Typography>
      <Typography variant="body2" sx={{ color: "#718096", maxWidth: 440, mx: "auto", mb: 3 }}>
        Generate an evidence-grounded AI clinical summary of your medication history, lab trends, and any flagged interactions.
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2, maxWidth: 440, mx: "auto" }}>{error}</Alert>}
      <Button
        variant="contained"
        onClick={() => handleGenerate(false)}
        disabled={generating}
        startIcon={generating ? <CircularProgress size={18} sx={{ color: "#fff" }} /> : <SummarizeIcon />}
        sx={{ backgroundColor: TEAL, "&:hover": { backgroundColor: "#165E71" }, py: 1.3, px: 3 }}
      >
        {generating ? "Generating Summary…" : "Generate Clinical Summary"}
      </Button>
    </Box>
  );

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2.5, flexWrap: "wrap", gap: 1.5 }}>
        <Box>
          <Typography variant="h6" sx={{ color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif", mb: 0.5 }}>
            AI Clinical Summary
          </Typography>
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            {summary.model_version && (
              <Chip label={summary.model_version} size="small" sx={{ fontFamily: "'JetBrains Mono',monospace", fontSize: "0.7rem", backgroundColor: "#EBF5F3", color: TEAL }} />
            )}
            {summary.generated_date && (
              <Typography variant="caption" sx={{ color: "#718096", alignSelf: "center" }}>
                Generated {new Date(summary.generated_date).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
              </Typography>
            )}
          </Box>
        </Box>
        <Button
          variant="outlined"
          startIcon={generating ? <CircularProgress size={16} /> : <AutorenewIcon />}
          onClick={() => handleGenerate(true)}
          disabled={generating}
          sx={{ color: TEAL, borderColor: TEAL, "&:hover": { borderColor: "#165E71", backgroundColor: "#EBF5F3" } }}
        >
          {generating ? "Regenerating…" : "Regenerate Summary"}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box
        sx={{
          p: 3, borderRadius: 2, border: `1px solid ${BORDER}`, backgroundColor: "#FAFBFC",
          "& h1,& h2,& h3": { fontFamily: "'Plus Jakarta Sans',sans-serif", color: TEAL, mt: 2, mb: 1 },
          "& p": { color: "#1A2230", lineHeight: 1.7, mb: 1.5, fontSize: "0.95rem" },
          "& strong": { color: "#1A2230", fontWeight: 700 },
          "& ul,& ol": { pl: 2.5, mb: 1.5 },
          "& li": { color: "#1A2230", mb: 0.5, lineHeight: 1.6 },
          "& hr": { borderColor: BORDER, my: 2 },
        }}
      >
        <ReactMarkdown>{summary.summary_text || "*No summary content available.*"}</ReactMarkdown>
      </Box>
    </Box>
  );
};
