// Viewport calculation utilities

function calculateViewport(player) {
    // Use visual position for smooth camera movement
    const visualX = typeof playerVisualX !== 'undefined' ? playerVisualX : player.x;
    const visualY = typeof playerVisualY !== 'undefined' ? playerVisualY : player.y;
    
    // Calculate integer tile positions for rendering
    const startX = Math.floor(visualX - Math.floor(VIEWPORT_WIDTH / 2));
    const startY = Math.floor(visualY - Math.floor(VIEWPORT_HEIGHT / 2));
    
    // Calculate fractional offset for smooth scrolling
    const offsetX = (visualX - Math.floor(visualX)) * TILE_SIZE;
    const offsetY = (visualY - Math.floor(visualY)) * TILE_SIZE;
    
    return {
        startX: startX,
        startY: startY,
        centerX: Math.floor(VIEWPORT_WIDTH / 2),
        centerY: Math.floor(VIEWPORT_HEIGHT / 2),
        visualX: visualX,
        visualY: visualY,
        offsetX: offsetX,
        offsetY: offsetY
    };
}

function isInViewport(screenX, screenY) {
    return screenX >= 0 && screenX < VIEWPORT_WIDTH && 
           screenY >= 0 && screenY < VIEWPORT_HEIGHT;
}

function worldToScreen(worldX, worldY, viewport) {
    return {
        x: worldX - viewport.startX,
        y: worldY - viewport.startY
    };
}
