import apiClient from "./client";
import type { components } from "../types/api";

export type CreateConfigurationRequest = components["schemas"]["CreateConfigurationRequest"];
export type UpdateConfigurationRequest = components["schemas"]["UpdateConfigurationRequest"];

// Note: The API wraps successful responses in APISuccessEnvelope which client interceptor unwraps.
// However, our interceptor unwraps `response.data`.
// So the return type of these functions is the generic structure that matches the backend response.

export const configurationApi = {
  create: async (data: CreateConfigurationRequest) => {
    return apiClient.post<{ configuration_id: string, status: string, selected_category: string, selected_feature_options: string[] }>("/configurations", data);
  },
  
  get: async (id: string) => {
    return apiClient.get<any>(`/configurations/${id}`);
  },

  update: async (id: string, data: UpdateConfigurationRequest) => {
    return apiClient.put<any>(`/configurations/${id}`, data);
  },

  validate: async (id: string) => {
    return apiClient.post<any>(`/configurations/${id}/validate`);
  },

  getPricing: async (id: string) => {
    return apiClient.get<any>(`/configurations/${id}/pricing`);
  },

  getValidation: async (id: string) => {
    return apiClient.get<any>(`/configurations/${id}/validation`);
  },

  delete: async (id: string) => {
    return apiClient.delete(`/configurations/${id}`);
  }
};
