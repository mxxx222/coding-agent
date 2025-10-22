import axios, { AxiosInstance } from 'axios';
import { ConfigManager } from './configManager';

export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
}

export class ApiClient {
    private client: AxiosInstance;
    private configManager: ConfigManager;

    constructor(configManager: ConfigManager) {
        this.configManager = configManager;
        this.client = axios.create({
            baseURL: this.configManager.getServerUrl(),
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add request interceptor for authentication
        this.client.interceptors.request.use((config) => {
            const apiKey = this.configManager.getApiKey();
            if (apiKey) {
                config.headers.Authorization = `Bearer ${apiKey}`;
            }
            return config;
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    async analyzeCode(code: string, language?: string): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/analyze/code', {
                code,
                language: language || this.configManager.getLanguage()
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async suggestRefactor(code: string, filePath: string, language?: string): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/analyze/refactor', {
                code,
                filePath,
                language: language || this.configManager.getLanguage()
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async generateTest(code: string, filePath: string, framework?: string): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/generate/test', {
                code,
                filePath,
                framework
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async explainCode(code: string, language?: string): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/explain/code', {
                code,
                language: language || this.configManager.getLanguage()
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async optimizeCode(code: string, language?: string): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/optimize/code', {
                code,
                language: language || this.configManager.getLanguage()
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async getIntegrations(): Promise<ApiResponse> {
        try {
            const response = await this.client.get('/api/integrations');
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async setupIntegration(service: string, config: any): Promise<ApiResponse> {
        try {
            const response = await this.client.post('/api/integrations/setup', {
                service,
                config
            });
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    async getHealth(): Promise<ApiResponse> {
        try {
            const response = await this.client.get('/api/health');
            return { success: true, data: response.data };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }
}
