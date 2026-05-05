// Enhanced sprite rendering with animations and effects

class SpriteRenderer {
    constructor() {
        this.animationFrame = 0;
        this.animationSpeed = 10;
        this.frameCounter = 0;
    }
    
    update() {
        this.frameCounter++;
        if (this.frameCounter >= this.animationSpeed) {
            this.animationFrame = (this.animationFrame + 1) % 4;
            this.frameCounter = 0;
        }
    }
    
    // Draw player with animation
    drawPlayer(ctx, x, y, size, sprites) {
        if (sprites.loaded && sprites.objects) {
            // Animate player (bobbing effect)
            const offset = Math.sin(this.animationFrame * 0.5) * 2;
            ctx.drawImage(
                sprites.objects,
                16, 0, 16, 16,
                x, y + offset, size, size
            );
            
            // Add glow effect
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#3498db';
            ctx.drawImage(
                sprites.objects,
                16, 0, 16, 16,
                x, y + offset, size, size
            );
            ctx.shadowBlur = 0;
        } else {
            // Fallback with gradient
            const gradient = ctx.createRadialGradient(
                x + size/2, y + size/2, 0,
                x + size/2, y + size/2, size/2
            );
            gradient.addColorStop(0, '#5dade2');
            gradient.addColorStop(1, '#2874a6');
            ctx.fillStyle = gradient;
            ctx.fillRect(x + 2, y + 2, size - 4, size - 4);
        }
    }
    
    // Draw enemy with animation
    drawEnemy(ctx, x, y, size, isBoss, sprites) {
        if (sprites.loaded && sprites.fire) {
            // Animate fire sprite
            const frame = Math.floor(this.animationFrame / 2) % 2;
            const row = isBoss ? 1 : 0;
            ctx.drawImage(
                sprites.fire,
                frame * 16, row * 16, 16, 16,
                x, y, size, size
            );
            
            // Boss glow
            if (isBoss) {
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#9b59b6';
                ctx.drawImage(
                    sprites.fire,
                    frame * 16, row * 16, 16, 16,
                    x, y, size, size
                );
                ctx.shadowBlur = 0;
            }
        } else {
            // Fallback with gradient
            const color1 = isBoss ? '#9b59b6' : '#e74c3c';
            const color2 = isBoss ? '#6c3483' : '#c0392b';
            const gradient = ctx.createRadialGradient(
                x + size/2, y + size/2, 0,
                x + size/2, y + size/2, size/2
            );
            gradient.addColorStop(0, color1);
            gradient.addColorStop(1, color2);
            ctx.fillStyle = gradient;
            ctx.fillRect(x + 2, y + 2, size - 4, size - 4);
        }
    }
    
    // Draw stairs with glow
    drawStairs(ctx, x, y, size, sprites) {
        if (sprites.loaded && sprites.objects) {
            // Pulsing glow effect
            const glowIntensity = 10 + Math.sin(this.animationFrame) * 5;
            ctx.shadowBlur = glowIntensity;
            ctx.shadowColor = '#f39c12';
            ctx.drawImage(
                sprites.objects,
                0, 32, 16, 16,
                x, y, size, size
            );
            ctx.shadowBlur = 0;
        } else {
            // Fallback with pulsing
            const pulse = 0.8 + Math.sin(this.animationFrame * 0.5) * 0.2;
            ctx.fillStyle = '#f39c12';
            ctx.globalAlpha = pulse;
            ctx.fillRect(x + 2, y + 2, size - 4, size - 4);
            ctx.globalAlpha = 1;
        }
    }
    
    // Draw chest or treasure
    drawChest(ctx, x, y, size, sprites) {
        if (sprites.loaded && sprites.doors) {
            ctx.drawImage(
                sprites.doors,
                32, 0, 16, 16,  // Chest sprite
                x, y, size, size
            );
        } else {
            ctx.fillStyle = '#f39c12';
            ctx.fillRect(x + 4, y + 4, size - 8, size - 8);
        }
    }
    
    // Draw HP bar with style
    drawHPBar(ctx, x, y, width, hpPercent) {
        // Background
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(x, y, width, 3);
        
        // HP fill with gradient
        const gradient = ctx.createLinearGradient(x, y, x + width * hpPercent, y);
        if (hpPercent > 0.5) {
            gradient.addColorStop(0, '#2ecc71');
            gradient.addColorStop(1, '#27ae60');
        } else if (hpPercent > 0.25) {
            gradient.addColorStop(0, '#f39c12');
            gradient.addColorStop(1, '#e67e22');
        } else {
            gradient.addColorStop(0, '#e74c3c');
            gradient.addColorStop(1, '#c0392b');
        }
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, width * hpPercent, 3);
        
        // Border
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, width, 3);
    }
    
    // Particle effects for combat
    drawCombatEffect(ctx, x, y, type) {
        ctx.save();
        ctx.globalAlpha = 0.7;
        
        if (type === 'hit') {
            // Red impact
            ctx.fillStyle = '#e74c3c';
            for (let i = 0; i < 5; i++) {
                const angle = (Math.PI * 2 * i) / 5;
                const px = x + Math.cos(angle) * 8;
                const py = y + Math.sin(angle) * 8;
                ctx.fillRect(px, py, 3, 3);
            }
        } else if (type === 'crit') {
            // Yellow burst
            ctx.fillStyle = '#f39c12';
            ctx.font = 'bold 12px Arial';
            ctx.fillText('CRIT!', x - 15, y - 10);
        } else if (type === 'dodge') {
            // Blue swirl
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        ctx.restore();
    }
}

// Export for use in main game
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpriteRenderer;
}
