import { apiClient } from "./client";

export const patientApi = {
  getMe: async () => {
    const res = await apiClient.get("/patients/me");
    return res.data;
  },
  getDashboard: async (patientId) => {
    const res = await apiClient.get(`/patients/${patientId}/dashboard`);
    return res.data;
  },
  getTimeline: async (patientId) => {
    const res = await apiClient.get(`/patients/${patientId}/timeline`);
    return res.data;
  },
  getAlerts: async (patientId) => {
    const res = await apiClient.get(`/patients/${patientId}/alerts`);
    return res.data;
  },
  getLabTrends: async (patientId) => {
    const res = await apiClient.get(`/patients/${patientId}/lab-trends`);
    return res.data;
  },
  getSummary: async (patientId) => {
    const res = await apiClient.get(`/patients/${patientId}/summary`);
    return res.data;
  },
  generateSummary: async (patientId, forceRefresh = false) => {
    const res = await apiClient.post(`/patients/${patientId}/summary/generate?force_refresh=${forceRefresh}`);
    return res.data;
  },
};
