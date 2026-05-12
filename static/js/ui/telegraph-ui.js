/**
 * Telegraph UI Component
 * Displays telegraph countdown and warnings
 */

class TelegraphUI {
    constructor() {
        this.container = null;
        this.activeTelegraph = null;
        this.createContainer();
    }

    /**
     * Create the telegraph UI container
     * @returns {HTMLElement} The container element
     */
    createContainer() {
        const container = document.createElement('div');
        container.id = 'telegraph-container';
        container.className = 'telegraph-container hidden';
        
        container.innerHTML = `
            <div class="telegraph-warning-icon">⚠️</div>
            <div class="telegraph-content">
                <div class="telegraph-boss-name"></div>
                <div class="telegraph-ability-name"></div>
                <div class="telegraph-countdown"></div>
            </div>
        `;
        
        document.body.appendChild(container);
        this.container = container;
        return container;
    }

    /**
     * Show telegraph warning
     * @param {Object} telegraphData - Telegraph data from server
     */
    show(telegraphData) {
        if (!this.container) return;
        
        this.activeTelegraph = telegraphData;
        
        const bossNameEl = this.container.querySelector('.telegraph-boss-name');
        const abilityNameEl = this.container.querySelector('.telegraph-ability-name');
        const countdownEl = this.container.querySelector('.telegraph-countdown');
        
        bossNameEl.textContent = telegraphData.boss_name || 'Boss';
        abilityNameEl.textContent = telegraphData.ability.name || 'Special Attack';
        
        this.updateCountdown(telegraphData.ability.telegraph_turns);
        
        this.container.classList.remove('hidden');
    }

    /**
     * Update countdown display
     * @param {number} turnsRemaining - Turns remaining
     */
    update(turnsRemaining) {
        this.updateCountdown(turnsRemaining);
    }

    /**
     * Update countdown text and color
     * @param {number} turnsRemaining - Turns remaining
     */
    updateCountdown(turnsRemaining) {
        if (!this.container) return;
        
        const countdownEl = this.container.querySelector('.telegraph-countdown');
        countdownEl.textContent = `${turnsRemaining} turn${turnsRemaining !== 1 ? 's' : ''} remaining`;
        
        // Color code based on urgency
        if (turnsRemaining === 1) {
            countdownEl.style.color = '#ff0000'; // Red
        } else if (turnsRemaining === 2) {
            countdownEl.style.color = '#ff8800'; // Orange
        } else {
            countdownEl.style.color = '#ffff00'; // Yellow
        }
    }

    /**
     * Hide telegraph warning
     */
    hide() {
        if (!this.container) return;
        
        this.container.classList.add('hidden');
        this.activeTelegraph = null;
    }
}
