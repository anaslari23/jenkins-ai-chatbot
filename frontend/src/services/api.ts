import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 120000, // 2 min — LLM generation can be slow
});

export interface AskResponse {
    answer: string;
    sources: string[];
}

export interface ApiStatus {
    status: string;
    service: string;
    version: string;
}

export async function askQuestion(question: string): Promise<AskResponse> {
    const response = await apiClient.post<AskResponse>('/ask', { question });
    return response.data;
}

export async function getApiStatus(): Promise<ApiStatus> {
    const response = await apiClient.get<ApiStatus>('/');
    return response.data;
}

export default apiClient;
