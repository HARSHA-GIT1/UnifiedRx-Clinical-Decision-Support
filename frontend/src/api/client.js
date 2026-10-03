import axios from "axios";

// Base API URL for backend
export const API_BASE_URL = "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// In-memory token holder (React AuthContext registers getter)
let getToken = () => null;

export const setAuthTokenGetter = (fn) => {
  getToken = fn;
};

// Attach in-memory bearer token to outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for clear clinical error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Pass along full error details or standardized fallback
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred. Please verify your connection.";
    const err = new Error(message);
    err.response = error.response;
    err.status = error.response?.status;
    err.detail = error.response?.data?.detail;
    return Promise.reject(err);
  }
);
