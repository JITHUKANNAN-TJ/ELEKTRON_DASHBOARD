import { Logger } from './modules/logger.js';
import { ApiService } from './modules/api.js';
import { StateManager } from './modules/state.js';
import { ThemeManager } from './modules/theme.js';
import { UI } from './modules/ui.js';

class App {
    constructor() {
        this.api = new ApiService();
        this.state = new StateManager();
        this.theme = new ThemeManager();
        
        this.init();
    }

    init() {
        Logger.info('Initializing HydraMetric Dashboard...');

        // 1. Subscribe UI to State Changes
        this.state.subscribe('sensors', (data) => UI.updateSensors(data));
        this.state.subscribe('aqi', (records) => UI.updateAQI(records));
        this.state.subscribe('camera', (camState) => {
            const feedUrl = `/video_feed?t=${new Date().getTime()}`;
            UI.updateVideoFeed(feedUrl, !camState.active);
            UI.setZoom(camState.zoom);
        });

        // 2. Setup Polling
        this.startPolling();

        // 3. Bind Global Functions for HTML compatibility (temporary)
        window.toggleFeed = () => this.toggleFeed();
        window.zoomFeed = (amt) => this.zoomFeed(amt);
        window.resetZoom = () => this.resetZoom();
        window.updateCameraUrl = (fixedUrl) => this.updateCameraUrl(fixedUrl);
        window.toggleTheme = () => this.toggleTheme();

        Logger.info('Dashboard Initialized successfully.');
    }

    startPolling() {
        // Sensor polling (every 1s)
        setInterval(async () => {
            try {
                const data = await this.api.fetchSensors();
                this.state.setState('sensors', data);
            } catch (e) {
                Logger.debug('Sensor backend offline');
            }
        }, 1000);

        // AQI polling (every 30 mins)
        const fetchAQI = async () => {
            try {
                const data = await this.api.fetchAQI();
                if (data.records) {
                    this.state.setState('aqi', data.records);
                }
            } catch (e) {
                Logger.warn('AQI API Error');
            }
        };
        fetchAQI();
        setInterval(fetchAQI, 30 * 60 * 1000);
    }

    async toggleFeed() {
        const current = this.state.getState('camera');
        const nextActive = !current.active;
        
        try {
            await this.api.updateCameraStatus(nextActive);
            this.state.setState('camera', { active: nextActive });
        } catch (e) {
            UI.showNotification('Failed to toggle camera', 'error');
        }
    }

    zoomFeed(amt) {
        let zoom = this.state.getState('camera').zoom + amt;
        zoom = Math.max(1, Math.min(zoom, 4));
        this.state.setState('camera', { zoom });
    }

    resetZoom() {
        this.state.setState('camera', { zoom: 1 });
    }

    async updateCameraUrl(fixedUrl = null) {
        const input = document.getElementById('camera-url-input');
        const url = fixedUrl || input.value;
        if (!url) return;

        try {
            const res = await this.api.updateCameraUrl(url);
            if (res.status === 'success') {
                this.state.setState('camera', { url, active: true });
                UI.showNotification('Camera feed updated', 'success');
            }
        } catch (e) {
            UI.showNotification('Failed to update camera URL', 'error');
        }
    }

    toggleTheme() {
        const isDark = this.theme.toggle();
        this.state.setState('theme', isDark ? 'dark' : 'light');
    }
}

// Global instance
window.app = new App();
