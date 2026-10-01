code = """import { apiClient } from "./client";

export const adminApi = {
  getStats: async () => {
    const res = await apiClient.get("/admin/stats");
    return res.data;
  },
  getPendingProfessionals: async () => {
    const res = await apiClient.get("/admin/professionals/pending");
    return res.data;
  },
  getRejectedProfessionals: async () => {
    const res = await apiClient.get("/admin/professionals/rejected");
    return res.data;
  },
  verifyProfessional: async (professionalId, verificationStatus) => {
    const res = await apiClient.patch(`/admin/professionals/${professionalId}/verify`, {
      verification_status: verificationStatus,
    });
    return res.data;
  },
  getInteractions: async (skip = 0, limit = 100) => {
    const res = await apiClient.get(`/admin/interaction-knowledge-base?skip=${skip}&limit=${limit}`);
    return res.data;
  },
  addInteraction: async (data) => {
    const res = await apiClient.post("/admin/interaction-knowledge-base", data);
    return res.data;
  },
  getUnmatchedMedicines: async () => {
    const res = await apiClient.get("/admin/unmatched-medicines");
    return res.data;
  },
  addNormalization: async (data) => {
    const res = await apiClient.post("/admin/normalization", data);
    return res.data;
  },
  getLabReferences: async () => {
    const res = await apiClient.get("/admin/lab-references");
    return res.data;
  },
};
"""
with open(r"E:\Capstone\Projectwork\frontend\src\api\admin.js", "w", encoding="utf-8") as f:
    f.write(code)
print("Created admin.js successfully")