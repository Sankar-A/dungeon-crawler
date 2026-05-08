// Viewport calculation utilities

function calculateViewport(player) {
    return {
        startX: player.x - Math.floor(VIEWPORT_WIDTH / 2),
        startY: player.y - Math.floor(VIEWPORT_HEIGHT / 2),
        centerX: Math.floor(VIEWPORT_WIDTH / 2),
        centerY: Math.floor(VIEWPORT_HEIGHT / 2)
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
