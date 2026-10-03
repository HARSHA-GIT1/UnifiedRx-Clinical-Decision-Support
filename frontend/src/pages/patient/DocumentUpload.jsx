import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Box, Typography, Button, Chip, Card, LinearProgress,
  Select, MenuItem, FormControl, InputLabel, Alert, Grid,
  Table, TableHead, TableRow, TableCell, TableBody, Tooltip, IconButton,
  CircularProgress, Divider, Stack,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutlined";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";
import RefreshIcon from "@mui/icons-material/Refresh";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import { documentsApi } from "../../api/documents";

const TEAL = "#0F4C5C";
const SAGE = "#2E8B75";
const AMBER = "#C07D32";
const CRIMSON = "#C53030";
const BORDER = "#E2E8F0";
const MAX_BYTES = 15 * 1024 * 1024; // 15 MB

const DOC_TYPES = [
  { value: "prescription", label: "Prescription" },
  { value: "lab_report", label: "Lab Report" },
  { value: "discharge_summary", label: "Discharge Summary" },
  { value: "diagnostic_report", label: "Diagnostic Report" },
];

const STATUS_CHIP = {
  pending:    { label: "Pending",    color: "#718096", bg: "#EDF2F7" },
  processing: { label: "Processing", color: AMBER,     bg: "#FDF3E7" },
  completed:  { label: "Completed",  color: SAGE,      bg: "#E6F4F1" },
  failed:     { label: "Failed",     color: CRIMSON,   bg: "#FED7D7" },
};

const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

// Status poller for a single document
const useDocumentPoller = (documentId, initialStatus, onComplete) => {
  const [status, setStatus] = useState(initialStatus);
  const [detail, setDetail] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!documentId || status === "completed" || status === "failed") return;
    intervalRef.current = setInterval(async () => {
      try {
        const res = await documentsApi.getStatus(documentId);
        setStatus(res.processing_status);
        if (res.processing_status === "completed") {
          const det = await documentsApi.getDetails(documentId);
          setDetail(det);
          clearInterval(intervalRef.current);
          onComplete?.();
        } else if (res.processing_status === "failed") {
          setDetail({ error_message: res.error_message });
          clearInterval(intervalRef.current);
        }
      } catch (_) {}
    }, 2000);
    return () => clearInterval(intervalRef.current);
  }, [documentId, status, onComplete]);

  return { status, detail };
};

// Uploaded item row with live status
const DocumentRow = ({ doc, onReprocess }) => {
  const { status, detail } = useDocumentPoller(
    doc.document_id, doc.processing_status, () => {}
  );
  const chip = STATUS_CHIP[status] || STATUS_CHIP.pending;

  return (
    <TableRow sx={{ "&:last-child td": { border: 0 } }}>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <InsertDriveFileIcon sx={{ color: "#718096", fontSize: 18 }} />
          <Typography variant="body2" sx={{ fontWeight: 500, color: "#1A2230" }}>{doc.file_name}</Typography>
        </Box>
      </TableCell>
      <TableCell>
        <Chip label={doc.document_type.replace("_", " ")} size="small" sx={{ textTransform: "capitalize", backgroundColor: "#EBF5F3", color: TEAL, fontWeight: 600 }} />
      </TableCell>
      <TableCell>
        <Chip
          icon={status === "processing" ? <CircularProgress size={10} sx={{ color: AMBER }} /> : undefined}
          label={chip.label}
          size="small"
          sx={{ backgroundColor: chip.bg, color: chip.color, fontWeight: 600 }}
        />
      </TableCell>
      <TableCell>
        {status === "completed" && detail && (
          <Typography variant="caption" sx={{ color: SAGE }}>
            {detail.medications_count ?? 0} medicines extracted
          </Typography>
        )}
        {status === "failed" && (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography variant="caption" sx={{ color: CRIMSON }}>
              {detail?.error_message || "Processing failed"}
            </Typography>
            <Tooltip title="Retry processing">
              <Button size="small" startIcon={<RefreshIcon />} onClick={() => onReprocess(doc.document_id)}
                sx={{ minWidth: 0, color: TEAL, textTransform: "none", fontSize: "0.75rem" }}>
                Retry
              </Button>
            </Tooltip>
          </Box>
        )}
      </TableCell>
      <TableCell>
        <Typography variant="caption" sx={{ color: "#718096" }}>
          {new Date(doc.upload_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
        </Typography>
      </TableCell>
    </TableRow>
  );
};

export const DocumentUpload = ({ patientId, onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const fileRef = useRef();

  const loadDocuments = useCallback(async () => {
    if (!patientId) return;
    setLoadingDocs(true);
    try {
      const docs = await documentsApi.listForPatient(patientId);
      setDocuments(docs);
    } catch (_) {}
    setLoadingDocs(false);
  }, [patientId]);

  useEffect(() => { loadDocuments(); }, [loadDocuments]);

  const handleFile = (f) => {
    if (!f) return;
    if (!["application/pdf", "image/jpeg", "image/png"].includes(f.type)) {
      setUploadError("Only PDF, JPG, and PNG files are accepted.");
      return;
    }
    setUploadError(null);
    setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file || !docType) return;
    setUploading(true);
    setUploadError(null);
    try {
      const res = await documentsApi.upload(file, docType);
      setUploadedDoc(res);
      setFile(null);
      setDocType("");
      await loadDocuments();
      onUploadComplete?.();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleReprocess = async (docId) => {
    try {
      await documentsApi.reprocess(docId);
      await loadDocuments();
    } catch (err) {
      setUploadError(err.message);
    }
  };

  const sizeWarning = file && file.size > MAX_BYTES * 0.9;

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, color: TEAL, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
        Upload Medical Documents
      </Typography>

      <Grid container spacing={3}>
        {/* Left: Upload zone */}
        <Grid item xs={12} md={5}>
          <Card sx={{ p: 0, border: `1px solid ${BORDER}`, borderRadius: 3, boxShadow: "none", overflow: "hidden" }}>
            {/* Drop zone */}
            <Box
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current.click()}
              sx={{
                height: 180,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                backgroundColor: dragOver ? "#EBF5F3" : (file ? "#F0FBF8" : "#FAFBFC"),
                border: `2px dashed ${dragOver ? SAGE : file ? SAGE : BORDER}`,
                borderRadius: 3,
                mx: 2,
                mt: 2,
                transition: "all 0.2s ease",
                "&:hover": { backgroundColor: "#EBF5F3", borderColor: SAGE },
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 40, color: file ? SAGE : "#B2C5CC", mb: 1 }} />
              {file ? (
                <>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: SAGE }}>{file.name}</Typography>
                  <Typography variant="caption" sx={{ color: sizeWarning ? AMBER : "#718096" }}>
                    {formatBytes(file.size)} {sizeWarning && "— approaching 15 MB limit"}
                  </Typography>
                </>
              ) : (
                <>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: "#5A677D" }}>
                    Drag & drop or click to select
                  </Typography>
                  <Typography variant="caption" sx={{ color: "#718096", mt: 0.5 }}>
                    PDF, JPG, PNG — max 15 MB
                  </Typography>
                </>
              )}
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" ref={fileRef} style={{ display: "none" }}
                onChange={(e) => handleFile(e.target.files[0])} />
            </Box>

            <Box sx={{ p: 2.5 }}>
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <InputLabel>Document Type *</InputLabel>
                <Select value={docType} onChange={(e) => setDocType(e.target.value)} label="Document Type *">
                  {DOC_TYPES.map((t) => (
                    <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              {uploadError && <Alert severity="error" sx={{ mb: 2 }}>{uploadError}</Alert>}

              <Button
                variant="contained"
                fullWidth
                size="large"
                disabled={!file || !docType || uploading || (file?.size > MAX_BYTES)}
                onClick={handleUpload}
                startIcon={uploading ? <CircularProgress size={18} sx={{ color: "#fff" }} /> : <CloudUploadIcon />}
                sx={{ py: 1.4, backgroundColor: TEAL, "&:hover": { backgroundColor: "#165E71" } }}
              >
                {uploading ? "Uploading…" : "Upload Document"}
              </Button>
            </Box>
          </Card>

          {/* Post-upload status */}
          {uploadedDoc && (
            <UploadStatus docId={uploadedDoc.document_id} initialStatus={uploadedDoc.processing_status} />
          )}
        </Grid>

        {/* Right: Documents list */}
        <Grid item xs={12} md={7}>
          <Typography variant="subtitle2" sx={{ mb: 1.5, color: "#5A677D", textTransform: "uppercase", letterSpacing: "0.06em", fontSize: "0.75rem", fontWeight: 700 }}>
            Uploaded Documents ({documents.length})
          </Typography>

          {loadingDocs ? (
            <Box sx={{ p: 3, textAlign: "center" }}><CircularProgress size={28} sx={{ color: TEAL }} /></Box>
          ) : documents.length === 0 ? (
            <Box sx={{ p: 4, textAlign: "center", border: `1px dashed ${BORDER}`, borderRadius: 2 }}>
              <InsertDriveFileIcon sx={{ fontSize: 40, color: "#B2C5CC", mb: 1 }} />
              <Typography variant="body2" sx={{ color: "#718096" }}>
                No documents uploaded yet. Upload your first prescription or lab report to start tracking.
              </Typography>
            </Box>
          ) : (
            <Box sx={{ border: `1px solid ${BORDER}`, borderRadius: 2, overflow: "hidden" }}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: "#F8FAFB" }}>
                  <TableRow>
                    {["File", "Type", "Status", "Details", "Uploaded"].map((h) => (
                      <TableCell key={h} sx={{ fontWeight: 700, color: "#5A677D", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                        {h}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents.map((doc) => (
                    <DocumentRow key={doc.document_id} doc={doc} onReprocess={handleReprocess} />
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

// Post-upload real-time status card
const UploadStatus = ({ docId, initialStatus }) => {
  const { status, detail } = useDocumentPoller(docId, initialStatus, () => {});
  const chip = STATUS_CHIP[status] || STATUS_CHIP.pending;

  return (
    <Card sx={{ mt: 2, p: 2, border: `1px solid ${BORDER}`, borderRadius: 2, boxShadow: "none" }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
        {status === "processing" && <CircularProgress size={18} sx={{ color: AMBER }} />}
        {status === "completed" && <CheckCircleIcon sx={{ color: SAGE, fontSize: 20 }} />}
        {status === "failed" && <ErrorOutlineIcon sx={{ color: CRIMSON, fontSize: 20 }} />}
        {status === "pending" && <HourglassEmptyIcon sx={{ color: "#718096", fontSize: 20 }} />}
        <Typography variant="subtitle2" sx={{ color: chip.color, fontWeight: 700 }}>
          {chip.label === "Processing" ? "Extracting clinical entities…" : chip.label}
        </Typography>
      </Box>
      {status === "processing" && <LinearProgress sx={{ borderRadius: 1, "& .MuiLinearProgress-bar": { backgroundColor: AMBER } }} />}
      {status === "completed" && detail && (
        <Typography variant="caption" sx={{ color: SAGE }}>
          {detail.medications_count ?? 0} medicines extracted from this document.
        </Typography>
      )}
      {status === "failed" && (
        <Typography variant="caption" sx={{ color: CRIMSON }}>
          {detail?.error_message || "Processing failed. Use Retry in the document list."}
        </Typography>
      )}
    </Card>
  );
};

