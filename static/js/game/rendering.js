// Rendering and animation
let animationLoop = null;
let isWalking = false;
let walkFrameIndex = 0;
let walkFrameCounter = 0;
const WALK_ANIMATION_SPEED = 8; // Frames to wait before advancing walk animation
let attackAnimations = [];
let deathAnimations = [];
let specialEffects = []; // Boss special attack effects

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
        duration: 30, // Increased from 8 to slow down attack animations (30 frames = 500ms at 60 FPS)
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

function createSpecialAttackEffect(ability, fromX, fromY, toX, toY) {
    const effect = {
        ability,
        fromX,
        fromY,
        toX,
        toY,
        progress: 0,
        duration: 60, // 1 second at 60 FPS
        particles: []
    };
    
    // Initialize particles based on ability type
    if (ability.includes('lightning') || ability.includes('thunder')) {
        effect.color = '#00ffff';
        effect.type = 'lightning';
    } else if (ability.includes('fire') || ability.includes('flame') || ability.includes('inferno') || ability.includes('dragon_breath')) {
        effect.color = '#ff4500';
        effect.type = 'fire';
    } else if (ability.includes('frost') || ability.includes('ice')) {
        effect.color = '#87ceeb';
        effect.type = 'frost';
    } else if (ability.includes('shadow') || ability.includes('darkness')) {
        effect.color = '#4b0082';
        effect.type = 'shadow';
    } else if (ability.includes('void') || ability.includes('chaos')) {
        effect.color = '#8b00ff';
        effect.type = 'void';
    } else if (ability.includes('poison') || ability.includes('venom')) {
        effect.color = '#00ff00';
        effect.type = 'poison';
    } else if (ability.includes('blood')) {
        effect.color = '#8b0000';
        effect.type = 'blood';
    } else if (ability.includes('death') || ability.includes('soul')) {
        effect.color = '#000000';
        effect.type = 'death';
    } else {
        effect.color = '#ffffff';
        effect.type = 'generic';
    }
    
    specialEffects.push(effect);
}

function startAnimationLoop() {
    if (animationLoop) return;
    animationLoop = setInterval(() => {
        if (spriteRenderer && dungeon && player) {
            spriteRenderer.update();
            updateAttackAnimations();
            updateDeathAnimations();
            updateSpecialEffects();
            
            // Update cooldown UI
            if (cooldownUI) {
                cooldownUI.update();
            }
            
            // Interpolate player visual position towards actual position
            updatePlayerVisualPosition();
            
            // Update walk animation (slower than 60 FPS)
            if (isWalking) {
                walkFrameCounter++;
                if (walkFrameCounter >= WALK_ANIMATION_SPEED) {
                    walkFrameIndex = (walkFrameIndex + 1) % 4;
                    walkFrameCounter = 0;
                }
            } else {
                walkFrameCounter = 0;
                walkFrameIndex = 0;
            }
            
            renderDungeon();
        }
    }, 1000 / 60); // 60 FPS
}

function updatePlayerVisualPosition() {
    // Always interpolate towards the actual server position
    // This ensures visual and server positions stay synchronized
    const dx = player.x - playerVisualX;
    const dy = player.y - playerVisualY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // If very close, snap to target
    if (distance < 0.01) {
        playerVisualX = player.x;
        playerVisualY = player.y;
    } else {
        // Move at constant speed towards server position (tiles per frame at 60 FPS)
        const moveAmount = MOVE_SPEED / 60;
        
        if (distance <= moveAmount) {
            // Close enough, snap to target
            playerVisualX = player.x;
            playerVisualY = player.y;
        } else {
            // Move towards server position at constant speed
            const ratio = moveAmount / distance;
            playerVisualX += dx * ratio;
            playerVisualY += dy * ratio;
        }
    }
}

function renderDungeon() {
    if (!ctx || !dungeon || !player) return;
    
    setupCanvas(ctx, canvas);
    const viewport = calculateViewport(player);
    
    // Apply viewport offset for smooth scrolling to all rendering
    ctx.save();
    ctx.translate(-viewport.offsetX, -viewport.offsetY);
    
    // 1. Render dungeon tiles
    renderTiles(ctx, dungeon, viewport, sprites);
    renderStairs(ctx, entities, viewport, sprites, spriteRenderer);
    
    // 2. Render attack zones (under entities)
    if (attackZoneRenderer) {
        attackZoneRenderer.render(viewport.startX, viewport.startY);
    }
    
    // 3. Render blink targeting overlay (if active)
    if (blinkTargetingMode && attackZoneRenderer && validBlinkTiles) {
        attackZoneRenderer.renderBlinkTargeting(validBlinkTiles, viewport.startX, viewport.startY);
    }
    
    // Convert lootDrops object to array for rendering
    const lootArray = Object.values(lootDrops);
    renderLootDrops(ctx, lootArray, player, viewport, spriteRenderer);
    
    renderDeathAnimations(ctx, deathAnimations, viewport, sprites);
    
    // 4. Render entities (enemies, players)
    renderEnemies(ctx, enemies, viewport, sprites, spriteRenderer);
    renderOtherPlayers(ctx, otherPlayers, viewport, sprites, spriteRenderer);
    renderPlayer(ctx, player, viewport, sprites, spriteRenderer, attackAnimations, isWalking, walkFrameIndex);
    renderAttackAnimations();
    renderSpecialEffects(); // Render boss special attack effects
    
    // 5. Render effects (over entities)
    if (effectRenderer) {
        effectRenderer.render(viewport.startX, viewport.startY);
    }
    
    ctx.restore();
    
    // Render UI elements without offset
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
            // Calculate frame based on progress (8 frames over 30 progress steps)
            anim.frame = Math.min(Math.floor((anim.progress / anim.duration) * anim.maxFrames), anim.maxFrames - 1);
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


function updateSpecialEffects() {
    specialEffects = specialEffects.filter(effect => {
        effect.progress++;
        return effect.progress < effect.duration;
    });
}

function renderSpecialEffects() {
    if (!ctx) return;
    
    for (const effect of specialEffects) {
        const viewport = calculateViewport(player);
        const progress = effect.progress / effect.duration;
        
        const fromScreenX = (effect.fromX - viewport.startX) * TILE_SIZE + TILE_SIZE / 2;
        const fromScreenY = (effect.fromY - viewport.startY) * TILE_SIZE + TILE_SIZE / 2;
        const toScreenX = (effect.toX - viewport.startX) * TILE_SIZE + TILE_SIZE / 2;
        const toScreenY = (effect.toY - viewport.startY) * TILE_SIZE + TILE_SIZE / 2;
        
        ctx.save();
        
        if (effect.type === 'lightning') {
            // Lightning bolt effect
            ctx.strokeStyle = effect.color;
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = effect.color;
            ctx.globalAlpha = 1 - progress;
            
            ctx.beginPath();
            ctx.moveTo(fromScreenX, fromScreenY);
            
            // Jagged lightning path
            const steps = 5;
            for (let i = 1; i <= steps; i++) {
                const t = i / steps;
                const x = fromScreenX + (toScreenX - fromScreenX) * t + (Math.random() - 0.5) * 30;
                const y = fromScreenY + (toScreenY - fromScreenY) * t + (Math.random() - 0.5) * 30;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(toScreenX, toScreenY);
            ctx.stroke();
            
        } else if (effect.type === 'fire') {
            // Fire particles
            const numParticles = 20;
            ctx.globalAlpha = 1 - progress;
            
            for (let i = 0; i < numParticles; i++) {
                const angle = (i / numParticles) * Math.PI * 2;
                const distance = progress * TILE_SIZE * 2;
                const x = toScreenX + Math.cos(angle) * distance;
                const y = toScreenY + Math.sin(angle) * distance;
                
                const gradient = ctx.createRadialGradient(x, y, 0, x, y, 10);
                gradient.addColorStop(0, '#ff4500');
                gradient.addColorStop(0.5, '#ff8c00');
                gradient.addColorStop(1, 'rgba(255, 69, 0, 0)');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y, 10, 0, Math.PI * 2);
                ctx.fill();
            }
            
        } else if (effect.type === 'frost') {
            // Frost wave
            ctx.strokeStyle = effect.color;
            ctx.lineWidth = 4;
            ctx.shadowBlur = 20;
            ctx.shadowColor = effect.color;
            ctx.globalAlpha = 1 - progress;
            
            const radius = progress * TILE_SIZE * 3;
            ctx.beginPath();
            ctx.arc(toScreenX, toScreenY, radius, 0, Math.PI * 2);
            ctx.stroke();
            
            // Ice crystals
            for (let i = 0; i < 8; i++) {
                const angle = (i / 8) * Math.PI * 2;
                const x = toScreenX + Math.cos(angle) * radius;
                const y = toScreenY + Math.sin(angle) * radius;
                
                ctx.fillStyle = effect.color;
                ctx.fillRect(x - 3, y - 3, 6, 6);
            }
            
        } else if (effect.type === 'shadow') {
            // Darkness spreading
            ctx.fillStyle = effect.color;
            ctx.globalAlpha = (1 - progress) * 0.7;
            
            const radius = progress * TILE_SIZE * 4;
            const gradient = ctx.createRadialGradient(toScreenX, toScreenY, 0, toScreenX, toScreenY, radius);
            gradient.addColorStop(0, 'rgba(75, 0, 130, 0.8)');
            gradient.addColorStop(1, 'rgba(75, 0, 130, 0)');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(toScreenX - radius, toScreenY - radius, radius * 2, radius * 2);
            
        } else if (effect.type === 'void') {
            // Void tentacles
            ctx.strokeStyle = effect.color;
            ctx.lineWidth = 5;
            ctx.shadowBlur = 20;
            ctx.shadowColor = effect.color;
            ctx.globalAlpha = 1 - progress;
            
            for (let i = 0; i < 3; i++) {
                const angle = (i / 3) * Math.PI * 2 + progress * Math.PI;
                const length = TILE_SIZE * 2;
                
                ctx.beginPath();
                ctx.moveTo(fromScreenX, fromScreenY);
                
                for (let j = 0; j <= 10; j++) {
                    const t = j / 10;
                    const x = fromScreenX + Math.cos(angle) * length * t + Math.sin(t * Math.PI * 4) * 20;
                    const y = fromScreenY + Math.sin(angle) * length * t + Math.cos(t * Math.PI * 4) * 20;
                    ctx.lineTo(x, y);
                }
                ctx.stroke();
            }
            
        } else if (effect.type === 'poison') {
            // Poison cloud
            ctx.fillStyle = effect.color;
            ctx.globalAlpha = (1 - progress) * 0.5;
            
            const radius = progress * TILE_SIZE * 2;
            for (let i = 0; i < 10; i++) {
                const angle = (i / 10) * Math.PI * 2;
                const distance = radius + Math.sin(effect.progress * 0.1 + i) * 10;
                const x = toScreenX + Math.cos(angle) * distance;
                const y = toScreenY + Math.sin(angle) * distance;
                
                ctx.beginPath();
                ctx.arc(x, y, 15, 0, Math.PI * 2);
                ctx.fill();
            }
            
        } else if (effect.type === 'blood') {
            // Blood splatter
            ctx.fillStyle = effect.color;
            ctx.globalAlpha = 1 - progress;
            
            for (let i = 0; i < 15; i++) {
                const angle = (i / 15) * Math.PI * 2;
                const distance = progress * TILE_SIZE * 1.5;
                const x = toScreenX + Math.cos(angle) * distance;
                const y = toScreenY + Math.sin(angle) * distance;
                
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fill();
            }
            
        } else if (effect.type === 'death') {
            // Death aura
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.shadowBlur = 25;
            ctx.shadowColor = '#000000';
            ctx.globalAlpha = 1 - progress;
            
            const radius = progress * TILE_SIZE * 3;
            ctx.beginPath();
            ctx.arc(toScreenX, toScreenY, radius, 0, Math.PI * 2);
            ctx.stroke();
            
            // Skull symbol (simplified)
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 30px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('💀', toScreenX, toScreenY);
            
        } else {
            // Generic energy blast
            ctx.strokeStyle = effect.color;
            ctx.lineWidth = 4;
            ctx.shadowBlur = 15;
            ctx.shadowColor = effect.color;
            ctx.globalAlpha = 1 - progress;
            
            ctx.beginPath();
            ctx.moveTo(fromScreenX, fromScreenY);
            ctx.lineTo(toScreenX, toScreenY);
            ctx.stroke();
            
            // Impact circle
            const impactRadius = progress * TILE_SIZE;
            ctx.beginPath();
            ctx.arc(toScreenX, toScreenY, impactRadius, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        ctx.restore();
    }
}
