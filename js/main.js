import { StateManager } from './modules/state.js';
import { ApiService } from './modules/api.js';
import { Dashboard } from './modules/dashboard.js';
import { MetricCard } from './modules/metricCard.js';
import { Logger } from './modules/logger.js';
import { Utils } from './modules/utils.js';

/**
 * Main application entry point
 */
document.addEventListener('DOMContentLoaded', async () => {
    Logger.info('Starting Advanced HydraMetric Application...');

    // 1. Initialize core services
    const state = new StateManager();
    const api = new ApiService(window.location.origin);
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProto}//${window.location.host}/ws`;

    // 2. Initialize dashboard controller
    const dashboard = new Dashboard(state, api, wsUrl);

    // 3. Initialize components
    const metrics = [
        { id: 'tds', name: 'TDS Level', unit: 'mg/L', key: 'tds_mgl' },
        { id: 'bod', name: 'BOD Level', unit: 'mg/L', key: 'bod_mgl' },
        { id: 'cod', name: 'COD Level', unit: 'mg/L', key: 'cod_mgl' },
        { id: 'ph', name: 'pH Level', unit: 'pH', key: 'ph_level' }
    ];

    metrics.forEach(m => {
        const card = new MetricCard(`#metric-${m.id}`, state, {
            id: m.id,
            name: m.name,
            value: 0,
            unit: m.unit,
            status: 'safe'
        });
        dashboard.addComponent(m.key, card);
    });

    // 4. Start the dashboard
    try {
        await dashboard.init();

        // 5. Global compatibility layer for HTML actions
        window.toggleFeed = async () => {
            const current = state.getState('camera');
            const nextActive = !current.active;
            await api.updateCameraStatus(nextActive);
            state.setState('camera', { active: nextActive });
            
            // Refresh feed element
            const feedImg = document.getElementById('ai-feed');
            if (nextActive) {
                feedImg.src = `/video_feed?t=${Date.now()}`;
                document.getElementById('pause-icon').innerText = 'pause';
                document.getElementById('pause-text').innerText = 'Pause';
            } else {
                feedImg.src = "https://placehold.co/1280x540/0f172a/7dd3fc?text=FEED+PAUSED";
                document.getElementById('pause-icon').innerText = 'play_arrow';
                document.getElementById('pause-text').innerText = 'Resume';
            }
        };

        window.zoomFeed = (amt) => {
            let zoom = state.getState('camera').zoom + amt;
            zoom = Math.max(1, Math.min(zoom, 4));
            state.setState('camera', { zoom });
            document.getElementById('ai-feed').style.transform = `scale(${zoom})`;
        };

        window.resetZoom = () => {
            state.setState('camera', { zoom: 1 });
            document.getElementById('ai-feed').style.transform = `scale(1)`;
        };

        window.toggleTheme = () => {
            const current = state.getState('userPrefs').theme;
            const next = current === 'light' ? 'dark' : 'light';
            state.savePreferences({ theme: next });
            dashboard.applyTheme(next);
        };

        window.updateCameraUrl = async (fixedUrl = null) => {
            const url = fixedUrl || document.getElementById('camera-url-input').value;
            if (!url) return;
            const res = await api.updateCameraUrl(url);
            if (res.status === 'success') {
                state.setState('camera', { url, active: true });
                document.getElementById('ai-feed').src = `/video_feed?t=${Date.now()}`;
            }
        };

        // 6. Subscribe components to state
        state.subscribe('metrics', (data) => {
            metrics.forEach(m => {
                const card = dashboard.components.get(m.key);
                if (card) {
                    const val = data[m.key];
                    card.updateValue(val);
                    // Update status badge if needed
                    card.metric.status = Utils.getStatus(val, m.key);
                    card.render(card.metric);
                }
            });
        });

        state.subscribe('aqi', (records) => {
            if (!records || records.length < 4) return;
            for (let i = 0; i < 4; i++) {
                const rec = records[i];
                document.getElementById(`sensor-aqi-${i + 1}-val`).innerText = rec.avg_value || rec.max_value || "N/A";
                document.getElementById(`sensor-aqi-${i + 1}-label`).innerText = `${rec.pollutant_id} (${rec.city})`;
            }
        });

    } catch (error) {
        Logger.error('Application startup failed', error);
    }
});
