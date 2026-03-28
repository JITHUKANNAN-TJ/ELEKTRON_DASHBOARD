import { Logger } from './logger.js';

/**
 * Base Component class for UI elements
 */
export class Component {
    constructor(selector, state) {
        this.element = document.querySelector(selector);
        this.state = state;
        this.data = null;
        this.unsubscribers = [];
        
        if (!this.element) {
            Logger.warn(`Element not found for component: ${selector}`);
        }
    }

    render(data) {
        if (!this.element) return;
        this.data = data;
        this.element.innerHTML = this.template();
        this.attachEventListeners();
        this.attachStateListeners();
    }

    template() {
        return '';
    }

    attachEventListeners() {}

    attachStateListeners() {}

    subscribe(key, callback) {
        const unsubscribe = this.state.subscribe(key, callback);
        this.unsubscribers.push(unsubscribe);
    }

    update(data) {
        this.render(data);
    }

    destroy() {
        this.unsubscribers.forEach(unsub => unsub());
    }
}
