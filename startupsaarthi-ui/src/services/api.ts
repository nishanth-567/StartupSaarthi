/**
 * API service for StartupSaarthi backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // Add admin key if present in localStorage
        const adminKey = localStorage.getItem('admin_key');
        if (adminKey && config.url?.includes('/admin/')) {
            config.headers['X-Admin-Key'] = adminKey;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear admin key
            localStorage.removeItem('admin_key');
        }
        return Promise.reject(error);
    }
);

// Types
export interface QueryRequest {
    query: string;
    deterministic?: boolean;
    language?: string;
}

export interface Source {
    source_id: number;
    document: string;
    page?: number;
    section?: string;
    content_snippet: string;
    metadata?: Record<string, any>;
}

export interface QueryResponse {
    answer: string;
    sources: Source[];
    detected_language: string;
    processing_time_seconds: number;
}

export interface IngestRequest {
    file_path: string;
    document_type: string;
    metadata?: Record<string, any>;
}

export interface IngestResponse {
    success: boolean;
    message: string;
    chunks_created: number;
    document_id?: string;
}

export interface StatsResponse {
    total_documents: number;
    total_chunks: number;
    faiss_index_size_mb: number;
    bm25_index_size_mb: number;
    supported_languages: string[];
    embedding_model: string;
}

// API Methods
export const api = {
    // User endpoints
    async query(request: QueryRequest): Promise<QueryResponse> {
        const response = await apiClient.post<QueryResponse>('/api/query', request);
        return response.data;
    },

    async getSupportedLanguages() {
        const response = await apiClient.get('/api/languages');
        return response.data;
    },

    async healthCheck() {
        const response = await apiClient.get('/health');
        return response.data;
    },

    // Admin endpoints
    async ingestDocument(request: IngestRequest): Promise<IngestResponse> {
        const response = await apiClient.post<IngestResponse>('/api/admin/ingest', request);
        return response.data;
    },

    async reindex(rebuildFaiss = true, rebuildBm25 = true) {
        const response = await apiClient.post('/api/admin/reindex', {
            rebuild_faiss: rebuildFaiss,
            rebuild_bm25: rebuildBm25,
        });
        return response.data;
    },

    async getStats(): Promise<StatsResponse> {
        const response = await apiClient.get<StatsResponse>('/api/admin/stats');
        return response.data;
    },
};

export default api;
