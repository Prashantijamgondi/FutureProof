import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: `${API_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            if (typeof window !== 'undefined') {
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// API Methods
export const projectsAPI = {
    getAll: () => api.get('/projects'),
    getById: (id: number) => api.get(`/projects/${id}`),
    create: (data: { name: string; repo_url: string }) => api.post('/projects', data),
    delete: (id: number) => api.delete(`/projects/${id}`),
};

export const analysisAPI = {
    analyze: (projectId: number) => api.post(`/analysis/${projectId}/analyze`),
    getAnalysis: (projectId: number) => api.get(`/analysis/${projectId}`),
};

export const transformAPI = {
    getPreview: (projectId: number) => api.get(`/transform/${projectId}/transformation-preview`),
    transform: (projectId: number) => api.post(`/transform/${projectId}/transform`),
    maximumTransform: (projectId: number, data: any) =>
        api.post(`/transform/${projectId}/maximum`, data),
    mlTransform: (projectId: number, data: any) =>
        api.post(`/transform/${projectId}/ml-transform`, data),
    reactOptimize: (projectId: number, data: any) =>
        api.post(`/transform/${projectId}/react-optimize`, data),
    getCapabilities: () => api.get('/transform/capabilities'),
    download: (projectId: number) =>
        api.get(`/transform/${projectId}/download`, { responseType: 'blob' }),
};

export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats'),
    getRecent: () => api.get('/dashboard/recent'),
};
