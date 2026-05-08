// Debug mode rendering

function renderDebugInfo(ctx, player, debugMode) {
    if (!debugMode) return;
    
    // Draw tile boundaries
    ctx.strokeStyle = 'rgba(255, 255, 0, 0.3)';
    ctx.lineWidth = 1;
    for (let y = 0; y < VIEWPORT_HEIGHT; y++) {
        for (let x = 0; x < VIEWPORT_WIDTH; x++) {
            ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        }
    }
    
    // Draw coordinate labels
    ctx.fillStyle = 'rgba(255, 255, 0, 0.8)';
    ctx.font = '8px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Player: (${player.x}, ${player.y})`, 5, 15);
    ctx.fillText('Press F1 to toggle debug', 5, 30);
}
