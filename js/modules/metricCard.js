import { Component } from './component.js';

/**
 * MetricCard component for displaying river telemetry data
 */
export class MetricCard extends Component {
    constructor(selector, state, metric) {
        super(selector, state);
        this.metric = metric; // { id, name, value, unit, status, icon }
    }

    template() {
        const { name, value, unit, status, id } = this.metric;
        const statusColors = {
            'safe': 'bg-secondary/10 text-secondary',
            'warning': 'bg-tertiary/10 text-tertiary',
            'danger': 'bg-error/10 text-error'
        };

        return `
            <div class="bg-surface-container-lowest p-4 rounded-xl border border-outline-variant/10 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-4">
                    <span class="text-[10px] font-bold text-on-surface-variant">${id.toUpperCase()}</span>
                    <span class="text-[8px] px-2 py-0.5 ${statusColors[status] || 'bg-outline/10 text-outline'} rounded-full font-black uppercase">${status}</span>
                </div>
                <p class="text-xl font-bold text-on-surface"><span class="metric-value">${typeof value === 'number' ? value.toFixed(1) : value}</span> <span class="text-[10px] text-outline font-normal">${unit}</span></p>
                <p class="text-[10px] text-on-surface-variant mt-1">${name}</p>
            </div>
        `;
    }

    updateValue(newValue) {
        this.metric.value = newValue;
        if (this.element) {
            const valueEl = this.element.querySelector('.metric-value');
            if (valueEl) {
                valueEl.textContent = typeof newValue === 'number' ? newValue.toFixed(1) : newValue;
                valueEl.classList.add('text-primary');
                setTimeout(() => valueEl.classList.remove('text-primary'), 500);
            }
        }
    }
}
