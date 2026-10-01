import os

base = r"E:\Capstone\Projectwork\frontend\src\api"

patient_api = (
    'import { apiClient } from "./client";\n\n'
    'export const patientApi = {\n'
    '  getMe: async () => {\n'
    '    const res = await apiClient.get("/patients/me");\n'
    '    return res.data;\n'
    '  },\n'
    '  getDashboard: async (patientId) => {\n'
    '    const res = await apiClient.get(`/patients/${patientId}/dashboard`);\n'
    '    return res.data;\n'
    '  },\n'
    '  getTimeline: async (patientId) => {\n'
    '    const res = await apiClient.get(`/patients/${patientId}/timeline`);\n'
    '    return res.data;\n'
    '  },\n'
    '  getAlerts: async (patientId) => {\n'
    '    const res = await apiClient.get(`/patients/${patientId}/alerts`);\n'
    '    return res.data;\n'
    '  },\n'
    '  getLabTrends: async (patientId) => {\n'
    '    const res = await apiClient.get(`/patients/${patientId}/lab-trends`);\n'
    '    return res.data;\n'
    '  },\n'
    '  getSummary: async (patientId) => {\n'
    '    const res = await apiClient.get(`/patients/${patientId}/summary`);\n'
    '    return res.data;\n'
    '  },\n'
    '  generateSummary: async (patientId, forceRefresh = false) => {\n'
    '    const res = await apiClient.post(`/patients/${patientId}/summary/generate?force_refresh=${forceRefresh}`);\n'
    '    return res.data;\n'
    '  },\n'
    '};\n'
)

documents_api = (
    'import { apiClient } from "./client";\n\n'
    'export const documentsApi = {\n'
    '  upload: async (file, documentType) => {\n'
    '    const formData = new FormData();\n'
    '    formData.append("file", file);\n'
    '    formData.append("document_type", documentType);\n'
    '    const res = await apiClient.post("/documents/upload", formData, {\n'
    '      headers: { "Content-Type": "multipart/form-data" },\n'
    '    });\n'
    '    return res.data;\n'
    '  },\n'
    '  getStatus: async (documentId) => {\n'
    '    const res = await apiClient.get(`/documents/${documentId}/status`);\n'
    '    return res.data;\n'
    '  },\n'
    '  getDetails: async (documentId) => {\n'
    '    const res = await apiClient.get(`/documents/${documentId}`);\n'
    '    return res.data;\n'
    '  },\n'
    '  reprocess: async (documentId) => {\n'
    '    const res = await apiClient.post(`/documents/${documentId}/reprocess`);\n'
    '    return res.data;\n'
    '  },\n'
    '  listForPatient: async (patientId) => {\n'
    '    const res = await apiClient.get(`/documents/patient/${patientId}`);\n'
    '    return res.data;\n'
    '  },\n'
    '};\n'
)

access_api = (
    'import { apiClient } from "./client";\n\n'
    'export const accessApi = {\n'
    '  getPendingRequests: async () => {\n'
    '    const res = await apiClient.get("/access/pending");\n'
    '    return res.data;\n'
    '  },\n'
    '  respond: async (grantId, approve) => {\n'
    '    const res = await apiClient.post(`/access/${grantId}/respond`, { approve });\n'
    '    return res.data;\n'
    '  },\n'
    '  revoke: async (grantId) => {\n'
    '    const res = await apiClient.post(`/access/${grantId}/revoke`);\n'
    '    return res.data;\n'
    '  },\n'
    '  requestAccess: async (healthCode) => {\n'
    '    const res = await apiClient.post("/access/request", { health_code: healthCode });\n'
    '    return res.data;\n'
    '  },\n'
    '};\n'
)

with open(os.path.join(base, "patient.js"), "w", encoding="utf-8") as f:
    f.write(patient_api)
with open(os.path.join(base, "documents.js"), "w", encoding="utf-8") as f:
    f.write(documents_api)
with open(os.path.join(base, "access.js"), "w", encoding="utf-8") as f:
    f.write(access_api)
print("All API modules written")