// Stairs rendering

function renderStairs(ctx, entities, viewport, sprites, spriteRenderer) {
    if (!entities || !entities.stairs) return;
    
    const stairsX = entities.stairs[0] - viewport.startX;
    const stairsY = entities.stairs[1] - viewport.startY;
    
    if (!isInViewport(stairsX, stairsY)) return;
    
    const pulse = 0.6 + Math.sin(spriteRenderer.animationFrame * 0.3) * 0.4;
    
    // Draw pulsing outline
    ctx.strokeStyle = `rgba(243, 156, 18, ${pulse})`;
    ctx.lineWidth = 3;
    ctx.strokeRect(
        stairsX * TILE_SIZE + 1, 
        stairsY * TILE_SIZE + 1, 
        TILE_SIZE - 2, 
        TILE_SIZE - 2
    );
    
    // Draw inner glow
    ctx.strokeStyle = `rgba(255, 200, 50, ${pulse * 0.5})`;
    ctx.lineWidth = 1;
    ctx.strokeRect(
        stairsX * TILE_SIZE + 4, 
        stairsY * TILE_SIZE + 4, 
        TILE_SIZE - 8, 
        TILE_SIZE - 8
    );
    
    if (sprites.loaded && sprites.dungeonProps && sprites.dungeonProps.complete) {
        renderStairsSprite(ctx, stairsX, stairsY, sprites, spriteRenderer);
    } else {
        renderStairsFallback(ctx, stairsX, stairsY, spriteRenderer);
    }
}

function renderStairsSprite(ctx, stairsX, stairsY, sprites, spriteRenderer) {
    const glowIntensity = 8 + Math.sin(spriteRenderer.animationFrame * 0.3) * 4;
    ctx.shadowBlur = glowIntensity;
    ctx.shadowColor = '#f39c12';
    
    ctx.drawImage(
        sprites.dungeonProps,
        48, 0, 16, 16,
        stairsX * TILE_SIZE, stairsY * TILE_SIZE, TILE_SIZE, TILE_SIZE
    );
    ctx.shadowBlur = 0;
}

function renderStairsFallback(ctx, stairsX, stairsY, spriteRenderer) {
    ctx.fillStyle = '#f39c12';
    const fallbackPulse = 0.8 + Math.sin(spriteRenderer.animationFrame * 0.5) * 0.2;
    ctx.globalAlpha = fallbackPulse;
    ctx.fillRect(stairsX * TILE_SIZE + 2, stairsY * TILE_SIZE + 2, 
                TILE_SIZE - 4, TILE_SIZE - 4);
    
    ctx.fillStyle = '#000';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('↓', stairsX * TILE_SIZE + TILE_SIZE/2, stairsY * TILE_SIZE + TILE_SIZE/2 + 6);
    
    ctx.globalAlpha = 1;
}
