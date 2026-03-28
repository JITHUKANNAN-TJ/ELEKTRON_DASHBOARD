import { Logger } from './logger.js';

/**
 * WebSocket wrapper with automatic reconnection logic
 */
export class RealtimeConnection {
    constructor(url, state) {
        this.url = url;
        this.state = state;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.maxReconnectDelay = 30000;
        this.messageHandlers = new Map();
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    Logger.info('WebSocket connected');
                    this.state.setState('isConnected', true);
                    this.reconnectAttempts = 0;
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        Logger.error('Message parse error', error);
                    }
                };

                this.ws.onerror = (error) => {
                    Logger.error('WebSocket error', error);
                    reject(error);
                };

                this.ws.onclose = (event) => {
                    Logger.warn('WebSocket disconnected', { code: event.code, reason: event.reason });
                    this.state.setState('isConnected', false);
                    this.reconnect();
                };
            } catch (error) {
                Logger.error('Connection attempt failed', error);
                reject(error);
            }
        });
    }

    handleMessage(data) {
        const { type, payload } = data;
        const handler = this.messageHandlers.get(type);

        if (handler) {
            handler(payload);
        } else {
            Logger.warn(`No handler for message type: ${type}`);
        }
    }

    on(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    send(type, payload) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        } else {
            Logger.warn('WebSocket not open, cannot send message');
        }
    }

    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            Logger.error('Max reconnection attempts reached');
            return;
        }

        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectDelay);
        this.reconnectAttempts++;

        Logger.warn(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect().catch(() => {}), delay);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
