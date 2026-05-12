/**
 * Attack Zone Renderer
 * Renders attack zones (red danger areas) and blink targeting (blue valid destinations)
 */

class AttackZoneRenderer {
    constructor(ctx, tileSize) {
        this.ctx = ctx;
        this.tileSize = tileSize;
        this.activeZones = [];
    }

    /**
     * Add a new attack zone to render
     * @param {Array} tiles - Array of {x, y} tile coordinates
     * @param {string} zoneType - Type of zone (cone, circle, line, etc.)
     */
    addZone(tiles, zoneType) {
        const zone = {
            tiles: tiles,
            type: zoneType,
            alpha: 0,
            createdAt: Date.now()
        };
        this.activeZones.push(zone);
    }

    /**
     * Clear all active zones
     */
    clearZones() {
        this.activeZones = [];
    }

    /**
     * Render all active attack zones with fade-in animation
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     */
    render(cameraX, cameraY) {
        const now = Date.now();
        
        for (const zone of this.activeZones) {
            // Calculate fade-in alpha (0.3 seconds)
            const elapsed = now - zone.createdAt;
            zone.alpha = Math.min(1, elapsed / 300);
            
            // Render each tile in the zone
            for (const tile of zone.tiles) {
                this.renderZoneTile(tile.x, tile.y, zone.alpha, cameraX, cameraY);
            }
        }
    }

    /**
     * Render a single zone tile
     * @param {number} worldX - World X coordinate
     * @param {number} worldY - World Y coordinate
     * @param {number} alpha - Alpha multiplier for fade-in
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     */
    renderZoneTile(worldX, worldY, alpha, cameraX, cameraY) {
        const screenX = (worldX - cameraX) * this.tileSize;
        const screenY = (worldY - cameraY) * this.tileSize;
        
        // Red overlay
        this.ctx.fillStyle = `rgba(255, 0, 0, ${0.5 * alpha})`;
        this.ctx.fillRect(screenX, screenY, this.tileSize, this.tileSize);
        
        // Red border
        this.ctx.strokeStyle = `rgba(200, 0, 0, ${0.8 * alpha})`;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(screenX, screenY, this.tileSize, this.tileSize);
    }

    /**
     * Render blink targeting overlay
     * @param {Array} validTiles - Array of {x, y} valid destination tiles
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     */
    renderBlinkTargeting(validTiles, cameraX, cameraY) {
        if (!validTiles || validTiles.length === 0) {
            return;
        }
        
        for (const tile of validTiles) {
            this.renderBlinkTile(tile.x, tile.y, cameraX, cameraY);
        }
    }

    /**
     * Render a single blink targeting tile
     * @param {number} worldX - World X coordinate
     * @param {number} worldY - World Y coordinate
     * @param {number} cameraX - Camera X offset
     * @param {number} cameraY - Camera Y offset
     */
    renderBlinkTile(worldX, worldY, cameraX, cameraY) {
        const screenX = (worldX - cameraX) * this.tileSize;
        const screenY = (worldY - cameraY) * this.tileSize;
        
        // Blue overlay
        this.ctx.fillStyle = 'rgba(0, 100, 255, 0.3)';
        this.ctx.fillRect(screenX, screenY, this.tileSize, this.tileSize);
        
        // Blue border
        this.ctx.strokeStyle = 'rgba(0, 150, 255, 0.8)';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(screenX, screenY, this.tileSize, this.tileSize);
    }
}
