import os
base = r"E:\Capstone\Projectwork\frontend\src\pages\patient"

# ── Screen 4: Lab Trends ───────────────────────────────────────────────────
lab_trends = r'''import React, { useState, useEffect } from "react";
import {
  Box, Typography, Card, Grid, Chip, CircularProgress,
} from "@mui/material";
import ScienceIcon from "@mui/icons-material/Science";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceArea, ReferenceLine, Dot,
} from "recharts";
import { patientApi } from "../../api/patient";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const CustomDot = (props) => {
  const { cx, cy, payload } = props;
  if (!payload) return null;
  const outOfRange = payload.out_of_range;
  return (
    <circle cx={cx} cy={cy} r={5} fill={outOfRange ? CRIMSON : SAGE} stroke="#fff" strokeWidth={2} />
  );
};

const TrendCard = ({ trend }) => {
  const chartData = [{ date: trend.latest_date, value: trend.latest_value, out_of_range: trend.out_of_range }];
  const hasRef = trend.reference_lower !== null && trend.reference_upper !== null;

  return (
    <Card sx={{ p: 2.5, border: `1px solid ${trend.flagged ? "#FEB2B2" : BORDER}`, borderRadius: 3, boxShadow: "none", height: "100%" }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: TEAL, mb: 0.25 }}>
            {trend.test_name}
          </Typography>
          <Typography variant="h5" sx={{ fontFamily: "'JetBrains Mono', monospace", color: trend.out_of_range ? CRIMSON : SAGE, fontWeight: 700 }}>
            {trend.latest_value} <Typography component="span" variant="caption" sx={{ color: "#718096" }}>{trend.unit || ""}</Typography>
          </Typography>
        </Box>
        <Box sx={{ textAlign: "right" }}>
          <Chip
            label={trend.out_of_range ? "Out of Range" : "Normal"}
            size="small"
            sx={{ backgroundColor: trend.out_of_range ? "#FED7D7" : "#E6F4F1", color: trend.out_of_range ? CRIMSON : SAGE, fontWeight: 700, mb: 0.5 }}
          />
          {hasRef && (
            <Typography variant="caption" sx={{ display: "block", color: "#718096" }}>
              Ref: {trend.reference_lower}–{trend.reference_upper} {trend.reference_unit || ""}
            </Typography>
          )}
        </Box>
      </Box>

      {/* Mini sparkline */}
      <Box sx={{ height: 80, mb: 1.5 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={BORDER} />
            {hasRef && (
              <ReferenceArea y1={trend.reference_lower} y2={trend.reference_upper} fill={`${SAGE}15`} />
            )}
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#718096" }} />
            <YAxis tick={{ fontSize: 10, fill: "#718096" }} domain={["auto", "auto"]} />
            <Tooltip
              contentStyle={{ fontSize: "0.78rem", border: `1px solid ${BORDER}`, borderRadius: 6 }}
              formatter={(val) => [val, trend.test_name]}
            />
            <Line type="monotone" dataKey="value" stroke={trend.out_of_range ? CRIMSON : SAGE} strokeWidth={2} dot={<CustomDot />} />
          </LineChart>
        </ResponsiveContainer>
      </Box>

      {/* Trend status */}
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", pt: 1, borderTop: `1px solid ${BORDER}` }}>
        <Typography variant="caption" sx={{ color: "#718096" }}>
          {trend.readings_count} reading{trend.readings_count !== 1 ? "s" : ""}
        </Typography>
        <Typography variant="caption" sx={{ color: trend.trend_status === "abnormal_trend" ? CRIMSON : trend.trend_status === "stable" ? SAGE : "#718096", fontWeight: 600 }}>
          {trend.trend_status === "insufficient_data" ? "Insufficient data for trend analysis" :
           trend.trend_status === "abnormal_trend" ? `Abnormal trend (z = ${trend.z_score})` :
           `Stable (z = ${trend.z_score ?? "—"})`}
        </Typography>
      </Box>
    </Card>
  );
};

export const LabTrendsPanel = ({ patientId, initialData }) => {
  const [trends, setTrends] = useState(initialData || []);
  const [loading, setLoading] = useState(!initialData || initialData.length === 0);

  useEffect(() => {
    if (!patientId) return;
    (async () => {
      setLoading(true);
      try {
        const data = await patientApi.getLabTrends(patientId);
        setTrends(data);
      } catch (_) {}
      setLoading(false);
    })();
  }, [patientId]);

  if (loading) return <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}><CircularProgress sx={{ color: TEAL }} /></Box>;

  if (trends.length === 0) return (
    <Box sx={{ textAlign: "center", py: 8 }}>
      <ScienceIcon sx={{ fontSize: 48, color: "#B2C5CC", mb: 2 }} />
      <Typography variant="h6" sx={{ color: TEAL, mb: 1 }}>No Lab Trends Yet</Typography>
      <Typography variant="body2" sx={{ color: "#718096", maxWidth: 400, mx: "auto" }}>
        No lab reports uploaded yet — upload a lab report to see your biomarker trends and reference range comparisons here.
      </Typography>
    </Box>
  );

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 0.5, color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>Lab Biomarker Trends</Typography>
      <Typography variant="caption" sx={{ color: "#718096", display: "block", mb: 3 }}>
        {trends.length} distinct test{trends.length !== 1 ? "s" : ""} tracked · Reference bands shown in green
      </Typography>
      <Grid container spacing={2.5}>
        {trends.map((t) => (
          <Grid item xs={12} sm={6} md={4} key={t.lab_id}>
            <TrendCard trend={t} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
'''

# ── Screen 5: Safety Alerts ────────────────────────────────────────────────
safety = r'''import React, { useState, useEffect } from "react";
import {
  Box, Typography, Chip, CircularProgress, Divider, Stack,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { patientApi } from "../../api/patient";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const SEVERITY_STYLES = {
  Major:    { bg: "#FED7D7", border: "#FC8181", text: CRIMSON, label: "MAJOR" },
  Moderate: { bg: "#FDF3E7", border: "#F6AD55", text: AMBER, label: "MODERATE" },
  Minor:    { bg: "#EDF2F7", border: "#CBD5E0", text: "#4A5568", label: "MINOR" },
};

const AlertCard = ({ alert }) => {
  const sev = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.Minor;
  return (
    <Box
      sx={{
        p: 3, borderRadius: 2.5,
        border: `1.5px solid ${sev.border}`,
        backgroundColor: sev.bg,
        position: "relative",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1.5, flexWrap: "wrap" }}>
        <Chip label={sev.label} size="small" sx={{ fontWeight: 800, backgroundColor: sev.text, color: "#fff", letterSpacing: "0.06em", fontSize: "0.7rem" }} />
        {alert.cross_system && (
          <Chip label="CROSS-SYSTEM" size="small" sx={{ fontWeight: 800, backgroundColor: AMBER, color: "#fff", letterSpacing: "0.06em", fontSize: "0.7rem" }} />
        )}
        <Typography variant="caption" sx={{ color: "#718096", ml: "auto" }}>
          {alert.generated_date ? new Date(alert.generated_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : ""}
        </Typography>
      </Box>

      <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "#1A2230", mb: 0.75, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
        {alert.medicine_1} + {alert.medicine_2}
      </Typography>

      <Typography variant="body2" sx={{ color: "#1A2230", lineHeight: 1.6, mb: alert.cross_system ? 1.5 : 0 }}>
        {alert.evidence}
      </Typography>

      {alert.cross_system && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 1, pt: 1, borderTop: `1px solid ${sev.border}` }}>
          <Box sx={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: TEAL, flexShrink: 0 }} />
          <Box sx={{ width: 24, height: 2, background: `linear-gradient(to right, ${TEAL}, ${AMBER})`, flexShrink: 0 }} />
          <Box sx={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: AMBER, flexShrink: 0 }} />
          <Typography variant="caption" sx={{ color: "#5A677D", fontWeight: 600 }}>
            Cross-system interaction — medicines from different therapeutic traditions are simultaneously active.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export const SafetyAlertsPanel = ({ patientId, initialData }) => {
  const [alerts, setAlerts] = useState(initialData || []);
  const [loading, setLoading] = useState(!initialData);

  useEffect(() => {
    if (!patientId) return;
    (async () => {
      setLoading(true);
      try {
        const data = await patientApi.getAlerts(patientId);
        setAlerts(data);
      } catch (_) {}
      setLoading(false);
    })();
  }, [patientId]);

  if (loading) return <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}><CircularProgress sx={{ color: TEAL }} /></Box>;

  if (alerts.length === 0) return (
    <Box sx={{ textAlign: "center", py: 8 }}>
      <Typography variant="h6" sx={{ color: TEAL, mb: 1 }}>No Medication Interactions Detected</Typography>
      <Typography variant="body2" sx={{ color: "#718096", maxWidth: 420, mx: "auto" }}>
        No medication interactions detected in your current regimen. Alerts will appear here if any concurrent medicines have documented clinical interactions.
      </Typography>
    </Box>
  );

  const major = alerts.filter(a => a.severity === "Major");
  const moderate = alerts.filter(a => a.severity === "Moderate");
  const minor = alerts.filter(a => a.severity === "Minor");

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 3, flexWrap: "wrap" }}>
        <Typography variant="h6" sx={{ color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
          Medication Safety Alerts
        </Typography>
        {major.length > 0 && <Chip label={`${major.length} Major`} sx={{ backgroundColor: "#FED7D7", color: CRIMSON, fontWeight: 700 }} size="small" />}
        {moderate.length > 0 && <Chip label={`${moderate.length} Moderate`} sx={{ backgroundColor: "#FDF3E7", color: AMBER, fontWeight: 700 }} size="small" />}
        {minor.length > 0 && <Chip label={`${minor.length} Minor`} sx={{ backgroundColor: "#EDF2F7", color: "#4A5568", fontWeight: 700 }} size="small" />}
      </Box>
      <Stack spacing={2}>
        {[...major, ...moderate, ...minor].map((a) => (
          <AlertCard key={a.alert_id} alert={a} />
        ))}
      </Stack>
    </Box>
  );
};
'''

# ── Screen 6: AI Summary ───────────────────────────────────────────────────
ai_summary = r'''import React, { useState, useEffect } from "react";
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
            {summary.generated_at && (
              <Typography variant="caption" sx={{ color: "#718096", alignSelf: "center" }}>
                Generated {new Date(summary.generated_at).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
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
'''

# ── Screen 7: Access Grants ────────────────────────────────────────────────
access = r'''import React, { useState, useEffect, useCallback } from "react";
import {
  Box, Typography, Button, Chip, CircularProgress, Avatar,
  Stack, Alert, Divider,
} from "@mui/material";
import PeopleOutlineIcon from "@mui/icons-material/PeopleOutline";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import { accessApi } from "../../api/access";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const formatDate = (iso) => iso ? new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—";

const GrantCard = ({ grant, onRespond, onRevoke, isApproved }) => {
  const [acting, setActing] = useState(false);

  const handleRespond = async (approve) => {
    setActing(true);
    await onRespond(grant.grant_id, approve);
    setActing(false);
  };

  const handleRevoke = async () => {
    setActing(true);
    await onRevoke(grant.grant_id);
    setActing(false);
  };

  return (
    <Box sx={{ p: 2.5, border: `1px solid ${isApproved ? "#B2DFDB" : BORDER}`, borderRadius: 2.5, backgroundColor: isApproved ? "#F0FBF8" : "#FFFFFF" }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
        <Avatar sx={{ backgroundColor: TEAL, width: 40, height: 40, fontWeight: 700, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
          {(grant.professional_name || "D")[0]}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#1A2230" }}>
            {grant.professional_name || "—"}
          </Typography>
          <Typography variant="caption" sx={{ fontFamily: "'JetBrains Mono',monospace", color: TEAL, fontWeight: 600 }}>
            {grant.professional_code || "—"}
          </Typography>
          <Typography variant="caption" sx={{ color: "#718096", display: "block" }}>
            Requested {formatDate(grant.requested_date)}
            {grant.approved_date && ` · Approved ${formatDate(grant.approved_date)}`}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1, flexShrink: 0 }}>
          {!isApproved ? (
            <>
              <Button
                size="small" variant="contained" startIcon={acting ? <CircularProgress size={14} sx={{ color: "#fff" }} /> : <CheckIcon />}
                onClick={() => handleRespond(true)} disabled={acting}
                sx={{ backgroundColor: SAGE, "&:hover": { backgroundColor: "#267764" }, textTransform: "none", fontWeight: 600 }}
              >
                Approve
              </Button>
              <Button
                size="small" variant="outlined" startIcon={<CloseIcon />}
                onClick={() => handleRespond(false)} disabled={acting}
                sx={{ color: CRIMSON, borderColor: "#FC8181", "&:hover": { borderColor: CRIMSON, backgroundColor: "#FED7D7" }, textTransform: "none", fontWeight: 600 }}
              >
                Deny
              </Button>
            </>
          ) : (
            <Button
              size="small" variant="outlined" startIcon={<CloseIcon />}
              onClick={handleRevoke} disabled={acting}
              sx={{ color: CRIMSON, borderColor: "#FC8181", "&:hover": { borderColor: CRIMSON, backgroundColor: "#FED7D7" }, textTransform: "none", fontWeight: 600 }}
            >
              {acting ? "Revoking…" : "Revoke Access"}
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export const AccessGrantsPanel = ({ patientId }) => {
  const [pending, setPending] = useState([]);
  const [approved, setApproved] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadGrants = useCallback(async () => {
    setLoading(true);
    try {
      const data = await accessApi.getPendingRequests();
      setPending(data.filter(g => g.status === "pending"));
      setApproved(data.filter(g => g.status === "approved"));
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadGrants(); }, [loadGrants]);

  const handleRespond = async (grantId, approve) => {
    try {
      await accessApi.respond(grantId, approve);
      await loadGrants();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRevoke = async (grantId) => {
    try {
      await accessApi.revoke(grantId);
      await loadGrants();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}><CircularProgress sx={{ color: TEAL }} /></Box>;

  const totalGrants = pending.length + approved.length;

  return (
    <Box>
      <Typography variant="h6" sx={{ color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif", mb: 0.5 }}>
        Doctor Access Grants
      </Typography>
      <Typography variant="caption" sx={{ color: "#718096", display: "block", mb: 3 }}>
        Only doctors you approve can view your medical records. You can revoke access at any time.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      {totalGrants === 0 ? (
        <Box sx={{ textAlign: "center", py: 8 }}>
          <PeopleOutlineIcon sx={{ fontSize: 48, color: "#B2C5CC", mb: 2 }} />
          <Typography variant="h6" sx={{ color: TEAL, mb: 1 }}>No Access Requests</Typography>
          <Typography variant="body2" sx={{ color: "#718096", maxWidth: 400, mx: "auto" }}>
            No doctors have requested access to your records yet. Share your Health ID with your doctor to allow them to request access.
          </Typography>
        </Box>
      ) : (
        <>
          {pending.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#1A2230" }}>Pending Requests</Typography>
                <Chip label={pending.length} size="small" sx={{ backgroundColor: "#FDF3E7", color: "#C07D32", fontWeight: 700 }} />
              </Box>
              <Stack spacing={1.5}>
                {pending.map(g => (
                  <GrantCard key={g.grant_id} grant={g} onRespond={handleRespond} onRevoke={handleRevoke} isApproved={false} />
                ))}
              </Stack>
            </Box>
          )}

          {approved.length > 0 && (
            <Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#1A2230" }}>Approved Access</Typography>
                <Chip label={approved.length} size="small" sx={{ backgroundColor: "#E6F4F1", color: SAGE, fontWeight: 700 }} />
              </Box>
              <Stack spacing={1.5}>
                {approved.map(g => (
                  <GrantCard key={g.grant_id} grant={g} onRespond={handleRespond} onRevoke={handleRevoke} isApproved={true} />
                ))}
              </Stack>
            </Box>
          )}
        </>
      )}
    </Box>
  );
};
'''

for fname, content in [
    ("LabTrendsPanel.jsx", lab_trends),
    ("SafetyAlertsPanel.jsx", safety),
    ("AISummaryPanel.jsx", ai_summary),
    ("AccessGrantsPanel.jsx", access),
]:
    with open(os.path.join(base, fname), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{fname} written")

print("All panels written")