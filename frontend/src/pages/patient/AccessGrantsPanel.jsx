import React, { useState, useEffect, useCallback } from "react";
import {
  Box, Typography, Button, Chip, CircularProgress, Avatar,
  Stack, Alert, Divider,
} from "@mui/material";
import PeopleOutlineIcon from "@mui/icons-material/PeopleOutlined";
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
