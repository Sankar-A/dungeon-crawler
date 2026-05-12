/**
 * Cooldown UI Component
 * Displays blink cooldown with circular progress indicator
 */

class CooldownUI {
    constructor() {
        this.container = null;
        this.cooldownEnd = 0;
        this.maxCooldown = 0;
        this.createContainer();
    }

    /**
     * Create the cooldown UI container
     * @returns {HTMLElement} The container element
     */
    createContainer() {
        const container = document.createElement('div');
        container.id = 'blink-cooldown';
        container.className = 'blink-cooldown hidden';
        
        // SVG circle for progress indicator
        const radius = 25;
        const circumference = 2 * Math.PI * radius;
        
        container.innerHTML = `
            <svg width="60" height="60" class="cooldown-svg">
                <circle class="cooldown-bg" cx="30" cy="30" r="${radius}" 
                        fill="none" stroke="#333" stroke-width="4"/>
                <circle class="cooldown-progress" cx="30" cy="30" r="${radius}" 
                        fill="none" stroke="#8800ff" stroke-width="4"
                        stroke-dasharray="${circumference}" 
                        stroke-dashoffset="${circumference}"
                        transform="rotate(-90 30 30)"/>
            </svg>
            <div class="cooldown-label">Blink</div>
            <div class="cooldown-text">0s</div>
        `;
        
        // Append to HUD or body
        const hud = document.getElementById('hud') || document.body;
        hud.appendChild(container);
        this.container = container;
        return container;
    }

    /**
     * Start cooldown timer
     * @param {number} cooldownSeconds - Cooldown duration in seconds
     */
    startCooldown(cooldownSeconds) {
        if (!this.container) return;
        
        this.cooldownEnd = Date.now() + (cooldownSeconds * 1000);
        this.maxCooldown = cooldownSeconds;
        this.container.classList.remove('hidden');
    }

    /**
     * Update cooldown display (called each frame)
     */
    update() {
        if (!this.container || this.cooldownEnd === 0) return;
        
        const now = Date.now();
        const remaining = Math.max(0, this.cooldownEnd - now);
        const remainingSeconds = Math.ceil(remaining / 1000);
        
        if (remaining <= 0) {
            this.hide();
            return;
        }
        
        // Update progress circle
        const progress = 1 - (remaining / (this.maxCooldown * 1000));
        this.updateProgress(progress);
        
        // Update text
        const textEl = this.container.querySelector('.cooldown-text');
        textEl.textContent = `${remainingSeconds}s`;
    }

    /**
     * Update SVG progress circle
     * @param {number} progress - Progress from 0 to 1
     */
    updateProgress(progress) {
        const circle = this.container.querySelector('.cooldown-progress');
        const radius = 25;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference * (1 - progress);
        circle.style.strokeDashoffset = offset;
    }

    /**
     * Render (called each frame for smooth animation)
     */
    render() {
        this.update();
    }

    /**
     * Hide cooldown display
     */
    hide() {
        if (!this.container) return;
        
        this.container.classList.add('hidden');
        this.cooldownEnd = 0;
        this.maxCooldown = 0;
    }
}
