// Player and other players rendering

function renderOtherPlayers(ctx, otherPlayers, viewport, sprites, spriteRenderer) {
    for (const [playerId, otherPlayer] of Object.entries(otherPlayers)) {
        const screen = worldToScreen(otherPlayer.x, otherPlayer.y, viewport);
        
        if (isInViewport(screen.x, screen.y)) {
            renderOtherPlayer(ctx, screen.x, screen.y, otherPlayer, sprites, spriteRenderer);
        }
    }
}

function renderOtherPlayer(ctx, screenX, screenY, otherPlayer, sprites, spriteRenderer) {
    if (sprites.loaded && sprites.playerIdle && sprites.playerIdle.complete) {
        const frame = Math.floor(spriteRenderer.animationFrame / 3) % 4;
        
        ctx.save();
        ctx.imageSmoothingEnabled = false;
        
        ctx.drawImage(
            sprites.playerIdle,
            frame * 64, 0, 64, 64,
            screenX * TILE_SIZE - 16, screenY * TILE_SIZE - 16, 64, 64
        );
        
        ctx.restore();
    } else {
        // Fallback
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(screenX * TILE_SIZE + 2, screenY * TILE_SIZE + 2, 
                    TILE_SIZE - 4, TILE_SIZE - 4);
        ctx.fillStyle = '#fff';
        ctx.fillRect(screenX * TILE_SIZE + 6, screenY * TILE_SIZE + 6, 4, 4);
    }
    
    // Name tag
    ctx.fillStyle = '#2ecc71';
    ctx.font = 'bold 10px Arial';
    ctx.textAlign = 'center';
    ctx.shadowBlur = 3;
    ctx.shadowColor = '#000';
    ctx.fillText(otherPlayer.name || 'Player', 
                 screenX * TILE_SIZE + TILE_SIZE/2, 
                 screenY * TILE_SIZE - 4);
    ctx.shadowBlur = 0;
}

function renderPlayer(ctx, player, viewport, sprites, spriteRenderer, attackAnimations, isWalking, walkFrameIndex) {
    // Calculate player position with sub-tile precision
    const visualX = viewport.visualX || player.x;
    const visualY = viewport.visualY || player.y;
    
    // Calculate screen position with fractional offset
    const screenX = (visualX - viewport.startX) * TILE_SIZE;
    const screenY = (visualY - viewport.startY) * TILE_SIZE;
    
    // Draw attack range indicator if ranged weapon
    if (player.weapon && player.weapon.ranged) {
        renderWeaponRange(ctx, screenX, screenY, player.weapon.range);
    }
    
    // Check if attacking with pierce (melee)
    const isAttacking = attackAnimations.some(anim => 
        anim.type === 'pierce' && anim.fromX === player.x && anim.fromY === player.y
    );
    
    if (isAttacking) {
        console.log('Player is attacking with pierce - hiding player sprite');
    }
    
    // Always render player sprite unless doing pierce attack (pierce sprite replaces player)
    if (!isAttacking) {
        renderPlayerSprite(ctx, screenX, screenY, player, sprites, spriteRenderer, isWalking, walkFrameIndex);
    }
    
    // Always render player info
    renderPlayerInfo(ctx, screenX, screenY, player);
}

function renderWeaponRange(ctx, screenX, screenY, range) {
    ctx.strokeStyle = 'rgba(52, 152, 219, 0.3)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(
        screenX + TILE_SIZE / 2,
        screenY + TILE_SIZE / 2,
        range * TILE_SIZE,
        0,
        Math.PI * 2
    );
    ctx.stroke();
}

function renderPlayerSprite(ctx, screenX, screenY, player, sprites, spriteRenderer, isWalking, walkFrameIndex) {
    if (sprites.loaded) {
        const useWalkSprite = isWalking && sprites.playerWalk && sprites.playerWalk.complete;
        const playerSprite = useWalkSprite ? sprites.playerWalk : sprites.playerIdle;
        
        if (playerSprite && playerSprite.complete) {
            ctx.save();
            ctx.imageSmoothingEnabled = false;
            
            const frame = useWalkSprite ? walkFrameIndex : Math.floor(spriteRenderer.animationFrame / 3) % 4;
            
            ctx.drawImage(
                playerSprite,
                frame * 64, 0, 64, 64,
                screenX - 16, screenY - 16, 64, 64
            );
            
            ctx.restore();
        } else {
            renderPlayerFallback(ctx, screenX, screenY);
        }
    } else {
        renderPlayerFallback(ctx, screenX, screenY);
    }
}

function renderPlayerFallback(ctx, screenX, screenY) {
    ctx.fillStyle = '#3498db';
    ctx.fillRect(screenX + 2, screenY + 2, 
                TILE_SIZE - 4, TILE_SIZE - 4);
    ctx.fillStyle = '#fff';
    ctx.fillRect(screenX + 6, screenY + 6, 4, 4);
}

function renderPlayerInfo(ctx, screenX, screenY, player) {
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 10px Arial';
    ctx.textAlign = 'center';
    ctx.shadowBlur = 3;
    ctx.shadowColor = '#000';
    ctx.fillText(player.name, 
                 screenX + TILE_SIZE/2, 
                 screenY - 4);
    
    if (player.weapon && player.weapon.ranged) {
        ctx.fillStyle = '#3498db';
        ctx.font = '8px Arial';
        ctx.fillText(`Range: ${player.weapon.range}`, 
                     screenX + TILE_SIZE/2, 
                     screenY + TILE_SIZE + 10);
    }
    ctx.shadowBlur = 0;
}
