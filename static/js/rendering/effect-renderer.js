/**
 * Effect Renderer
 * Renders visual effects like blink teleport and telegraph warnings
 */

class EffectRenderer {
    constructor(ctx, tileSize) {
        this.ctx = ctx;
        this.tileSize = tileSize;
        this.activeEffects = [];
        this.telegraphWarning = null;
    }

    /**
     * Add a blink effect (start or end position)
     * @param {number} x - World X coordinate
     * @param {number} y - World Y coordinate
     * @param {string} type - 'start' or 'end'
     */
    addBlinkEffect(x, y, type) {
        const effect = {
            type: 'blink',
            subtype: type,
            x: x,
            y: y,
            createdAt: Date.now(),
            duration: 500 // 500ms
        };
        this.activeEffects.push(effect);
    }

    /**
     * Add a telegraph warning above boss
     * @param {number} x - World X coordinate
     * @param {number} y - World Y coordinate
     * @param {string} abilityName - Name of the ability
     */
    addTelegraphWarning(x, y, abilityName) {
        this.telegraphWarning = {
            x: x,
            y: y,
            abilityName: abilityName,
            createdAt: Date.now()
        };
    }

    /**
     * Remove telegraph warning
     */
    removeTelegraphWarning() {
        this.telegraphWarning = null;
    }

    /**
     * Render all active effects
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     */
    render(cameraX, cameraY) {
        const now = Date.now();
        
        // Remove expired effects
        this.activeEffects = this.activeEffects.filter(effect => {
            const elapsed = now - effect.createdAt;
            return elapsed < effect.duration;
        });
        
        // Render each active effect
        for (const effect of this.activeEffects) {
            if (effect.type === 'blink') {
                this.renderBlinkEffect(effect, cameraX, cameraY, now);
            }
        }
        
        // Render telegraph warning
        if (this.telegraphWarning) {
            this.renderTelegraphWarning(this.telegraphWarning, cameraX, cameraY, now);
        }
    }

    /**
     * Render blink teleport effect
     * @param {Object} effect - Effect data
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     * @param {number} now - Current timestamp
     */
    renderBlinkEffect(effect, cameraX, cameraY, now) {
        const elapsed = now - effect.createdAt;
        const progress = elapsed / effect.duration;
        const alpha = 1 - progress; // Fade out
        
        const screenX = (effect.x - cameraX) * this.tileSize + this.tileSize / 2;
        const screenY = (effect.y - cameraY) * this.tileSize + this.tileSize / 2;
        
        // Purple expanding circle
        const radius = 5 + progress * 15;
        this.ctx.strokeStyle = `rgba(150, 0, 255, ${alpha})`;
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // 8 purple particles in circle pattern
        for (let i = 0; i < 8; i++) {
            const angle = (Math.PI * 2 * i) / 8;
            const particleRadius = radius + 5;
            const px = screenX + Math.cos(angle) * particleRadius;
            const py = screenY + Math.sin(angle) * particleRadius;
            
            this.ctx.fillStyle = `rgba(150, 0, 255, ${alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(px, py, 2, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }

    /**
     * Render telegraph warning above boss
     * @param {Object} warning - Warning data
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     * @param {number} now - Current timestamp
     */
    renderTelegraphWarning(warning, cameraX, cameraY, now) {
        const screenX = (warning.x - cameraX) * this.tileSize + this.tileSize / 2;
        const screenY = (warning.y - cameraY) * this.tileSize - 20;
        
        // Pulsing effect
        const pulse = Math.sin(now / 200) * 0.3 + 0.7;
        
        // Red warning triangle
        this.ctx.save();
        this.ctx.globalAlpha = pulse;
        this.ctx.fillStyle = '#ff0000';
        this.ctx.beginPath();
        this.ctx.moveTo(screenX, screenY - 10);
        this.ctx.lineTo(screenX - 8, screenY + 5);
        this.ctx.lineTo(screenX + 8, screenY + 5);
        this.ctx.closePath();
        this.ctx.fill();
        
        // White exclamation mark
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('!', screenX, screenY);
        
        this.ctx.restore();
    }
}
