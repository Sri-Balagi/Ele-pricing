import apiClient from "./client";

export const dashboardApi = {
  getMetrics: async () => {
    return apiClient.get<any>("/dashboard/metrics");
  }
};
