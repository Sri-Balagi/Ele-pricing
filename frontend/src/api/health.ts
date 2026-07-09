import apiClient from "./client";
import type { components } from "../types/api";

export type DetailedHealthResponse = components["schemas"]["DetailedHealthResponse"];
export type ReadinessResponse = components["schemas"]["ReadinessResponse"];

export const healthApi = {
  getLiveness: async () => {
    return apiClient.get<DetailedHealthResponse>("/health");
  },
  getReadiness: async () => {
    return apiClient.get<ReadinessResponse>("/health/ready");
  }
};
