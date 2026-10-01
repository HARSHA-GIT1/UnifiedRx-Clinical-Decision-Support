import { apiClient } from "./client";

export const documentsApi = {
  upload: async (file, documentType) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);
    const res = await apiClient.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },
  getStatus: async (documentId) => {
    const res = await apiClient.get(`/documents/${documentId}/status`);
    return res.data;
  },
  getDetails: async (documentId) => {
    const res = await apiClient.get(`/documents/${documentId}`);
    return res.data;
  },
  reprocess: async (documentId) => {
    const res = await apiClient.post(`/documents/${documentId}/reprocess`);
    return res.data;
  },
  listForPatient: async (patientId) => {
    const res = await apiClient.get(`/documents/patient/${patientId}`);
    return res.data;
  },
};
