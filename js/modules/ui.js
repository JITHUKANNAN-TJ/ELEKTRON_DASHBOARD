import { Logger } from './logger.js';

/**
 * Handles all UI updates and DOM manipulations
 */
export class UI {
    static updateSensors(data) {
        try {
            document.getElementById('sensor-tds').innerText = data.tds_mgl.toFixed(0);
            document.getElementById('sensor-bod').innerText = data.bod_mgl.toFixed(1);
            document.getElementById('sensor-cod').innerText = data.cod_mgl.toFixed(1);
            document.getElementById('sensor-ph').innerText = data.ph_level.toFixed(1);
        } catch (e) {
            Logger.debug('Failed to update sensor UI components');
        }
    }

    static updateAQI(records) {
        if (!records || records.length < 4) return;
        
        for (let i = 0; i < 4; i++) {
            const rec = records[i];
            const valElem = document.getElementById(`sensor-aqi-${i + 1}-val`);
            const labelElem = document.getElementById(`sensor-aqi-${i + 1}-label`);
            
            if (valElem) valElem.innerText = rec.avg_value || rec.max_value || "N/A";
            if (labelElem) labelElem.innerText = `${rec.pollutant_id} (${rec.city})`;
        }
    }

    static updateVideoFeed(src, isPaused) {
        const feedImg = document.getElementById('ai-feed');
        const icon = document.getElementById('pause-icon');
        const text = document.getElementById('pause-text');

        if (isPaused) {
            feedImg.removeAttribute('onerror');
            feedImg.src = "https://placehold.co/1280x540/0f172a/7dd3fc?text=FEED+PAUSED";
            if (icon) icon.innerText = "play_arrow";
            if (text) text.innerText = "Resume";
        } else {
            feedImg.setAttribute('onerror', "this.onerror=null; this.src='https://placehold.co/1280x540/0f172a/38bdf8?text=START+AI+BACKEND';");
            feedImg.src = src;
            if (icon) icon.innerText = "pause";
            if (text) text.innerText = "Pause";
        }
    }

    static setZoom(zoom) {
        const feedImg = document.getElementById('ai-feed');
        if (feedImg) {
            feedImg.style.transform = `scale(${zoom})`;
            feedImg.style.transition = 'transform 0.2s ease-out';
        }
    }

    static showNotification(message, type = 'info') {
        Logger.info(`Notification: ${message} (${type})`);
        // Simple alert for now, could be upgraded to custom toast later
        console.log(`[UI Notification] [${type.toUpperCase()}] ${message}`);
    }
}
