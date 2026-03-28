import { Logger } from './logger.js';

/**
 * Resilient ApiService with automatic retries and exponential backoff
 */
export class ApiService {
    constructor(baseUrl = window.location.origin) {
        this.baseUrl = baseUrl;
        this.timeout = 10000;
        this.retryAttempts = 3;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        let lastError = null;

        for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal,
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });

                if (response.ok) {
                    clearTimeout(timeoutId);
                    return await response.json();
                }

                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            } catch (error) {
                lastError = error;
                if (error.name === 'AbortError') {
                    Logger.warn(`Request timeout reached for ${endpoint}`);
                    break; 
                }
                
                Logger.warn(`Request attempt ${attempt + 1} failed for ${endpoint}`, { error: error.message });

                if (attempt < this.retryAttempts - 1) {
                    await this.delay(1000 * Math.pow(2, attempt)); // Exponential backoff: 1s, 2s, 4s...
                }
            }
        }

        clearTimeout(timeoutId);
        Logger.error('API request failed after retries', { endpoint, error: lastError?.message });
        throw lastError;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Specific domain helpers
    async fetchSensors() { return this.get('/api/sensors'); }
    async fetchAQI(city = 'Coimbatore', limit = 10) { 
        return this.get(`/api/aqi?city=${encodeURIComponent(city)}&limit=${limit}`); 
    }
    async updateCameraUrl(url) { return this.post('/api/camera_url', { url }); }
    async updateCameraStatus(active) { return this.post('/api/camera_status', { active }); }
}
