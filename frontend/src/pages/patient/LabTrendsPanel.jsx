import React, { useState, useEffect } from "react";
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
