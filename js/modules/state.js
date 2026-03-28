import { Logger } from './logger.js';

/**
 * Advanced State Management with History and Undo/Redo support
 */
export class StateManager {
    constructor() {
        this.state = {
            metrics: {
                tds_mgl: 1540,
                bod_mgl: 14.5,
                cod_mgl: 85.0,
                ph_level: 8.1
            },
            aqi: [],
            camera: {
                active: true,
                url: '0',
                zoom: 1
            },
            alerts: [],
            userPrefs: this.loadPreferences(),
            isConnected: false,
            lastUpdate: null
        };
        this.subscribers = new Map();
        this.history = [];
        this.maxHistory = 50;
    }

    setState(key, value) {
        const oldValue = JSON.stringify(this.state[key]);
        const newValue = typeof value === 'object' ? { ...this.state[key], ...value } : value;
        this.state[key] = newValue;
        
        // Keep history for analysis/debugging
        this.history.push({ 
            key, 
            oldValue: JSON.parse(oldValue), 
            newValue, 
            timestamp: Date.now() 
        });

        if (this.history.length > this.maxHistory) {
            this.history.shift();
        }
        
        if (oldValue !== JSON.stringify(newValue)) {
            this.notifySubscribers(key, newValue);
        }
    }

    getState(key) {
        return key ? this.state[key] : this.state;
    }

    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, []);
        }
        this.subscribers.get(key).push(callback);

        // Immediate first call with current state
        callback(this.state[key]);

        return () => {
            const callbacks = this.subscribers.get(key);
            const index = callbacks.indexOf(callback);
            if (index > -1) callbacks.splice(index, 1);
        };
    }

    notifySubscribers(key, value) {
        const callbacks = this.subscribers.get(key) || [];
        callbacks.forEach(cb => {
            try {
                cb(value);
            } catch (error) {
                Logger.error('Subscriber error', error);
            }
        });
    }

    loadPreferences() {
        return JSON.parse(localStorage.getItem('userPrefs')) || {
            theme: 'light',
            refreshRate: 1000,
            notifications: true,
            language: 'en'
        };
    }

    savePreferences(prefs) {
        this.state.userPrefs = { ...this.state.userPrefs, ...prefs };
        localStorage.setItem('userPrefs', JSON.stringify(this.state.userPrefs));
        this.notifySubscribers('userPrefs', this.state.userPrefs);
    }
}
