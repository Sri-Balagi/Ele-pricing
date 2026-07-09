import axios from "axios";
import type { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from "axios";
import { monitor } from "@/lib/monitoring";

// Standard API Envelope Structure
export interface APIErrorResponse {
  success: boolean;
  error_code: string;
  message: string;
  correlation_id?: string;
  details?: Record<string, any>;
  timestamp?: string;
}

export interface APISuccessResponse<T> {
  success: boolean;
  data: T;
  correlation_id?: string;
  timestamp?: string;
}

const apiClient = axios.create({
  baseURL: "/api/v1", // Assumes vite proxy /api to backend
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // We can add auth tokens here if needed in the future
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Extract correlation ID if present and not in body
    const correlationId = response.headers["x-correlation-id"] || (response.data && response.data.correlation_id);
    
    // Unwrap the 'data' payload from APISuccessEnvelope if present
    if (response.data && response.data.success === true && 'data' in response.data) {
      const payload = response.data.data;
      if (correlationId && typeof payload === 'object' && payload !== null) {
        payload.correlation_id = payload.correlation_id || correlationId;
      }
      return payload;
    }
    
    if (correlationId && response.data && typeof response.data === 'object') {
      response.data.correlation_id = response.data.correlation_id || correlationId;
    }
    return response.data;
  },
  (error: AxiosError<APIErrorResponse>) => {
    // Normalize error
    let normalizedError: APIErrorResponse = {
      success: false,
      error_code: "UNKNOWN_ERROR",
      message: "An unexpected error occurred",
    };

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.data && error.response.data.error_code) {
        normalizedError = error.response.data;
      } else {
        normalizedError.error_code = `HTTP_${error.response.status}`;
        normalizedError.message = error.message;
      }
      
      const correlationId = error.response.headers["x-correlation-id"];
      if (correlationId) {
        normalizedError.correlation_id = correlationId;
      }
    } else if (error.request) {
      // The request was made but no response was received
      normalizedError.error_code = "NETWORK_ERROR";
      normalizedError.message = "No response received from the server.";
    } else {
      // Something happened in setting up the request that triggered an Error
      normalizedError.error_code = "REQUEST_SETUP_ERROR";
      // Fallback
      normalizedError.message = error.message || "An unexpected error occurred.";
    }

    monitor.captureException(normalizedError, { url: error.config?.url, method: error.config?.method });
    return Promise.reject(normalizedError);
  }
);

const customClient = {
  get: <T = any>(url: string, config?: any) => apiClient.get(url, config) as unknown as Promise<T>,
  post: <T = any>(url: string, data?: any, config?: any) => apiClient.post(url, data, config) as unknown as Promise<T>,
  put: <T = any>(url: string, data?: any, config?: any) => apiClient.put(url, data, config) as unknown as Promise<T>,
  delete: <T = any>(url: string, config?: any) => apiClient.delete(url, config) as unknown as Promise<T>,
  patch: <T = any>(url: string, data?: any, config?: any) => apiClient.patch(url, data, config) as unknown as Promise<T>,
  interceptors: apiClient.interceptors,
  defaults: apiClient.defaults,
};

export default customClient;
