/**
 * Advanced Logger with colorized output and server reporting
 */
export class Logger {
    static INFO = 'INFO';
    static WARN = 'WARN';
    static ERROR = 'ERROR';
    static DEBUG = 'DEBUG';

    static log(message, level = this.INFO, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data
        };

        // Console output
        const color = {
            INFO: 'color: #3b82f6;', // blue
            WARN: 'color: #f59e0b;', // amber
            ERROR: 'color: #ef4444;', // red
            DEBUG: 'color: #10b981;'  // emerald
        };

        const icon = {
            INFO: 'ℹ️',
            WARN: '⚠️',
            ERROR: '❌',
            DEBUG: '🐛'
        };

        console.log(`%c${icon[level]} ${timestamp} [${level}] ${message}`, color[level], data || '');

        // Report critical errors to server (if endpoint exists)
        if (level === this.ERROR) {
            this.reportToServer(logEntry).catch(() => {});
        }
    }

    static info(msg, data) { this.log(msg, this.INFO, data); }
    static warn(msg, data) { this.log(msg, this.WARN, data); }
    static error(msg, data) { this.log(msg, this.ERROR, data); }
    static debug(msg, data) { this.log(msg, this.DEBUG, data); }

    static async reportToServer(logEntry) {
        try {
            await fetch('/api/logs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            });
        } catch (err) {
            // Silently fail if logging server is not available
        }
    }
}
