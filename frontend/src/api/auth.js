import { apiClient } from "./client";

export const authApi = {
  registerPatient: async (data) => {
    const res = await apiClient.post("/auth/register/patient", data);
    return res.data;
  },

  registerDoctor: async (data) => {
    const res = await apiClient.post("/auth/register/doctor", data);
    return res.data;
  },

  login: async (email, password) => {
    const res = await apiClient.post("/auth/login", { email, password });
    return res.data;
  },

  adminLogin: async (email, password) => {
    const res = await apiClient.post("/auth/admin/login", { email, password });
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get("/auth/me");
    return res.data;
  },
};
