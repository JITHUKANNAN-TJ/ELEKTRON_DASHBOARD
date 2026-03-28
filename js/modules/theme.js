/**
 * Theme Manager for Light/Dark mode
 */
export class ThemeManager {
    constructor() {
        this.isDark = localStorage.getItem('theme') === 'dark';
        this.apply();
    }

    toggle() {
        this.isDark = !this.isDark;
        localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
        this.apply();
        return this.isDark;
    }

    apply() {
        if (this.isDark) {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.add('light');
            document.documentElement.classList.remove('dark');
        }
    }

    getTheme() {
        return this.isDark ? 'dark' : 'light';
    }
}
