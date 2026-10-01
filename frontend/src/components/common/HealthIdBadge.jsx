import React, { useState } from "react";
import { Box, Chip, Tooltip, IconButton, Snackbar } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckIcon from "@mui/icons-material/Check";

export const HealthIdBadge = ({ id, label = "Health ID", size = "medium" }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e) => {
    e.stopPropagation();
    if (!id) return;
    navigator.clipboard.writeText(id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!id) return null;

  return (
    <Box sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}>
      <Tooltip title={`Click to copy ${label}`}>
        <Chip
          label={`${label ? `${label}: ` : ""}${id}`}
          onClick={handleCopy}
          icon={copied ? <CheckIcon fontSize="small" sx={{ color: "#2E8B75 !important" }} /> : <ContentCopyIcon fontSize="small" />}
          sx={{
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: 600,
            fontSize: size === "large" ? "1.1rem" : "0.85rem",
            padding: size === "large" ? "12px 14px" : "6px 8px",
            height: size === "large" ? 44 : 32,
            backgroundColor: "#EBF5F3",
            color: "#0F4C5C",
            border: "1px solid #B8DFD8",
            cursor: "pointer",
            "&:hover": {
              backgroundColor: "#DCEEEA",
            },
          }}
        />
      </Tooltip>
      <Snackbar
        open={copied}
        autoHideDuration={2000}
        onClose={() => setCopied(false)}
        message={`${label} copied to clipboard`}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
};
