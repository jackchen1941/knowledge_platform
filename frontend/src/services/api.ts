import axios, { AxiosInstance } from 'axios';
import { LoginCredentials, RegisterData, AuthResponse, User } from '@/types/auth';

// Create axios instance with base configuration
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: process.env.REACT_APP_API_URL || '/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle token refresh
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          try {
            const response = await axios.post('/api/v1/auth/refresh', {
              refresh_token: refreshToken,
            });

            const { access_token } = response.data;
            localStorage.setItem('token', access_token);

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return instance(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
          }
        }
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

const api = createApiInstance();

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },
};

// Knowledge API
export const knowledgeAPI = {
  list: (params?: any) => api.get('/knowledge', { params }),
  get: (id: string) => api.get(`/knowledge/${id}`),
  create: (data: any) => api.post('/knowledge', data),
  update: (id: string, data: any) => api.put(`/knowledge/${id}`, data),
  delete: (id: string) => api.delete(`/knowledge/${id}`),
  restore: (id: string) => api.post(`/knowledge/${id}/restore`),
  publish: (id: string) => api.post(`/knowledge/${id}/publish`),
  getVersions: (id: string) => api.get(`/knowledge/${id}/versions`),
};

// Categories API
export const categoriesAPI = {
  list: (params?: any) => api.get('/categories', { params }),
  getTree: () => api.get('/categories/tree'),
  get: (id: string) => api.get(`/categories/${id}`),
  create: (data: any) => api.post('/categories', data),
  update: (id: string, data: any) => api.put(`/categories/${id}`, data),
  delete: (id: string, deleteChildren?: boolean) =>
    api.delete(`/categories/${id}`, { params: { delete_children: deleteChildren } }),
};

// Tags API
export const tagsAPI = {
  list: (params?: any) => api.get('/tags', { params }),
  get: (id: string) => api.get(`/tags/${id}`),
  create: (data: any) => api.post('/tags', data),
  update: (id: string, data: any) => api.put(`/tags/${id}`, data),
  delete: (id: string) => api.delete(`/tags/${id}`),
  getPopular: (limit?: number) => api.get('/tags/popular', { params: { limit } }),
  autocomplete: (prefix: string) => api.get('/tags/autocomplete', { params: { prefix } }),
};

// Search API
export const searchAPI = {
  search: (params: any) => api.get('/search', { params }),
  suggestions: (prefix: string) => api.get('/search/suggestions', { params: { prefix } }),
  similar: (id: string) => api.get(`/search/similar/${id}`),
};

// Analytics API
export const analyticsAPI = {
  overview: () => api.get('/analytics/overview'),
  activity: (days?: number) => api.get('/analytics/activity', { params: { days } }),
  distribution: () => api.get('/analytics/distribution'),
  topTags: (limit?: number) => api.get('/analytics/tags/top', { params: { limit } }),
  trends: (days?: number) => api.get('/analytics/trends', { params: { days } }),
};

// Knowledge Graph API
export const graphAPI = {
  getData: (centerId?: string, depth?: number) => {
    const params: any = {};
    if (centerId) params.center_id = centerId;
    if (depth) params.depth = depth;
    return api.get('/graph', { params });
  },
  getStats: () => api.get('/graph/stats'),
  createLink: (knowledgeId: string, data: any) => 
    api.post(`/knowledge/${knowledgeId}/links`, data),
  getLinks: (knowledgeId: string, direction: string = 'both') => 
    api.get(`/knowledge/${knowledgeId}/links`, { params: { direction } }),
  deleteLink: (linkId: string) => api.delete(`/links/${linkId}`),
  getRelated: (knowledgeId: string, limit: number = 10) => 
    api.get(`/knowledge/${knowledgeId}/related`, { params: { limit } }),
};

// Backup API
export const backupAPI = {
  create: (backupType: string = 'full', since?: string) => {
    const data: any = { backup_type: backupType };
    if (since) data.since = since;
    return api.post('/backup/create', data, { responseType: 'blob' });
  },
  verify: (file: File) => {
    const formData = new FormData();
    formData.append('backup_file', file);
    return api.post('/backup/verify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  restore: (file: File, options: any) => {
    const formData = new FormData();
    formData.append('backup_file', file);
    const params = new URLSearchParams(options).toString();
    return api.post(`/backup/restore?${params}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// Sync API
export const syncAPI = {
  // Device management
  registerDevice: (data: any) => api.post('/sync/devices/register', data),
  listDevices: () => api.get('/sync/devices'),
  getDevice: (deviceId: string) => api.get(`/sync/devices/${deviceId}`),
  updateDevice: (deviceId: string, data: any) => api.put(`/sync/devices/${deviceId}`, data),
  deleteDevice: (deviceId: string) => api.delete(`/sync/devices/${deviceId}`),
  
  // Sync operations
  pull: (deviceId: string, lastSyncTime?: string) => {
    const params: any = {};
    if (lastSyncTime) params.last_sync_time = lastSyncTime;
    return api.post(`/sync/pull/${deviceId}`, null, { params });
  },
  push: (deviceId: string, changes: any[]) => 
    api.post(`/sync/push/${deviceId}`, { changes }),
  
  // Conflict management
  listConflicts: (deviceId?: string) => {
    const params: any = {};
    if (deviceId) params.device_id = deviceId;
    return api.get('/sync/conflicts', { params });
  },
  resolveConflict: (conflictId: string, resolution: string, resolvedData?: any) => {
    const data: any = { resolution };
    if (resolvedData) data.resolved_data = resolvedData;
    return api.post(`/sync/conflicts/${conflictId}/resolve`, data);
  },
};

// Notifications API
export const notificationsAPI = {
  // Basic operations
  list: (params?: any) => api.get('/notifications', { params }),
  create: (data: any) => api.post('/notifications', data),
  markAsRead: (notificationIds?: string[], category?: string) => 
    api.post('/notifications/mark-read', { notification_ids: notificationIds, category }),
  archive: (notificationId: string) => api.delete(`/notifications/${notificationId}`),
  
  // Statistics
  getStats: () => api.get('/notifications/stats'),
  
  // Templates
  createFromTemplate: (data: any) => api.post('/notifications/from-template', data),
  sendBulk: (data: any) => api.post('/notifications/bulk', data),
  
  // Convenience methods for common notifications
  notifySyncCompleted: (deviceName: string, changesCount: number) =>
    api.post('/notifications/sync/completed', null, { 
      params: { device_name: deviceName, changes_count: changesCount } 
    }),
  notifySyncConflict: (deviceName: string, conflictsCount: number) =>
    api.post('/notifications/sync/conflict', null, { 
      params: { device_name: deviceName, conflicts_count: conflictsCount } 
    }),
  notifyKnowledgeCreated: (title: string) =>
    api.post('/notifications/knowledge/created', null, { params: { title } }),
  notifyImportCompleted: (platform: string, importedCount: number) =>
    api.post('/notifications/import/completed', null, { 
      params: { platform, imported_count: importedCount } 
    }),
  
  // Test endpoint
  test: () => api.get('/notifications/test'),
  createDemo: () => api.post('/notifications/demo'),
};

export default api;
