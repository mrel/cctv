/**
 * API client for the Surveillance System backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post('/auth/login', { username, password }),
  
  refresh: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  
  getMe: () =>
    apiClient.get('/auth/me'),
  
  logout: () =>
    apiClient.post('/auth/logout'),
};

// Camera API
export const cameraApi = {
  getAll: (params?: any) =>
    apiClient.get('/cameras', { params }),
  
  getById: (id: string) =>
    apiClient.get(`/cameras/${id}`),
  
  create: (data: any) =>
    apiClient.post('/cameras', data),
  
  update: (id: string, data: any) =>
    apiClient.put(`/cameras/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/cameras/${id}`),
  
  getHealth: (id: string) =>
    apiClient.get(`/cameras/${id}/health`),
  
  test: (id: string) =>
    apiClient.post(`/cameras/${id}/test`),
  
  testConnection: (rtspUrl: string) =>
    apiClient.post('/cameras/test-connection', { rtsp_url: rtspUrl }),
};

// Subject API
export const subjectApi = {
  getAll: (params?: any) =>
    apiClient.get('/subjects', { params }),
  
  search: (params: any) =>
    apiClient.get('/subjects/search', { params }),
  
  getById: (id: string) =>
    apiClient.get(`/subjects/${id}`),
  
  create: (data: any) =>
    apiClient.post('/subjects', data),
  
  update: (id: string, data: any) =>
    apiClient.put(`/subjects/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/subjects/${id}`),
  
  getTimeline: (id: string, limit?: number) =>
    apiClient.get(`/subjects/${id}/timeline`, { params: { limit } }),
  
  enroll: (id: string, image: File) => {
    const formData = new FormData();
    formData.append('image', image);
    return apiClient.post(`/subjects/${id}/enroll`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  searchByImage: (image: File, threshold?: number) => {
    const formData = new FormData();
    formData.append('image', image);
    return apiClient.post('/subjects/search-by-image', formData, {
      params: { threshold },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  vectorSearch: (embedding: number[], threshold?: number, maxResults?: number) =>
    apiClient.post('/subjects/vector-search', embedding, {
      params: { threshold, max_results: maxResults },
    }),
};

// Sighting API
export const sightingApi = {
  search: (params: any) =>
    apiClient.get('/sightings/search', { params }),
  
  getById: (id: string) =>
    apiClient.get(`/sightings/${id}`),
  
  getRecent: (limit?: number) =>
    apiClient.get('/sightings/recent', { params: { limit } }),
  
  create: (data: any) =>
    apiClient.post('/sightings', data),
};

// Alert API
export const alertApi = {
  // Rules
  getRules: (params?: any) =>
    apiClient.get('/alerts/rules', { params }),
  
  getRuleById: (id: string) =>
    apiClient.get(`/alerts/rules/${id}`),
  
  createRule: (data: any) =>
    apiClient.post('/alerts/rules', data),
  
  updateRule: (id: string, data: any) =>
    apiClient.put(`/alerts/rules/${id}`, data),
  
  deleteRule: (id: string) =>
    apiClient.delete(`/alerts/rules/${id}`),
  
  // Logs
  getLogs: (params?: any) =>
    apiClient.get('/alerts/logs', { params }),
  
  getLogById: (id: string) =>
    apiClient.get(`/alerts/logs/${id}`),
  
  acknowledge: (id: string, notes?: string) =>
    apiClient.post(`/alerts/logs/${id}/acknowledge`, { notes }),
  
  resolve: (id: string, notes?: string) =>
    apiClient.post(`/alerts/logs/${id}/resolve`, { notes }),
  
  // Stats
  getStats: () =>
    apiClient.get('/alerts/stats'),
};

// Analytics API
export const analyticsApi = {
  getStatistics: () =>
    apiClient.get('/analytics/statistics'),
  
  getHeatmap: (data: any) =>
    apiClient.post('/analytics/heatmap', data),
  
  getCameraStats: (cameraId: string, hours?: number) =>
    apiClient.get(`/analytics/cameras/${cameraId}/stats`, { params: { hours } }),
  
  getMovementFlow: (timeFrom: string, timeTo: string) =>
    apiClient.get('/analytics/movement-flow', { params: { time_from: timeFrom, time_to: timeTo } }),
  
  getDemographics: (timeFrom: string, timeTo: string) =>
    apiClient.get('/analytics/demographics', { params: { time_from: timeFrom, time_to: timeTo } }),
  
  export: (data: any) =>
    apiClient.post('/analytics/export', data),
};

// User API
export const userApi = {
  getAll: (params?: any) =>
    apiClient.get('/users', { params }),
  
  getById: (id: string) =>
    apiClient.get(`/users/${id}`),
  
  create: (data: any) =>
    apiClient.post('/users', data),
  
  update: (id: string, data: any) =>
    apiClient.put(`/users/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/users/${id}`),
  
  resetPassword: (id: string, newPassword: string) =>
    apiClient.post(`/users/${id}/reset-password`, { new_password: newPassword }),
};

// Image API
export const imageApi = {
  getById: (id: string) =>
    apiClient.get(`/images/${id}`),
  
  download: (id: string) =>
    apiClient.get(`/images/${id}/download`, { responseType: 'blob' }),
  
  getUrl: (id: string, expires?: number) =>
    apiClient.get(`/images/${id}/url`, { params: { expires } }),
  
  uploadSubjectImage: (subjectId: string, image: File, imageType?: string) => {
    const formData = new FormData();
    formData.append('image', image);
    return apiClient.post(`/images/upload/subject/${subjectId}`, formData, {
      params: { image_type: imageType },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  delete: (id: string) =>
    apiClient.delete(`/images/${id}`),
};

export default apiClient;
