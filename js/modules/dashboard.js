import { Logger } from './logger.js';
import { RealtimeConnection } from './realtime.js';

/**
 * Main Dashboard controller
 */
export class Dashboard {
    constructor(state, api, wsUrl) {
        this.state = state;
        this.api = api;
        this.realtimeConn = new RealtimeConnection(wsUrl, state);
        this.components = new Map();
        this.initialized = false;
    }

    async init() {
        try {
            Logger.info('Initializing Advanced Dashboard...');
            
            // 1. Apply user theme
            this.applyTheme(this.state.getState('userPrefs').theme);
            
            // 2. Setup WebSocket handlers
            this.setupRealtimeHandlers();
            
            // 3. Connect to WebSocket
            this.realtimeConn.connect().catch(() => Logger.warn('WebSocket connection deferred'));
            
            // 4. Initial content fetch
            await this.loadInitialData();
            
            // 5. Setup polling intervals
            this.setupPolling();
            
            this.initialized = true;
            Logger.info('Dashboard initialized successfully');
        } catch (error) {
            Logger.error('Dashboard initialization failed', error);
        }
    }

    setupRealtimeHandlers() {
        this.realtimeConn.on('metricUpdate', (payload) => {
            this.state.setState('metrics', payload);
            this.state.setState('lastUpdate', new Date());
        });

        this.realtimeConn.on('alert', (payload) => {
            const alerts = this.state.getState('alerts');
            this.state.setState('alerts', [...alerts, payload]);
        });
    }

    async loadInitialData() {
        try {
            const sensorData = await this.api.fetchSensors();
            this.state.setState('metrics', sensorData);
            
            const aqiData = await this.api.fetchAQI();
            if (aqiData.records) {
                this.state.setState('aqi', aqiData.records);
            }
        } catch (error) {
            Logger.warn('Initial data load partially failed');
        }
    }

    setupPolling() {
        const refreshRate = this.state.getState('userPrefs').refreshRate || 1000;
        
        // Polling loop for sensors
        this.refreshInterval = setInterval(async () => {
            if (!this.state.getState('isConnected')) {
                try {
                    const metrics = await this.api.fetchSensors();
                    this.state.setState('metrics', metrics);
                } catch (error) {
                    Logger.debug('Sensor auto-refresh failed');
                }
            }
        }, refreshRate);

        // Polling loop for AQI (every 30 mins)
        setInterval(async () => {
            try {
                const aqi = await this.api.fetchAQI();
                if (aqi.records) this.state.setState('aqi', aqi.records);
            } catch (error) {
                Logger.warn('AQI auto-refresh failed');
            }
        }, 30 * 60 * 1000);
    }

    applyTheme(theme) {
        document.documentElement.className = theme;
        // Also update data-theme for compatibility with user guidelines
        document.documentElement.setAttribute('data-theme', theme);
    }

    addComponent(key, component) {
        this.components.set(key, component);
    }

    destroy() {
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.realtimeConn.disconnect();
        this.components.forEach(c => c.destroy());
    }
}
