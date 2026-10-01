import React, { useState, useEffect } from "react";
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
