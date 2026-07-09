import apiClient from "./client";

export const quoteApi = {
  getQuoteInfo: async (configurationId: string) => {
    return apiClient.get<any>(`/configurations/${configurationId}/quote`);
  }
};
