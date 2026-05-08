// Death animation rendering

function renderDeathAnimations(ctx, deathAnimations, viewport, sprites) {
    for (const deathAnim of deathAnimations) {
        const screen = worldToScreen(deathAnim.x, deathAnim.y, viewport);
        
        if (isInViewport(screen.x, screen.y)) {
            renderDeathAnimation(ctx, screen.x, screen.y, deathAnim, sprites);
        }
    }
}

function renderDeathAnimation(ctx, screenX, screenY, deathAnim, sprites) {
    const deathSprite = deathAnim.isBoss ? sprites.enemyOrcDeath : sprites.enemySkeletonDeath;
    
    if (sprites.loaded && deathSprite && deathSprite.complete) {
        ctx.save();
        ctx.imageSmoothingEnabled = false;
        
        const frameWidth = deathAnim.isBoss ? 64 : 96;
        const frameHeight = 64;
        const offsetX = (frameWidth - TILE_SIZE) / 2;
        const offsetY = frameHeight - TILE_SIZE;
        
        ctx.drawImage(
            deathSprite,
            deathAnim.frame * frameWidth, 0, frameWidth, frameHeight,
            screenX * TILE_SIZE - offsetX, screenY * TILE_SIZE - offsetY, frameWidth, frameHeight
        );
        
        ctx.restore();
    } else {
        // Fallback
        ctx.fillStyle = '#ff0000';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('X', screenX * TILE_SIZE + TILE_SIZE/2, screenY * TILE_SIZE + TILE_SIZE/2 + 8);
    }
}
