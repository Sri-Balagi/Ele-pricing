import apiClient from "./client";
import type { components } from "../types/api";

export type CreateConfigurationRequest = components["schemas"]["CreateConfigurationRequest"];
export type UpdateConfigurationRequest = components["schemas"]["UpdateConfigurationRequest"];

export interface CreateConfigPayload {
  project_name: string;
  customer_name?: string;
  selected_category?: string;
}

export interface UpdateConfigPayload {
  project_name?: string;
  customer_name?: string;
  selected_category?: string;
}

export interface Configuration {
  configuration_id: string;
  project_name: string | null;
  customer_name: string | null;
  status: string;
}

// Note: The API wraps successful responses in APISuccessEnvelope which client interceptor unwraps.
// However, our interceptor unwraps `response.data`.
// So the return type of these functions is the generic structure that matches the backend response.

export const configurationApi = {
  create: async (data: CreateConfigurationRequest) => {
    return apiClient.post<any>("/configurations", data);
  },
  
  list: async (limit = 100, offset = 0) => {
    return apiClient.get<any>(`/configurations?limit=${limit}&offset=${offset}`);
  },

  search: async (query: string, limit = 20) => {
    return apiClient.get<any>(`/configurations/search?q=${encodeURIComponent(query)}&limit=${limit}`);
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

  getBOM: async (id: string) => {
    return apiClient.get<any>(`/configurations/${id}/bom`);
  },

  getValidation: async (id: string) => {
    return apiClient.get<any>(`/configurations/${id}/validation`);
  },

  delete: async (id: string) => {
    return apiClient.delete(`/configurations/${id}`);
  }
};
