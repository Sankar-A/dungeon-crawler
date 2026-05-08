// Rendering and animation
let animationLoop = null;
let isWalking = false;
let walkFrameIndex = 0;
let attackAnimations = [];
let deathAnimations = [];

function createAttackAnimation(fromX, fromY, toX, toY, isRanged) {
    const dx = toX - fromX;
    const dy = toY - fromY;
    let direction = 'down';
    
    if (Math.abs(dx) > Math.abs(dy)) {
        direction = 'side';
    } else if (dy < 0) {
        direction = 'up';
    } else {
        direction = 'down';
    }
    
    const animation = {
        fromX,
        fromY,
        toX,
        toY,
        isRanged,
        direction,
        flipX: dx < 0,
        progress: 0,
        frame: 0,
        duration: 8,
        maxFrames: 8,
        type: isRanged ? 'projectile' : 'pierce'
    };
    attackAnimations.push(animation);
}

function createDeathAnimation(x, y, isBoss) {
    const animation = {
        x,
        y,
        isBoss,
        frame: 0,
        maxFrames: isBoss ? 6 : 8,
        progress: 0
    };
    deathAnimations.push(animation);
}

function startAnimationLoop() {
    if (animationLoop) return;
    animationLoop = setInterval(() => {
        if (spriteRenderer && dungeon && player) {
            spriteRenderer.update();
            updateAttackAnimations();
            updateDeathAnimations();
            
            // Update walk animation
            if (isWalking) {
                walkFrameIndex = (walkFrameIndex + 1) % 4;
            }
            
            renderDungeon();
        }
    }, 100);
}

function renderDungeon() {
    if (!ctx || !dungeon || !player) return;
    
    setupCanvas(ctx, canvas);
    const viewport = calculateViewport(player);
    
    renderTiles(ctx, dungeon, viewport, sprites);
    renderStairs(ctx, entities, viewport, sprites, spriteRenderer);
    
    // Convert lootDrops object to array for rendering
    const lootArray = Object.values(lootDrops);
    renderLootDrops(ctx, lootArray, player, viewport, spriteRenderer);
    
    renderDeathAnimations(ctx, deathAnimations, viewport, sprites);
    renderEnemies(ctx, enemies, viewport, sprites, spriteRenderer);
    renderOtherPlayers(ctx, otherPlayers, viewport, sprites, spriteRenderer);
    renderPlayer(ctx, player, viewport, sprites, spriteRenderer, attackAnimations, isWalking, walkFrameIndex);
    renderAttackAnimations();
    renderDebugInfo(ctx, player, debugMode);
    renderMinimap();
}

function renderMinimap() {
    if (!minimapCtx || !dungeon || !player) return;
    
    const minimapSize = 150;
    const dungeonWidth = dungeon[0].length;
    const dungeonHeight = dungeon.length;
    const scale = Math.min(minimapSize / dungeonWidth, minimapSize / dungeonHeight);
    
    minimapCtx.fillStyle = '#000';
    minimapCtx.fillRect(0, 0, minimapSize, minimapSize);
    
    for (let y = 0; y < dungeonHeight; y++) {
        for (let x = 0; x < dungeonWidth; x++) {
            const tile = dungeon[y][x];
            minimapCtx.fillStyle = tile === 0 ? '#4a4a4a' : '#1a1a1a';
            minimapCtx.fillRect(x * scale, y * scale, scale, scale);
        }
    }
    
    if (entities && entities.stairs) {
        minimapCtx.fillStyle = '#f39c12';
        minimapCtx.fillRect(
            entities.stairs[0] * scale,
            entities.stairs[1] * scale,
            scale * 2,
            scale * 2
        );
    }
    
    for (const enemy of Object.values(enemies)) {
        minimapCtx.fillStyle = enemy.is_boss ? '#9b59b6' : '#e74c3c';
        minimapCtx.fillRect(
            enemy.x * scale,
            enemy.y * scale,
            scale * 2,
            scale * 2
        );
    }
    
    for (const otherPlayer of Object.values(otherPlayers)) {
        minimapCtx.fillStyle = '#3498db';
        minimapCtx.fillRect(
            otherPlayer.x * scale,
            otherPlayer.y * scale,
            scale * 2,
            scale * 2
        );
    }
    
    minimapCtx.fillStyle = '#2ecc71';
    minimapCtx.fillRect(
        player.x * scale,
        player.y * scale,
        scale * 2,
        scale * 2
    );
}

function renderOtherPlayers(ctx, otherPlayers, viewport, sprites, spriteRenderer) {
    for (const [playerId, otherPlayer] of Object.entries(otherPlayers)) {
        const screenX = (otherPlayer.x - viewport.startX) * TILE_SIZE;
        const screenY = (otherPlayer.y - viewport.startY) * TILE_SIZE;
        
        if (screenX >= -TILE_SIZE && screenX < canvas.width &&
            screenY >= -TILE_SIZE && screenY < canvas.height) {
            
            if (spriteRenderer) {
                spriteRenderer.drawPlayerSprite(ctx, screenX, screenY, 'down', 0, false);
            } else {
                ctx.fillStyle = '#3498db';
                ctx.fillRect(screenX, screenY, TILE_SIZE, TILE_SIZE);
            }
            
            ctx.fillStyle = '#fff';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(otherPlayer.name, screenX + TILE_SIZE / 2, screenY - 5);
        }
    }
}

function updateAttackAnimations() {
    attackAnimations = attackAnimations.filter(anim => {
        anim.progress++;
        if (anim.type === 'pierce') {
            anim.frame = Math.min(Math.floor(anim.progress), 7);
        }
        return anim.progress < anim.duration;
    });
}

function updateDeathAnimations() {
    deathAnimations = deathAnimations.filter(anim => {
        anim.progress++;
        
        if (anim.frame < anim.maxFrames - 1) {
            anim.frame = Math.min(Math.floor(anim.progress / 5), anim.maxFrames - 1);
        }
        
        const animationDuration = anim.maxFrames * 5;
        const holdDuration = 100;
        const totalDuration = animationDuration + holdDuration;
        
        return anim.progress < totalDuration;
    });
}

function renderAttackAnimations() {
    if (!ctx) return;
    
    if (attackAnimations.length > 0) {
        console.log('Rendering', attackAnimations.length, 'attack animations');
    }
    
    for (const anim of attackAnimations) {
        const viewport = calculateViewport(player);
        const progress = anim.progress / anim.duration;
        
        if (anim.type === 'pierce') {
            console.log('Rendering pierce animation - frame:', anim.frame, 'progress:', anim.progress, 'direction:', anim.direction);
        }
        
        if (anim.type === 'projectile') {
            // Ranged attack - draw projectile moving from player to enemy
            const currentX = anim.fromX + (anim.toX - anim.fromX) * progress;
            const currentY = anim.fromY + (anim.toY - anim.fromY) * progress;
            
            const screenX = (currentX - viewport.startX) * TILE_SIZE;
            const screenY = (currentY - viewport.startY) * TILE_SIZE;
            
            if (screenX >= -TILE_SIZE && screenX < canvas.width &&
                screenY >= -TILE_SIZE && screenY < canvas.height) {
                
                ctx.save();
                ctx.fillStyle = '#f39c12';
                ctx.beginPath();
                ctx.arc(screenX + TILE_SIZE / 2, screenY + TILE_SIZE / 2, 6, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#f39c12';
                ctx.fill();
                ctx.restore();
            }
            
        } else if (anim.type === 'pierce') {
            // Melee attack - draw pierce sprite animation
            const screenX = (anim.fromX - viewport.startX) * TILE_SIZE;
            const screenY = (anim.fromY - viewport.startY) * TILE_SIZE;
            
            // Select the appropriate sprite based on direction
            let pierceSprite = null;
            if (anim.direction === 'down') {
                pierceSprite = sprites.playerPierceDown;
            } else if (anim.direction === 'up') {
                pierceSprite = sprites.playerPierceUp;
            } else if (anim.direction === 'side') {
                pierceSprite = sprites.playerPierceSide;
            }
            
            if (sprites.loaded && pierceSprite && pierceSprite.complete) {
                ctx.save();
                ctx.imageSmoothingEnabled = false;
                
                // Each pierce sprite is 512x64 (8 frames of 64x64)
                const frame = anim.frame;
                
                // Handle horizontal flipping for left attacks
                if (anim.flipX && anim.direction === 'side') {
                    // For flipped sprites, translate to the center point first
                    ctx.translate(screenX + TILE_SIZE / 2, screenY + TILE_SIZE / 2);
                    ctx.scale(-1, 1);
                    // Draw 64x64 sprite at original size
                    ctx.drawImage(
                        pierceSprite,
                        frame * 64, 0, 64, 64,
                        -32, -32, 64, 64
                    );
                } else {
                    // Draw 64x64 sprite at original size, centered in 32x32 tile
                    ctx.drawImage(
                        pierceSprite,
                        frame * 64, 0, 64, 64,
                        screenX - 16, screenY - 16, 64, 64
                    );
                }
                
                ctx.restore();
            } else {
                // Fallback - draw slash arc if sprites not loaded
                const targetScreenX = (anim.toX - viewport.startX) * TILE_SIZE + TILE_SIZE / 2;
                const targetScreenY = (anim.toY - viewport.startY) * TILE_SIZE + TILE_SIZE / 2;
                
                ctx.save();
                ctx.globalAlpha = 1 - progress;
                ctx.strokeStyle = '#e74c3c';
                ctx.lineWidth = 3;
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#e74c3c';
                
                const angle = Math.atan2(anim.toY - anim.fromY, anim.toX - anim.fromX);
                const radius = TILE_SIZE * 0.8;
                
                ctx.beginPath();
                ctx.arc(targetScreenX, targetScreenY, radius, 
                       angle - Math.PI / 3 + progress * Math.PI / 2, 
                       angle + Math.PI / 3 + progress * Math.PI / 2);
                ctx.stroke();
                ctx.restore();
            }
        }
    }
}
