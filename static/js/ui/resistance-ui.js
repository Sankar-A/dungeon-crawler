/**
 * Resistance UI Component
 * Displays active resistance effects
 */

class ResistanceUI {
    constructor() {
        this.container = null;
        this.elementColors = {
            fire: '#ff4400',
            frost: '#00ccff',
            lightning: '#ffff00',
            poison: '#00ff00',
            shadow: '#8800ff',
            holy: '#ffdd00',
            void: '#aa00ff'
        };
        this.createContainer();
    }

    /**
     * Create the resistance UI container
     * @returns {HTMLElement} The container element
     */
    createContainer() {
        const container = document.createElement('div');
        container.id = 'resistance-container';
        container.className = 'resistance-container hidden';
        
        container.innerHTML = `
            <div class="resistance-icon"></div>
            <div class="resistance-content">
                <div class="resistance-element"></div>
                <div class="resistance-turns"></div>
            </div>
        `;
        
        // Append to HUD or body
        const hud = document.getElementById('hud') || document.body;
        hud.appendChild(container);
        this.container = container;
        return container;
    }

    /**
     * Show resistance effect
     * @param {Object} resistanceData - Resistance data from server
     */
    show(resistanceData) {
        if (!this.container) return;
        
        const element = resistanceData.element;
        const reduction = Math.round(resistanceData.reduction * 100);
        const duration = resistanceData.duration;
        
        const iconEl = this.container.querySelector('.resistance-icon');
        const elementEl = this.container.querySelector('.resistance-element');
        const turnsEl = this.container.querySelector('.resistance-turns');
        
        // Set icon and color
        iconEl.textContent = this.getElementIcon(element);
        iconEl.style.color = this.elementColors[element] || '#ffffff';
        
        // Set element text
        elementEl.textContent = `${element.toUpperCase()} -${reduction}%`;
        elementEl.style.color = this.elementColors[element] || '#ffffff';
        
        // Set turns remaining
        turnsEl.textContent = `${duration} turn${duration !== 1 ? 's' : ''}`;
        
        this.container.classList.remove('hidden');
    }

    /**
     * Update turns remaining
     * @param {number} turnsRemaining - Turns remaining
     */
    update(turnsRemaining) {
        if (!this.container) return;
        
        const turnsEl = this.container.querySelector('.resistance-turns');
        turnsEl.textContent = `${turnsRemaining} turn${turnsRemaining !== 1 ? 's' : ''}`;
    }

    /**
     * Hide resistance effect
     */
    hide() {
        if (!this.container) return;
        
        this.container.classList.add('hidden');
    }

    /**
     * Get emoji icon for element
     * @param {string} element - Element type
     * @returns {string} Emoji icon
     */
    getElementIcon(element) {
        const icons = {
            fire: '🔥',
            frost: '❄️',
            lightning: '⚡',
            poison: '☠️',
            shadow: '🌑',
            holy: '✨',
            void: '🌀'
        };
        return icons[element] || '🛡️';
    }
}
