import { apiClient } from "./client";

export const accessApi = {
  getPendingRequests: async () => {
    const res = await apiClient.get("/access/pending");
    return res.data;
  },
  respond: async (grantId, approve) => {
    const res = await apiClient.post(`/access/${grantId}/respond`, { approve });
    return res.data;
  },
  revoke: async (grantId) => {
    const res = await apiClient.post(`/access/${grantId}/revoke`);
    return res.data;
  },
  requestAccess: async (healthCode) => {
    const res = await apiClient.post("/access/request", { health_code: healthCode });
    return res.data;
  },
  getMyPatients: async () => {
    const res = await apiClient.get("/access/my-patients");
    return res.data;
  },
};
