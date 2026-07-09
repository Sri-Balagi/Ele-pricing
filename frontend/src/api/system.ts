import apiClient from "./client";
import type { components } from "../types/api";

export type SystemPipelineResponse = components["schemas"]["SystemPipelineResponse"];

export const systemApi = {
  getPipelineDiagnostics: async () => {
    return apiClient.get<SystemPipelineResponse>("/system/pipeline");
  },
  getStoreDiagnostics: async () => {
    return apiClient.get<any>("/system/store");
  }
};
