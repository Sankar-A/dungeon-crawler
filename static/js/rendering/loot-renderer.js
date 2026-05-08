// Loot drop rendering

function renderLootDrops(ctx, lootDrops, player, viewport, spriteRenderer) {
    for (const loot of lootDrops) {
        const screen = worldToScreen(loot.x, loot.y, viewport);
        
        if (isInViewport(screen.x, screen.y)) {
            renderLootDrop(ctx, screen.x, screen.y, loot, player, spriteRenderer);
        }
    }
}

function renderLootDrop(ctx, screenX, screenY, loot, player, spriteRenderer) {
    const pulse = 0.5 + Math.sin(spriteRenderer.animationFrame * 0.4) * 0.5;
    
    // Glow effect
    ctx.save();
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#f39c12';
    ctx.fillStyle = `rgba(243, 156, 18, ${pulse * 0.6})`;
    ctx.beginPath();
    ctx.arc(
        screenX * TILE_SIZE + TILE_SIZE / 2,
        screenY * TILE_SIZE + TILE_SIZE / 2,
        TILE_SIZE * 0.4,
        0,
        Math.PI * 2
    );
    ctx.fill();
    ctx.restore();
    
    // Draw loot icon
    ctx.fillStyle = '#f39c12';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowBlur = 5;
    ctx.shadowColor = '#000';
    ctx.fillText('💰', 
        screenX * TILE_SIZE + TILE_SIZE / 2, 
        screenY * TILE_SIZE + TILE_SIZE / 2
    );
    ctx.shadowBlur = 0;
    
    // Range indicator
    const distance = Math.max(Math.abs(player.x - loot.x), Math.abs(player.y - loot.y));
    if (distance <= LOOT_RANGE) {
        ctx.strokeStyle = `rgba(46, 204, 113, ${pulse * 0.5})`;
        ctx.lineWidth = 2;
        ctx.strokeRect(
            screenX * TILE_SIZE + 2,
            screenY * TILE_SIZE + 2,
            TILE_SIZE - 4,
            TILE_SIZE - 4
        );
    }
}
