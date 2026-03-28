/**
 * Utility functions for HydraMetric Dashboard
 */
export class Utils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static formatNumber(num, decimals = 2) {
        return Number(num).toFixed(decimals);
    }

    static getStatus(value, key) {
        const thresholds = {
            tds_mgl: { warning: 1000, danger: 2000 },
            bod_mgl: { warning: 10, danger: 30 },
            cod_mgl: { warning: 50, danger: 150 },
            ph_level: { low: 6.5, high: 8.5 }
        };

        const t = thresholds[key];
        if (!t) return 'safe';

        if (key === 'ph_level') {
            return (value < t.low || value > t.high) ? 'danger' : 'safe';
        }

        if (value >= t.danger) return 'danger';
        if (value >= t.warning) return 'warning';
        return 'safe';
    }
}
