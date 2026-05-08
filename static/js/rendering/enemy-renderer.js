// Enemy rendering

function renderEnemies(ctx, enemies, viewport, sprites, spriteRenderer) {
    for (const enemy of Object.values(enemies)) {
        const screen = worldToScreen(enemy.x, enemy.y, viewport);
        
        if (isInViewport(screen.x, screen.y)) {
            renderEnemySprite(ctx, screen.x, screen.y, enemy, sprites, spriteRenderer);
            renderEnemyHPBar(ctx, screen.x, screen.y, enemy, spriteRenderer);
        }
    }
}

function renderEnemySprite(ctx, screenX, screenY, enemy, sprites, spriteRenderer) {
    const enemySprite = enemy.is_boss ? sprites.enemyOrc : sprites.enemySkeleton;
    
    if (sprites.loaded && enemySprite && enemySprite.complete) {
        const frame = Math.floor(spriteRenderer.animationFrame / 2) % 4;
        
        ctx.save();
        ctx.imageSmoothingEnabled = false;
        
        ctx.drawImage(
            enemySprite,
            frame * 32, 0, 32, 32,
            screenX * TILE_SIZE, screenY * TILE_SIZE, 32, 32
        );
        
        if (enemy.is_boss) {
            renderBossGlow(ctx, screenX, screenY, enemySprite, frame);
        }
        
        ctx.restore();
    } else {
        // Fallback
        ctx.fillStyle = enemy.is_boss ? '#9b59b6' : '#e74c3c';
        ctx.fillRect(screenX * TILE_SIZE + 2, screenY * TILE_SIZE + 2, 
                    TILE_SIZE - 4, TILE_SIZE - 4);
    }
}

function renderBossGlow(ctx, screenX, screenY, sprite, frame) {
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#9b59b6';
    ctx.globalAlpha = 0.3;
    ctx.drawImage(
        sprite,
        frame * 32, 0, 32, 32,
        screenX * TILE_SIZE, screenY * TILE_SIZE, 32, 32
    );
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
}

function renderEnemyHPBar(ctx, screenX, screenY, enemy, spriteRenderer) {
    const hpPercent = enemy.hp / enemy.max_hp;
    
    if (spriteRenderer) {
        spriteRenderer.drawHPBar(
            ctx,
            screenX * TILE_SIZE,
            screenY * TILE_SIZE - 4,
            TILE_SIZE,
            hpPercent
        );
    } else {
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(screenX * TILE_SIZE, screenY * TILE_SIZE - 3, 
                    TILE_SIZE * hpPercent, 2);
    }
}
