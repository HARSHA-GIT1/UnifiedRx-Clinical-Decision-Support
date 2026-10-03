import React, { useState, useEffect, useRef } from "react";
import {
  Box, Typography, Chip, ToggleButton, ToggleButtonGroup,
  CircularProgress, Tooltip,
} from "@mui/material";
import TimelineIcon from "@mui/icons-material/Timeline";
import MedicationIcon from "@mui/icons-material/Medication";
import ScienceIcon from "@mui/icons-material/Science";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import { patientApi } from "../../api/patient";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";

const SYSTEM_COLORS = {
  Allopathy: { bg: "#EBF5F3", border: TEAL, text: TEAL },
  Ayurveda: { bg: "#FDF3E7", border: AMBER, text: AMBER },
  Ayurvedic: { bg: "#FDF3E7", border: AMBER, text: AMBER },
  Homeopathy: { bg: "#F0F4FF", border: "#5C6BC0", text: "#5C6BC0" },
  default: { bg: "#F0F4F8", border: "#718096", text: "#718096" },
};

const EVENT_ICONS = {
  medication_started: <MedicationIcon sx={{ fontSize: 14 }} />,
  medication_stopped: <MedicationIcon sx={{ fontSize: 14 }} />,
  lab_result_recorded: <ScienceIcon sx={{ fontSize: 14 }} />,
  diagnosis_recorded: <LocalHospitalIcon sx={{ fontSize: 14 }} />,
};

const getSystemColor = (system) => SYSTEM_COLORS[system] || SYSTEM_COLORS.default;

const formatDate = (iso) => {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
};

// ── Single event node ──────────────────────────────────────────────────────
const EventNode = ({ event, track }) => {
  const sysColor = getSystemColor(event.system_of_medicine);
  const isMed = event.event_type?.startsWith("medication");
  const isLab = event.event_type === "lab_result_recorded";
  const isDiag = event.event_type === "diagnosis_recorded";
  const isStopped = event.event_type === "medication_stopped";

  return (
    <Tooltip
      title={
        <Box>
          <Typography variant="caption" sx={{ fontWeight: 700, display: "block" }}>{event.description}</Typography>
          <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.75)" }}>{formatDate(event.event_date)}</Typography>
        </Box>
      }
      arrow
    >
      <Box
        sx={{
          minWidth: 140,
          maxWidth: 160,
          mx: 1,
          flexShrink: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Node circle */}
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            border: `2.5px solid ${isMed ? sysColor.border : isLab ? SAGE : isDiag ? TEAL : "#718096"}`,
            backgroundColor: isMed ? sysColor.bg : isLab ? "#E6F4F1" : isDiag ? "#EBF5F3" : "#F0F4F8",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: isMed ? sysColor.text : isLab ? SAGE : isDiag ? TEAL : "#718096",
            opacity: isStopped ? 0.55 : 1,
            cursor: "pointer",
            transition: "transform 0.15s ease",
            "&:hover": { transform: "scale(1.12)" },
          }}
        >
          {EVENT_ICONS[event.event_type] || <TimelineIcon sx={{ fontSize: 14 }} />}
        </Box>

        {/* Date */}
        <Typography
          variant="caption"
          sx={{ mt: 0.75, color: "#718096", fontFamily: "'JetBrains Mono', monospace", fontSize: "0.65rem", textAlign: "center", lineHeight: 1.2 }}
        >
          {formatDate(event.event_date)}
        </Typography>

        {/* Label */}
        <Typography
          variant="caption"
          sx={{
            mt: 0.4,
            color: "#1A2230",
            fontWeight: 600,
            textAlign: "center",
            fontSize: "0.72rem",
            maxWidth: 140,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            textDecoration: isStopped ? "line-through" : "none",
          }}
        >
          {event.medicine_name || event.description}
        </Typography>

        {/* System badge */}
        {event.system_of_medicine && (
          <Chip
            label={event.system_of_medicine}
            size="small"
            sx={{
              mt: 0.5,
              height: 16,
              fontSize: "0.6rem",
              fontWeight: 700,
              backgroundColor: sysColor.bg,
              color: sysColor.text,
              border: `1px solid ${sysColor.border}`,
            }}
          />
        )}
      </Box>
    </Tooltip>
  );
};

// ── Track row ─────────────────────────────────────────────────────────────
const TrackRow = ({ label, color, events, showConnector }) => (
  <Box sx={{ display: "flex", alignItems: "flex-start", mb: 3 }}>
    {/* Track label */}
    <Box
      sx={{
        width: 110,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        gap: 0.75,
        pt: 1.2,
      }}
    >
      <Box sx={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: color, flexShrink: 0 }} />
      <Typography variant="caption" sx={{ color, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", fontSize: "0.68rem", lineHeight: 1.3 }}>
        {label}
      </Typography>
    </Box>

    {/* Track line + events */}
    <Box sx={{ flex: 1, position: "relative" }}>
      {/* Horizontal rail */}
      <Box
        sx={{
          position: "absolute",
          top: 18,
          left: 0,
          right: 0,
          height: 2,
          backgroundColor: events.length > 0 ? `${color}30` : `${color}15`,
          borderRadius: 1,
        }}
      />
      {events.length === 0 ? (
        <Box sx={{ pl: 2, pt: 1 }}>
          <Typography variant="caption" sx={{ color: "#B2C5CC", fontStyle: "italic" }}>
            No {label.toLowerCase()} events yet
          </Typography>
        </Box>
      ) : (
        <Box sx={{ display: "flex", overflowX: "auto", pb: 1, "&::-webkit-scrollbar": { height: 4 }, "&::-webkit-scrollbar-thumb": { background: "#B2C5CC", borderRadius: 2 } }}>
          {events.map((evt) => (
            <EventNode key={evt.timeline_id} event={evt} />
          ))}
        </Box>
      )}
    </Box>
  </Box>
);

// ── Cross-system overlap bridges ──────────────────────────────────────────
const CrossSystemBadge = ({ count }) => (
  count > 0 ? (
    <Chip
      label={`${count} Cross-System Overlap Window${count > 1 ? "s" : ""} Detected`}
      sx={{ backgroundColor: "#FDF3E7", border: `1px solid ${AMBER}`, color: AMBER, fontWeight: 700, fontSize: "0.78rem" }}
      icon={<TimelineIcon sx={{ color: AMBER, fontSize: 16 }} />}
    />
  ) : null
);

// ── Main Component ─────────────────────────────────────────────────────────
export const TimelineViewer = ({ patientId, initialData }) => {
  const [events, setEvents] = useState(initialData || []);
  const [loading, setLoading] = useState(!initialData);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!patientId) return;
    (async () => {
      setLoading(true);
      try {
        const data = await patientApi.getTimeline(patientId);
        setEvents(data);
      } catch (_) {}
      setLoading(false);
    })();
  }, [patientId]);

  // Explicit whitelists for swim-lane partitioning
  const AYUSH_SYSTEMS = ["Ayurveda", "Ayurvedic", "Unani", "Siddha", "Homeopathy", "AYUSH"];
  const ALLOPATHY_SYSTEMS = ["Allopathy", "Allopathic"];

  // Partition into swim-lanes
  const allopathyEvents = events.filter(
    (e) => (e.event_type === "medication_started" || e.event_type === "medication_stopped") &&
           (ALLOPATHY_SYSTEMS.includes(e.system_of_medicine) || !e.system_of_medicine)
  );
  const ayushEvents = events.filter(
    (e) => (e.event_type === "medication_started" || e.event_type === "medication_stopped") &&
           AYUSH_SYSTEMS.includes(e.system_of_medicine)
  );
  const diagnosticEvents = events.filter(
    (e) => e.event_type === "lab_result_recorded" || e.event_type === "diagnosis_recorded"
  );

  // Cross-system overlap detection: count concurrent allopathy + AYUSH windows
  const crossSystemCount = (() => {
    let count = 0;
    for (const ae of allopathyEvents.filter(e => e.event_type === "medication_started")) {
      for (const ye of ayushEvents.filter(e => e.event_type === "medication_started")) {
        count++;
      }
    }
    return Math.min(count, allopathyEvents.length > 0 && ayushEvents.length > 0 ? 1 : 0);
  })();

  const visibleEvents =
    filter === "medications" ? [...allopathyEvents, ...ayushEvents] :
    filter === "labs" ? diagnosticEvents :
    events;

  if (loading) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, py: 6, justifyContent: "center" }}>
        <CircularProgress size={24} sx={{ color: TEAL }} />
        <Typography variant="body2" sx={{ color: "#718096" }}>Loading clinical timeline…</Typography>
      </Box>
    );
  }

  if (events.length === 0) {
    return (
      <Box sx={{ textAlign: "center", py: 8 }}>
        <TimelineIcon sx={{ fontSize: 48, color: "#B2C5CC", mb: 2 }} />
        <Typography variant="h6" sx={{ color: TEAL, mb: 1 }}>Your Longitudinal Timeline</Typography>
        <Typography variant="body2" sx={{ color: "#718096", maxWidth: 420, mx: "auto" }}>
          Your medication, diagnosis, and lab events will appear here after you upload and process your first document.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2.5, flexWrap: "wrap", gap: 1.5 }}>
        <Box>
          <Typography variant="h6" sx={{ color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif", mb: 0.5 }}>
            Multi-Track Longitudinal Timeline
          </Typography>
          <Typography variant="caption" sx={{ color: "#718096" }}>
            {events.length} clinical events across all documents
          </Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, flexWrap: "wrap" }}>
          <CrossSystemBadge count={crossSystemCount} />
          <ToggleButtonGroup value={filter} exclusive onChange={(_, v) => v && setFilter(v)} size="small">
            <ToggleButton value="all" sx={{ textTransform: "none", fontWeight: 600, px: 2 }}>All</ToggleButton>
            <ToggleButton value="medications" sx={{ textTransform: "none", fontWeight: 600, px: 2 }}>Medicines</ToggleButton>
            <ToggleButton value="labs" sx={{ textTransform: "none", fontWeight: 600, px: 2 }}>Labs & Diagnoses</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {/* Legend */}
      <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
        {[
          { color: TEAL, label: "Allopathy" },
          { color: AMBER, label: "AYUSH / Ayurveda" },
          { color: SAGE, label: "Lab Results" },
          { color: "#718096", label: "Diagnosis" },
        ].map((l) => (
          <Box key={l.label} sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
            <Box sx={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: l.color }} />
            <Typography variant="caption" sx={{ color: "#5A677D", fontWeight: 500 }}>{l.label}</Typography>
          </Box>
        ))}
      </Box>

      {/* Cross-system bridge visualization */}
      {crossSystemCount > 0 && (
        <Box
          sx={{
            mb: 3, p: 2, borderRadius: 2,
            background: `linear-gradient(135deg, #EBF5F3 0%, #FDF3E7 100%)`,
            border: `1px solid ${BORDER}`,
            display: "flex", alignItems: "center", gap: 2,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: TEAL }} />
            <Box sx={{ width: 48, height: 2, background: `linear-gradient(to right, ${TEAL}, ${AMBER})` }} />
            <Box sx={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: AMBER }} />
          </Box>
          <Typography variant="caption" sx={{ color: "#5A677D", fontWeight: 600 }}>
            Co-prescription window detected between Allopathy and AYUSH medicine tracks. Review Safety Alerts for interaction flags.
          </Typography>
        </Box>
      )}

      {/* Three swim-lanes */}
      <Box sx={{ overflowX: "auto", pb: 1, border: `1px solid ${BORDER}`, borderRadius: 2, p: 2.5, backgroundColor: "#FAFBFC" }}>
        {(filter === "all" || filter === "medications") && (
          <>
            <TrackRow label="Allopathy" color={TEAL} events={filter === "all" ? allopathyEvents : allopathyEvents} />
            <TrackRow label="AYUSH" color={AMBER} events={filter === "all" ? ayushEvents : ayushEvents} />
          </>
        )}
        {(filter === "all" || filter === "labs") && (
          <TrackRow label="Labs & Diagnosis" color={SAGE} events={filter === "all" ? diagnosticEvents : diagnosticEvents} />
        )}
        {filter === "medications" && diagnosticEvents.length === 0 && null}
      </Box>
    </Box>
  );
};
