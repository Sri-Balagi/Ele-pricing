import apiClient from "./client";

export const exportApi = {
  getExportUrl: (configurationId: string, format: string) => {
    return `${apiClient.defaults.baseURL}/configurations/${configurationId}/export/${format}`;
  },
  downloadExport: async (configurationId: string, format: string, onProgress?: (progressEvent: any) => void) => {
    return apiClient.get(`/configurations/${configurationId}/export/${format}`, {
      responseType: 'blob',
      onDownloadProgress: onProgress
    });
  }
};
