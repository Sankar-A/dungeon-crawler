// Game state
let socket;
let player = null;
let dungeon = null;
let entities = null;
let enemies = {};
let otherPlayers = {}; // Track other players in multiplayer
let inventory = [];
let rareWeapons = [];
let rareBosses = [];
let attackAnimations = []; // Track active attack animations
let debugMode = false; // Debug flag for tile boundaries
let isWalking = false; // Track if player is currently walking
let walkAnimationTimer = null; // Timer for walk animation
let keysPressed = {}; // Track which keys are currently pressed
let lastMoveTime = 0; // Track last movement time
const MOVE_COOLDOWN = 250; // Minimum time between moves in ms (slower)
let walkFrameIndex = 0; // Track current walk animation frame (0-5)
let inputLocked = false; // Lock input during animations
let activeModal = null; // Track which modal is open ('skills', 'inventory', or null)
let selectedIndex = 0; // Track selected item in modal
let deathAnimations = []; // Track enemy death animations

// Canvas
const canvas = document.getElementById('dungeon-canvas');
const ctx = canvas ? canvas.getContext('2d') : null;
const minimapCanvas = document.getElementById('minimap-canvas');
const minimapCtx = minimapCanvas ? minimapCanvas.getContext('2d') : null;
const TILE_SIZE = 32;
const VIEWPORT_WIDTH = 25;
const VIEWPORT_HEIGHT = 18;

// Sprite loading
const sprites = {
    dungeonTiles: null,
    dungeonProps: null,
    playerIdle: null,
    playerWalk: null,
    playerPierceDown: null,
    playerPierceSide: null,
    playerPierceUp: null,
    enemySkeleton: null,
    enemyOrc: null,
    enemySkeletonDeath: null,
    enemyOrcDeath: null,
    loaded: false
};

let spritesLoaded = 0;
const totalSprites = 11; // Updated count
let spriteRenderer = null;
let animationLoop = null;

function loadSprites() {
    spriteRenderer = new SpriteRenderer();
    
    // Load Pixel Crawler tileset (contains both floors and walls)
    sprites.dungeonTiles = new Image();
    sprites.dungeonTiles.onload = () => checkSpritesLoaded();
    sprites.dungeonTiles.onerror = () => checkSpritesLoaded();
    sprites.dungeonTiles.src = '/static/images/dungeon-tiles.png';
    
    sprites.dungeonProps = new Image();
    sprites.dungeonProps.onload = () => checkSpritesLoaded();
    sprites.dungeonProps.onerror = () => checkSpritesLoaded();
    sprites.dungeonProps.src = '/static/images/dungeon-props.png';
    
    // Load character sprites
    sprites.playerIdle = new Image();
    sprites.playerIdle.onload = () => checkSpritesLoaded();
    sprites.playerIdle.onerror = () => checkSpritesLoaded();
    sprites.playerIdle.src = '/static/images/player-idle.png';
    
    sprites.playerWalk = new Image();
    sprites.playerWalk.onload = () => checkSpritesLoaded();
    sprites.playerWalk.onerror = () => checkSpritesLoaded();
    sprites.playerWalk.src = '/static/images/player-walk.png';
    
    // Load pierce attack sprites
    sprites.playerPierceDown = new Image();
    sprites.playerPierceDown.onload = () => checkSpritesLoaded();
    sprites.playerPierceDown.onerror = () => checkSpritesLoaded();
    sprites.playerPierceDown.src = '/static/images/player-pierce-down.png';
    
    sprites.playerPierceSide = new Image();
    sprites.playerPierceSide.onload = () => checkSpritesLoaded();
    sprites.playerPierceSide.onerror = () => checkSpritesLoaded();
    sprites.playerPierceSide.src = '/static/images/player-pierce-side.png';
    
    sprites.playerPierceUp = new Image();
    sprites.playerPierceUp.onload = () => checkSpritesLoaded();
    sprites.playerPierceUp.onerror = () => checkSpritesLoaded();
    sprites.playerPierceUp.src = '/static/images/player-pierce-up.png';
    
    // Load enemy sprites
    sprites.enemySkeleton = new Image();
    sprites.enemySkeleton.onload = () => checkSpritesLoaded();
    sprites.enemySkeleton.onerror = () => checkSpritesLoaded();
    sprites.enemySkeleton.src = '/static/images/enemy-skeleton.png';
    
    sprites.enemyOrc = new Image();
    sprites.enemyOrc.onload = () => checkSpritesLoaded();
    sprites.enemyOrc.onerror = () => checkSpritesLoaded();
    sprites.enemyOrc.src = '/static/images/enemy-orc.png';
    
    // Load enemy death sprites
    sprites.enemySkeletonDeath = new Image();
    sprites.enemySkeletonDeath.onload = () => checkSpritesLoaded();
    sprites.enemySkeletonDeath.onerror = () => checkSpritesLoaded();
    sprites.enemySkeletonDeath.src = '/static/images/enemy-skeleton-death.png';
    
    sprites.enemyOrcDeath = new Image();
    sprites.enemyOrcDeath.onload = () => checkSpritesLoaded();
    sprites.enemyOrcDeath.onerror = () => checkSpritesLoaded();
    sprites.enemyOrcDeath.src = '/static/images/enemy-orc-death.png';
}

function checkSpritesLoaded() {
    spritesLoaded++;
    console.log(`Loaded ${spritesLoaded}/${totalSprites} sprites`);
    if (spritesLoaded >= totalSprites) {
        sprites.loaded = true;
        console.log('All sprites loaded!');
        console.log('Player idle sprite:', sprites.playerIdle ? `${sprites.playerIdle.width}x${sprites.playerIdle.height}` : 'NOT LOADED');
        console.log('Dungeon tiles:', sprites.dungeonTiles ? `${sprites.dungeonTiles.width}x${sprites.dungeonTiles.height}` : 'NOT LOADED');
        if (dungeon) {
            renderDungeon();
            startAnimationLoop();
        }
    }
}

function startAnimationLoop() {
    if (animationLoop) return;
    animationLoop = setInterval(() => {
        if (spriteRenderer && dungeon && player) {
            spriteRenderer.update();
            updateAttackAnimations();
            updateDeathAnimations();
            renderDungeon();
        }
    }, 100);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    socket = io();
    loadSprites();
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('connected', (data) => {
        console.log('Player ID:', data.player_id);
    });
    
    // Start button
    document.getElementById('start-btn').addEventListener('click', () => {
        const name = document.getElementById('character-name').value || 'Adventurer';
        socket.emit('create_character', { name });
    });
    
    // Character created
    socket.on('character_created', (data) => {
        player = data.player;
        dungeon = data.dungeon;
        entities = data.entities;
        enemies = data.enemies;
        otherPlayers = data.other_players || {};
        
        document.getElementById('start-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        document.getElementById('game-screen').style.display = 'grid';
        
        updateHUD();
        renderDungeon();
        startAnimationLoop();
    });
    
    // New player joined
    socket.on('player_joined', (data) => {
        otherPlayers[data.player_id] = {
            x: data.x,
            y: data.y,
            name: data.name
        };
        renderDungeon();
    });
    
    // Movement and Attack
    document.addEventListener('keydown', (e) => {
        if (!player) return;
        
        const key = e.key.toLowerCase();
        
        // Handle modal navigation
        if (activeModal) {
            if (key === 'escape') {
                e.preventDefault();
                closeActiveModal();
                return;
            }
            else if (key === 'w' || key === 'arrowup') {
                e.preventDefault();
                navigateModal(-1);
                return;
            }
            else if (key === 's' || key === 'arrowdown') {
                e.preventDefault();
                navigateModal(1);
                return;
            }
            else if (key === 'e') {
                e.preventDefault();
                activateSelectedItem();
                return;
            }
            // Block other inputs when modal is open
            return;
        }
        
        let direction = null;
        
        if (key === 'w' || key === 'arrowup') direction = 'up';
        else if (key === 's' || key === 'arrowdown') direction = 'down';
        else if (key === 'a' || key === 'arrowleft') direction = 'left';
        else if (key === 'd' || key === 'arrowright') direction = 'right';
        else if (key === 'p') {
            // Attack closest enemy in range
            if (!keysPressed[key] && !inputLocked) {
                e.preventDefault();
                keysPressed[key] = true;
                attackClosestEnemy();
            }
            return;
        }
        else if (key === 'l') {
            // Open skills modal
            if (!keysPressed[key]) {
                e.preventDefault();
                keysPressed[key] = true;
                showSkillsModal();
            }
            return;
        }
        else if (key === 'i') {
            // Open inventory modal
            if (!keysPressed[key]) {
                e.preventDefault();
                keysPressed[key] = true;
                showInventoryModal();
            }
            return;
        }
        else if (key === 'escape') {
            // Close any open modal
            e.preventDefault();
            closeActiveModal();
            return;
        }
        else if (key === 'f1') {
            // Toggle debug mode
            e.preventDefault();
            debugMode = !debugMode;
            console.log('Debug mode:', debugMode ? 'ON' : 'OFF');
            renderDungeon();
            return;
        }
        
        if (direction) {
            e.preventDefault();
            
            // Block input during animations
            if (inputLocked) {
                return;
            }
            
            // Check cooldown to prevent too-fast movement
            const currentTime = Date.now();
            if (currentTime - lastMoveTime < MOVE_COOLDOWN) {
                return;
            }
            
            lastMoveTime = currentTime;
            keysPressed[key] = true;
            
            // Lock input during walk animation
            inputLocked = true;
            
            // Advance walk animation frame (1 frame per tile movement)
            walkFrameIndex = (walkFrameIndex + 1) % 6;
            
            // Trigger walking animation
            isWalking = true;
            if (walkAnimationTimer) clearTimeout(walkAnimationTimer);
            walkAnimationTimer = setTimeout(() => {
                isWalking = false;
                inputLocked = false; // Unlock input after animation
                renderDungeon();
            }, MOVE_COOLDOWN); // Walk animation duration matches move cooldown
            
            socket.emit('move', { direction });
        }
    });
    
    // Key release handler
    document.addEventListener('keyup', (e) => {
        const key = e.key.toLowerCase();
        delete keysPressed[key];
    });
    
    // Player moved
    socket.on('player_moved', (data) => {
        if (data.player_id === socket.id) {
            player.x = data.x;
            player.y = data.y;
            renderDungeon();
        } else {
            // Update other player position
            if (!otherPlayers[data.player_id]) {
                otherPlayers[data.player_id] = {
                    x: data.x,
                    y: data.y,
                    name: data.name || 'Player'
                };
            } else {
                otherPlayers[data.player_id].x = data.x;
                otherPlayers[data.player_id].y = data.y;
            }
            renderDungeon();
        }
    });
    
    // Player left
    socket.on('player_left', (data) => {
        delete otherPlayers[data.player_id];
        renderDungeon();
    });
    
    // Reached stairs
    socket.on('reached_stairs', (data) => {
        if (confirm(`You reached the stairs to floor ${data.floor + 1}. Descend?`)) {
            socket.emit('descend_stairs');
        }
    });
    
    // Floor changed
    socket.on('floor_changed', (data) => {
        player = data.player;
        dungeon = data.dungeon;
        entities = data.entities;
        enemies = data.enemies;
        
        addLog(`Descended to floor ${data.floor}!`, 'loot');
        updateHUD();
        renderDungeon();
    });
    
    // Combat
    canvas?.addEventListener('click', (e) => {
        if (!player) return;
        
        const rect = canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        const tileX = Math.floor(clickX / TILE_SIZE) + player.x - Math.floor(VIEWPORT_WIDTH / 2);
        const tileY = Math.floor(clickY / TILE_SIZE) + player.y - Math.floor(VIEWPORT_HEIGHT / 2);
        
        // Check if clicked on enemy
        for (const [enemyId, enemy] of Object.entries(enemies)) {
            if (enemy.x === tileX && enemy.y === tileY) {
                // Check distance
                const dx = Math.abs(player.x - enemy.x);
                const dy = Math.abs(player.y - enemy.y);
                const distance = Math.max(dx, dy);
                
                // Get weapon range
                const weaponRange = player.weapon ? (player.weapon.range || 1) : 1;
                
                if (distance <= weaponRange) {
                    socket.emit('attack_enemy', { enemy_id: enemyId });
                } else {
                    addLog(`Enemy too far away! (Distance: ${distance}, Range: ${weaponRange})`, 'damage');
                }
                break;
            }
        }
    });
    
    socket.on('attack_failed', (data) => {
        addLog(`${data.reason}! Distance: ${data.distance}, Range: ${data.range}`, 'damage');
    });
    
    socket.on('combat_result', (data) => {
        player = data.player;
        const result = data.result;
        
        if (result.is_ranged) {
            addLog(`🏹 You shot for ${result.player_damage} damage!${result.critical ? ' CRITICAL!' : ''}`, 'damage');
        } else {
            addLog(`⚔️ You dealt ${result.player_damage} damage!${result.critical ? ' CRITICAL!' : ''}`, 'damage');
        }
        
        if (result.dodged) {
            addLog('You dodged the attack!', 'heal');
        } else if (result.enemy_damage > 0) {
            addLog(`Enemy dealt ${result.enemy_damage} damage!`, 'damage');
        }
        
        updateHUD();
        renderDungeon();
    });
    
    socket.on('enemy_defeated', (data) => {
        // Get enemy data before deleting
        const enemy = enemies[data.enemy_id];
        if (enemy) {
            // Create death animation
            createDeathAnimation(enemy.x, enemy.y, enemy.is_boss);
        }
        
        // Delete enemy for all players
        delete enemies[data.enemy_id];
        
        // Only update player stats and show loot for the attacker
        if (data.attacker_id === socket.id) {
            player = data.player;
            
            if (data.is_ranged) {
                addLog(`🏹 Enemy defeated with ranged attack! +${data.loot.xp} XP`, 'loot');
            } else {
                addLog(`⚔️ Enemy defeated! +${data.loot.xp} XP`, 'loot');
            }
            
            if (data.loot.items.length > 0) {
                data.loot.items.forEach(item => {
                    inventory.push(item);
                    const rangedTag = item.ranged ? ' 🏹' : '';
                    addLog(`Found: ${item.name}${rangedTag}!`, 'loot');
                });
            }
            
            if (data.leveled_up) {
                showLevelUpModal();
            }
            
            updateHUD();
        } else {
            // Other players just see the enemy disappear
            addLog(`Enemy defeated by another player!`, 'loot');
        }
        
        renderDungeon();
    });
    
    // New handler for enemy HP updates
    socket.on('enemy_hp_updated', (data) => {
        if (enemies[data.enemy_id]) {
            enemies[data.enemy_id].hp = data.hp;
            enemies[data.enemy_id].max_hp = data.max_hp;
            renderDungeon();
        }
    });
    
    // Skills
    document.getElementById('skills-btn')?.addEventListener('click', () => {
        showSkillsModal();
    });
    
    socket.on('skill_upgraded', (data) => {
        player = data.player;
        updateHUD();
        showSkillsModal();
    });
    
    // Inventory
    document.getElementById('inventory-btn')?.addEventListener('click', () => {
        showInventoryModal();
    });
    
    socket.on('item_equipped', (data) => {
        player = data.player;
        updateHUD();
        showInventoryModal();
    });
    
    // Lore buttons
    document.getElementById('view-weapons-btn')?.addEventListener('click', () => {
        socket.emit('get_rare_weapons');
    });
    
    document.getElementById('view-bosses-btn')?.addEventListener('click', () => {
        socket.emit('get_rare_bosses');
    });
    
    socket.on('rare_weapons_list', (data) => {
        rareWeapons = data.weapons;
        showLoreModal('Legendary Weapons', rareWeapons, 'weapon');
    });
    
    socket.on('rare_bosses_list', (data) => {
        rareBosses = data.bosses;
        showLoreModal('Epic Bosses', rareBosses, 'boss');
    });
    
    // Modal close buttons
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.remove('active');
        });
    });
    
    document.getElementById('level-up-ok')?.addEventListener('click', () => {
        document.getElementById('level-up-modal').classList.remove('active');
    });
});


// Attack system
function attackClosestEnemy() {
    if (!player || Object.keys(enemies).length === 0) {
        addLog('No enemies in range!', 'damage');
        return;
    }
    
    const weaponRange = player.weapon ? (player.weapon.range || 1) : 1;
    let closestEnemy = null;
    let closestDistance = Infinity;
    
    // Find closest enemy within range
    for (const [enemyId, enemy] of Object.entries(enemies)) {
        const dx = Math.abs(player.x - enemy.x);
        const dy = Math.abs(player.y - enemy.y);
        const distance = Math.max(dx, dy);
        
        if (distance <= weaponRange && distance < closestDistance) {
            closestDistance = distance;
            closestEnemy = { id: enemyId, ...enemy };
        }
    }
    
    if (closestEnemy) {
        // Lock input during attack animation
        inputLocked = true;
        
        // Create attack animation
        createAttackAnimation(player.x, player.y, closestEnemy.x, closestEnemy.y, 
                            player.weapon && player.weapon.ranged);
        
        // Unlock input after attack animation completes (8 frames * 100ms = 800ms)
        setTimeout(() => {
            inputLocked = false;
        }, 800);
        
        // Send attack to server
        socket.emit('attack_enemy', { enemy_id: closestEnemy.id });
    } else {
        addLog(`No enemies within range ${weaponRange}!`, 'damage');
    }
}

function createAttackAnimation(fromX, fromY, toX, toY, isRanged) {
    // Determine direction for sprite selection
    const dx = toX - fromX;
    const dy = toY - fromY;
    let direction = 'down'; // default
    
    if (Math.abs(dx) > Math.abs(dy)) {
        direction = 'side'; // left or right
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
        flipX: dx < 0, // flip sprite if attacking left
        progress: 0,
        frame: 0,
        duration: 8, // 8 frames for pierce animation
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
        maxFrames: isBoss ? 6 : 8, // Orc: 6 frames, Skeleton: 8 frames
        progress: 0
    };
    deathAnimations.push(animation);
}

function updateDeathAnimations() {
    deathAnimations = deathAnimations.filter(anim => {
        anim.progress++;
        
        // Update frame every 5 ticks for slower, more visible animation
        if (anim.frame < anim.maxFrames - 1) {
            // Still animating through frames
            anim.frame = Math.min(Math.floor(anim.progress / 5), anim.maxFrames - 1);
        }
        // Once we reach the last frame, hold it for 10 seconds (100 ticks at 100ms each)
        
        // Total duration: (maxFrames * 5) ticks for animation + 100 ticks for holding last frame
        const animationDuration = anim.maxFrames * 5;
        const holdDuration = 100; // 10 seconds at 100ms per tick
        const totalDuration = animationDuration + holdDuration;
        
        return anim.progress < totalDuration;
    });
}

function updateAttackAnimations() {
    attackAnimations = attackAnimations.filter(anim => {
        anim.progress++;
        // Update frame for sprite animations (8 frames total)
        if (anim.type === 'pierce') {
            anim.frame = Math.min(Math.floor(anim.progress), 7);
        }
        return anim.progress < anim.duration;
    });
}

function renderAttackAnimations() {
    if (!ctx || !dungeon || !player) return;
    
    const startX = player.x - Math.floor(VIEWPORT_WIDTH / 2);
    const startY = player.y - Math.floor(VIEWPORT_HEIGHT / 2);
    
    for (const anim of attackAnimations) {
        const progress = anim.progress / anim.duration;
        
        if (anim.type === 'projectile') {
            // Ranged attack - draw projectile
            const currentX = anim.fromX + (anim.toX - anim.fromX) * progress;
            const currentY = anim.fromY + (anim.toY - anim.fromY) * progress;
            
            const screenX = (currentX - startX) * TILE_SIZE + TILE_SIZE / 2;
            const screenY = (currentY - startY) * TILE_SIZE + TILE_SIZE / 2;
            
            ctx.save();
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#3498db';
            ctx.fillStyle = '#3498db';
            ctx.beginPath();
            ctx.arc(screenX, screenY, 3, 0, Math.PI * 2);
            ctx.fill();
            
            // Trail effect
            ctx.globalAlpha = 0.5;
            ctx.beginPath();
            ctx.arc(screenX - (anim.toX - anim.fromX) * 2, 
                   screenY - (anim.toY - anim.fromY) * 2, 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
            
        } else if (anim.type === 'pierce') {
            // Melee attack - draw pierce sprite animation
            const screenX = (anim.fromX - startX) * TILE_SIZE;
            const screenY = (anim.fromY - startY) * TILE_SIZE;
            
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
                const targetScreenX = (anim.toX - startX) * TILE_SIZE + TILE_SIZE / 2;
                const targetScreenY = (anim.toY - startY) * TILE_SIZE + TILE_SIZE / 2;
                
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


// Rendering
function renderDungeon() {
    if (!ctx || !dungeon || !player) return;
    
    // Ensure crisp pixel art rendering
    ctx.imageSmoothingEnabled = false;
    ctx.mozImageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.msImageSmoothingEnabled = false;
    
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const startX = player.x - Math.floor(VIEWPORT_WIDTH / 2);
    const startY = player.y - Math.floor(VIEWPORT_HEIGHT / 2);
    
    // Draw tiles
    for (let y = 0; y < VIEWPORT_HEIGHT; y++) {
        for (let x = 0; x < VIEWPORT_WIDTH; x++) {
            const worldX = startX + x;
            const worldY = startY + y;
            
            if (worldX >= 0 && worldX < dungeon[0].length && 
                worldY >= 0 && worldY < dungeon.length) {
                
                const tile = dungeon[worldY][worldX];
                
                if (sprites.loaded && sprites.dungeonTiles && sprites.dungeonTiles.complete) {
                    // Dungeon_Tiles.png contains organized sections
                    // Using specific tiles for consistency
                    
                    if (tile === 0) {
                        // Floor tile - use a simple stone floor tile
                        // Row 0, columns 0-4 typically have basic floor tiles
                        const floorVariants = [
                            [0, 0],   // Basic stone floor
                            [16, 0],  // Variant 1
                            [32, 0],  // Variant 2
                            [48, 0],  // Variant 3
                        ];
                        const variantIndex = ((worldX + worldY) % floorVariants.length);
                        const [tileX, tileY] = floorVariants[variantIndex];
                        
                        // Scale 16x16 sprite to fill 32x32 tile
                        ctx.drawImage(
                            sprites.dungeonTiles,
                            tileX, tileY, 16, 16,
                            x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
                        );
                    } else {
                        // Wall tile - use solid wall tiles
                        // Walls are typically in rows 5-10
                        const wallVariants = [
                            [0, 80],   // Basic wall (row 5)
                            [16, 80],  // Variant 1
                            [32, 80],  // Variant 2
                            [0, 96],   // Variant 3 (row 6)
                        ];
                        const variantIndex = ((worldX * 2 + worldY) % wallVariants.length);
                        const [tileX, tileY] = wallVariants[variantIndex];
                        
                        // Scale 16x16 sprite to fill 32x32 tile
                        ctx.drawImage(
                            sprites.dungeonTiles,
                            tileX, tileY, 16, 16,
                            x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
                        );
                    }
                } else {
                    // Fallback to colored tiles
                    ctx.fillStyle = tile === 0 ? '#4a4a4a' : '#1a1a1a';
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }
            } else {
                // Draw black for out of bounds
                ctx.fillStyle = '#000';
                ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }
        }
    }
    
    // Draw stairs
    if (entities && entities.stairs) {
        const stairsX = entities.stairs[0] - startX;
        const stairsY = entities.stairs[1] - startY;
        
        if (stairsX >= 0 && stairsX < VIEWPORT_WIDTH && 
            stairsY >= 0 && stairsY < VIEWPORT_HEIGHT) {
            
            // Draw pulsing outline around stairs tile
            const pulse = 0.6 + Math.sin(spriteRenderer.animationFrame * 0.3) * 0.4;
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
                // Draw stairs from dungeon props
                // Stairs are typically in the props sheet - using a specific tile
                // Pulsing glow effect
                const glowIntensity = 8 + Math.sin(spriteRenderer.animationFrame * 0.3) * 4;
                ctx.shadowBlur = glowIntensity;
                ctx.shadowColor = '#f39c12';
                
                // Scale 16x16 sprite to fill 32x32 tile
                ctx.drawImage(
                    sprites.dungeonProps,
                    48, 0, 16, 16,  // 3rd tile in first row (3*16, 0)
                    stairsX * TILE_SIZE, stairsY * TILE_SIZE, TILE_SIZE, TILE_SIZE
                );
                ctx.shadowBlur = 0;
            } else {
                // Fallback - bright golden square
                ctx.fillStyle = '#f39c12';
                const fallbackPulse = 0.8 + Math.sin(spriteRenderer.animationFrame * 0.5) * 0.2;
                ctx.globalAlpha = fallbackPulse;
                ctx.fillRect(stairsX * TILE_SIZE + 2, stairsY * TILE_SIZE + 2, 
                            TILE_SIZE - 4, TILE_SIZE - 4);
                
                // Draw down arrow
                ctx.fillStyle = '#000';
                ctx.font = 'bold 16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('↓', stairsX * TILE_SIZE + TILE_SIZE/2, stairsY * TILE_SIZE + TILE_SIZE/2 + 6);
                
                ctx.globalAlpha = 1;
            }
        }
    }
    
    // Draw enemies
    for (const enemy of Object.values(enemies)) {
        const enemyX = enemy.x - startX;
        const enemyY = enemy.y - startY;
        
        if (enemyX >= 0 && enemyX < VIEWPORT_WIDTH && 
            enemyY >= 0 && enemyY < VIEWPORT_HEIGHT) {
            
            // Draw enemy sprite
            const enemySprite = enemy.is_boss ? sprites.enemyOrc : sprites.enemySkeleton;
            if (sprites.loaded && enemySprite && enemySprite.complete) {
                // Enemy sprites are 4x1 layout: 4 frames of 32x32 each (128x32 total)
                const frame = Math.floor(spriteRenderer.animationFrame / 2) % 4;
                
                ctx.save();
                ctx.imageSmoothingEnabled = false;
                
                // Draw 32x32 sprite at original size, centered in 32x32 tile
                ctx.drawImage(
                    enemySprite,
                    frame * 32, 0, 32, 32,  // Source: 32x32 per frame
                    enemyX * TILE_SIZE, enemyY * TILE_SIZE, 32, 32  // Dest: 32x32 at original size
                );
                
                // Boss glow effect
                if (enemy.is_boss) {
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = '#9b59b6';
                    ctx.globalAlpha = 0.3;
                    ctx.drawImage(
                        enemySprite,
                        frame * 32, 0, 32, 32,
                        enemyX * TILE_SIZE, enemyY * TILE_SIZE, 32, 32
                    );
                    ctx.globalAlpha = 1;
                    ctx.shadowBlur = 0;
                }
                
                ctx.restore();
            } else {
                // Fallback
                ctx.fillStyle = enemy.is_boss ? '#9b59b6' : '#e74c3c';
                ctx.fillRect(enemyX * TILE_SIZE + 2, enemyY * TILE_SIZE + 2, 
                            TILE_SIZE - 4, TILE_SIZE - 4);
            }
            
            // HP bar
            if (spriteRenderer) {
                const hpPercent = enemy.hp / enemy.max_hp;
                spriteRenderer.drawHPBar(
                    ctx,
                    enemyX * TILE_SIZE,
                    enemyY * TILE_SIZE - 4,
                    TILE_SIZE,
                    hpPercent
                );
            } else {
                const hpPercent = enemy.hp / enemy.max_hp;
                ctx.fillStyle = '#2ecc71';
                ctx.fillRect(enemyX * TILE_SIZE, enemyY * TILE_SIZE - 3, 
                            TILE_SIZE * hpPercent, 2);
            }
        }
    }
    
    // Draw death animations
    for (const deathAnim of deathAnimations) {
        const deathX = deathAnim.x - startX;
        const deathY = deathAnim.y - startY;
        
        if (deathX >= 0 && deathX < VIEWPORT_WIDTH && 
            deathY >= 0 && deathY < VIEWPORT_HEIGHT) {
            
            const deathSprite = deathAnim.isBoss ? sprites.enemyOrcDeath : sprites.enemySkeletonDeath;
            if (sprites.loaded && deathSprite && deathSprite.complete) {
                ctx.save();
                ctx.imageSmoothingEnabled = false;
                
                // Skeleton: 8 frames of 96x64, Orc: 6 frames of 64x64
                const frameWidth = deathAnim.isBoss ? 64 : 96;
                const frameHeight = 64;
                
                // Align bottom of sprite with bottom of tile (like idle sprite)
                const offsetX = (frameWidth - TILE_SIZE) / 2;  // Center horizontally
                const offsetY = frameHeight - TILE_SIZE;  // Align bottom
                
                ctx.drawImage(
                    deathSprite,
                    deathAnim.frame * frameWidth, 0, frameWidth, frameHeight,  // Source
                    deathX * TILE_SIZE - offsetX, deathY * TILE_SIZE - offsetY, frameWidth, frameHeight  // Dest: bottom-aligned
                );
                
                ctx.restore();
            } else {
                // Fallback - draw red X if sprite not loaded
                ctx.fillStyle = '#ff0000';
                ctx.font = 'bold 24px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('X', deathX * TILE_SIZE + TILE_SIZE/2, deathY * TILE_SIZE + TILE_SIZE/2 + 8);
            }
        }
    }
    
    // Draw other players (multiplayer)
    for (const [playerId, otherPlayer] of Object.entries(otherPlayers)) {
        const otherX = otherPlayer.x - startX;
        const otherY = otherPlayer.y - startY;
        
        if (otherX >= 0 && otherX < VIEWPORT_WIDTH && 
            otherY >= 0 && otherY < VIEWPORT_HEIGHT) {
            
            // Draw other player sprite
            if (sprites.loaded && sprites.playerIdle && sprites.playerIdle.complete) {
                const frame = Math.floor(spriteRenderer.animationFrame / 3) % 4;
                
                ctx.save();
                ctx.imageSmoothingEnabled = false;
                
                // Draw 64x64 sprite at original size, centered in 32x32 tile
                ctx.drawImage(
                    sprites.playerIdle,
                    frame * 64, 0, 64, 64,  // Source: 64x64 per frame
                    otherX * TILE_SIZE - 16, otherY * TILE_SIZE - 16, 64, 64  // Dest: 64x64 centered
                );
                
                ctx.restore();
            } else {
                // Fallback - green square for other players
                ctx.fillStyle = '#2ecc71';
                ctx.fillRect(otherX * TILE_SIZE + 2, otherY * TILE_SIZE + 2, 
                            TILE_SIZE - 4, TILE_SIZE - 4);
                
                ctx.fillStyle = '#fff';
                ctx.fillRect(otherX * TILE_SIZE + 6, otherY * TILE_SIZE + 6, 
                            4, 4);
            }
            
            // Other player name tag
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.shadowBlur = 3;
            ctx.shadowColor = '#000';
            ctx.fillText(otherPlayer.name || 'Player', 
                         otherX * TILE_SIZE + TILE_SIZE/2, 
                         otherY * TILE_SIZE - 4);
            ctx.shadowBlur = 0;
        }
    }
    
    // Draw player
    const playerX = Math.floor(VIEWPORT_WIDTH / 2);
    const playerY = Math.floor(VIEWPORT_HEIGHT / 2);
    
    // Draw attack range indicator if player has ranged weapon
    if (player.weapon && player.weapon.ranged) {
        const weaponRange = player.weapon.range || 1;
        ctx.strokeStyle = 'rgba(52, 152, 219, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(
            playerX * TILE_SIZE + TILE_SIZE / 2,
            playerY * TILE_SIZE + TILE_SIZE / 2,
            weaponRange * TILE_SIZE,
            0,
            Math.PI * 2
        );
        ctx.stroke();
    }
    
    // Draw player sprite
    // Hide sprite if attack animation is playing (check against actual player position)
    const isAttacking = attackAnimations.some(anim => 
        anim.type === 'pierce' && anim.fromX === player.x && anim.fromY === player.y
    );
    
    // Only draw player sprite if not attacking
    if (!isAttacking) {
        if (sprites.loaded) {
            // Choose sprite based on walking state
            const useWalkSprite = isWalking && sprites.playerWalk && sprites.playerWalk.complete;
            const playerSprite = useWalkSprite ? sprites.playerWalk : sprites.playerIdle;
            
            if (playerSprite && playerSprite.complete) {
                ctx.save();
                ctx.imageSmoothingEnabled = false;
                
                let frame;
                if (useWalkSprite) {
                    // Player walk: 384x64 = 6x1 sprite sheet (6 frames of 64x64 each)
                    // Use walkFrameIndex - 1 frame per tile movement
                    frame = walkFrameIndex;
                } else {
                    // Player idle: 256x64 = 4x1 sprite sheet (4 frames of 64x64 each)
                    frame = Math.floor(spriteRenderer.animationFrame / 3) % 4; // 4 frames for idle
                }
                
                // Draw 64x64 sprite at original size, centered in 32x32 tile
                ctx.drawImage(
                    playerSprite,
                    frame * 64, 0, 64, 64,  // Source: 64x64 per frame
                    playerX * TILE_SIZE - 16, playerY * TILE_SIZE - 16, 64, 64  // Dest: 64x64 centered
                );
                
                ctx.restore();
            } else {
                // Fallback if sprites not loaded - bright visible square
                ctx.fillStyle = '#3498db';
                ctx.fillRect(playerX * TILE_SIZE + 2, playerY * TILE_SIZE + 2, 
                            TILE_SIZE - 4, TILE_SIZE - 4);
                
                // Add white center dot for visibility
                ctx.fillStyle = '#fff';
                ctx.fillRect(playerX * TILE_SIZE + 6, playerY * TILE_SIZE + 6, 
                            4, 4);
            }
        } else {
            // Fallback if sprites not loaded - bright visible square
            ctx.fillStyle = '#3498db';
            ctx.fillRect(playerX * TILE_SIZE + 2, playerY * TILE_SIZE + 2, 
                        TILE_SIZE - 4, TILE_SIZE - 4);
            
            // Add white center dot for visibility
            ctx.fillStyle = '#fff';
            ctx.fillRect(playerX * TILE_SIZE + 6, playerY * TILE_SIZE + 6, 
                        4, 4);
        }
    }
    // When attacking, nothing is drawn here - only the pierce animation shows
    
    // Player name tag and weapon info
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 10px Arial';
    ctx.textAlign = 'center';
    ctx.shadowBlur = 3;
    ctx.shadowColor = '#000';
    ctx.fillText(player.name, 
                 playerX * TILE_SIZE + TILE_SIZE/2, 
                 playerY * TILE_SIZE - 4);
    
    // Show weapon range if ranged
    if (player.weapon && player.weapon.ranged) {
        ctx.fillStyle = '#3498db';
        ctx.font = '8px Arial';
        ctx.fillText(`Range: ${player.weapon.range}`, 
                     playerX * TILE_SIZE + TILE_SIZE/2, 
                     playerY * TILE_SIZE + TILE_SIZE + 10);
    }
    ctx.shadowBlur = 0;
    
    // Render attack animations on top of everything
    renderAttackAnimations();
    
    // Debug mode: Draw tile boundaries
    if (debugMode) {
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
    
    // Render minimap
    renderMinimap();
}

// Minimap rendering
function renderMinimap() {
    if (!minimapCtx || !dungeon || !player) return;
    
    const minimapSize = 150;
    const dungeonWidth = dungeon[0].length;
    const dungeonHeight = dungeon.length;
    const scale = Math.min(minimapSize / dungeonWidth, minimapSize / dungeonHeight);
    
    // Clear minimap
    minimapCtx.fillStyle = '#000';
    minimapCtx.fillRect(0, 0, minimapSize, minimapSize);
    
    // Draw dungeon tiles
    for (let y = 0; y < dungeonHeight; y++) {
        for (let x = 0; x < dungeonWidth; x++) {
            const tile = dungeon[y][x];
            if (tile === 0) {
                // Floor
                minimapCtx.fillStyle = '#4a4a4a';
            } else {
                // Wall
                minimapCtx.fillStyle = '#1a1a1a';
            }
            minimapCtx.fillRect(x * scale, y * scale, scale, scale);
        }
    }
    
    // Draw stairs
    if (entities && entities.stairs) {
        minimapCtx.fillStyle = '#f39c12';
        minimapCtx.fillRect(
            entities.stairs[0] * scale,
            entities.stairs[1] * scale,
            scale * 2,
            scale * 2
        );
    }
    
    // Draw enemies
    for (const enemy of Object.values(enemies)) {
        minimapCtx.fillStyle = enemy.is_boss ? '#9b59b6' : '#e74c3c';
        minimapCtx.fillRect(
            enemy.x * scale,
            enemy.y * scale,
            scale * 2,
            scale * 2
        );
    }
    
    // Draw other players
    for (const otherPlayer of Object.values(otherPlayers)) {
        minimapCtx.fillStyle = '#2ecc71';
        minimapCtx.fillRect(
            otherPlayer.x * scale,
            otherPlayer.y * scale,
            scale * 2,
            scale * 2
        );
    }
    
    // Draw player (larger and brighter)
    minimapCtx.fillStyle = '#3498db';
    minimapCtx.fillRect(
        player.x * scale - scale,
        player.y * scale - scale,
        scale * 3,
        scale * 3
    );
    
    // Draw player center dot
    minimapCtx.fillStyle = '#fff';
    minimapCtx.fillRect(
        player.x * scale,
        player.y * scale,
        scale,
        scale
    );
}


// HUD Updates
function updateHUD() {
    if (!player) return;
    
    document.getElementById('player-name').textContent = player.name;
    document.getElementById('player-level').textContent = player.level;
    document.getElementById('current-floor').textContent = player.floor;
    document.getElementById('player-hp').textContent = player.hp;
    document.getElementById('player-max-hp').textContent = player.max_hp;
    document.getElementById('player-xp').textContent = player.xp;
    document.getElementById('player-xp-next').textContent = player.xp_to_next;
    document.getElementById('player-str').textContent = player.strength;
    document.getElementById('player-dex').textContent = player.dexterity;
    document.getElementById('player-int').textContent = player.intelligence;
    document.getElementById('player-vit').textContent = player.vitality;
    document.getElementById('skill-points').textContent = player.skill_points;
    
    // Progress bars
    const hpPercent = (player.hp / player.max_hp) * 100;
    const xpPercent = (player.xp / player.xp_to_next) * 100;
    document.getElementById('hp-bar').style.width = hpPercent + '%';
    document.getElementById('xp-bar').style.width = xpPercent + '%';
}

function addLog(message, type = '') {
    const logDiv = document.getElementById('log-messages');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = message;
    logDiv.insertBefore(entry, logDiv.firstChild);
    
    // Keep only last 20 messages
    while (logDiv.children.length > 20) {
        logDiv.removeChild(logDiv.lastChild);
    }
}

// Modals
function closeActiveModal() {
    if (activeModal === 'skills') {
        document.getElementById('skills-modal').classList.remove('active');
    } else if (activeModal === 'inventory') {
        document.getElementById('inventory-modal').classList.remove('active');
    }
    activeModal = null;
    selectedIndex = 0;
}

function navigateModal(direction) {
    if (!activeModal) return;
    
    let items;
    if (activeModal === 'skills') {
        items = document.querySelectorAll('.skill-item');
    } else if (activeModal === 'inventory') {
        items = document.querySelectorAll('.inventory-item');
    }
    
    if (!items || items.length === 0) return;
    
    // Remove previous selection
    items[selectedIndex]?.classList.remove('selected');
    
    // Update index
    selectedIndex = (selectedIndex + direction + items.length) % items.length;
    
    // Add new selection
    items[selectedIndex].classList.add('selected');
    items[selectedIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function activateSelectedItem() {
    if (!activeModal) return;
    
    if (activeModal === 'skills') {
        const items = document.querySelectorAll('.skill-item');
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
            const button = selectedItem.querySelector('button');
            if (button && !button.disabled) {
                button.click();
            }
        }
    } else if (activeModal === 'inventory') {
        const items = document.querySelectorAll('.inventory-item');
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
            const button = selectedItem.querySelector('button');
            if (button && !button.disabled) {
                button.click();
            }
        }
    }
}

function showSkillsModal() {
    const modal = document.getElementById('skills-modal');
    const skillsList = document.getElementById('skills-list');
    const pointsSpan = document.getElementById('modal-skill-points');
    
    pointsSpan.textContent = player.skill_points;
    skillsList.innerHTML = '';
    
    const skillDescriptions = {
        'power_strike': 'Increases physical damage (+5 per level)',
        'quick_reflexes': 'Increases dodge chance (+3% per level)',
        'arcane_knowledge': 'Increases magic damage (+5 per level)',
        'iron_skin': 'Increases defense (+3 per level)',
        'critical_eye': 'Increases critical hit chance (+5% per level)',
        'life_drain': 'Lifesteal on hit (+10% per level)'
    };
    
    let index = 0;
    for (const [skill, level] of Object.entries(player.skills)) {
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skill-item';
        if (index === 0) skillDiv.classList.add('selected');
        
        const title = skill.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        
        skillDiv.innerHTML = `
            <h4>${title} (Level ${level})</h4>
            <p>${skillDescriptions[skill]}</p>
            <button class="btn-small" onclick="upgradeSkill('${skill}')" 
                    ${player.skill_points === 0 ? 'disabled' : ''}>
                Upgrade (1 point)
            </button>
        `;
        
        skillsList.appendChild(skillDiv);
        index++;
    }
    
    activeModal = 'skills';
    selectedIndex = 0;
    modal.classList.add('active');
}

function upgradeSkill(skillName) {
    socket.emit('upgrade_skill', { skill: skillName });
}

function showInventoryModal() {
    const modal = document.getElementById('inventory-modal');
    const equippedDiv = document.getElementById('equipped-items');
    const inventoryDiv = document.getElementById('inventory-items');
    
    equippedDiv.innerHTML = '<h3>Equipped</h3>';
    
    if (player.weapon) {
        const rangedIcon = player.weapon.ranged ? ' 🏹' : ' ⚔️';
        const rangeText = player.weapon.ranged ? `<p>Range: ${player.weapon.range} tiles</p>` : '';
        equippedDiv.innerHTML += `
            <div class="item-card">
                <h4 class="rarity-${player.weapon.rarity || 'legendary'}">${player.weapon.name}${rangedIcon}</h4>
                <p>Damage: ${player.weapon.damage}</p>
                ${rangeText}
            </div>
        `;
    } else {
        equippedDiv.innerHTML += '<p>No weapon equipped</p>';
    }
    
    if (player.armor) {
        equippedDiv.innerHTML += `
            <div class="item-card">
                <h4 class="rarity-${player.armor.rarity || 'common'}">${player.armor.name}</h4>
                <p>Defense: ${player.armor.defense}</p>
            </div>
        `;
    } else {
        equippedDiv.innerHTML += '<p>No armor equipped</p>';
    }
    
    inventoryDiv.innerHTML = '<h3>Inventory</h3>';
    
    if (inventory.length === 0) {
        inventoryDiv.innerHTML += '<p>No items in inventory</p>';
    } else {
        inventory.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'item-card inventory-item';
            if (index === 0) itemDiv.classList.add('selected');
            
            const canEquip = player.level >= (item.min_level || 1);
            const rangedIcon = item.ranged ? ' 🏹' : (item.type === 'weapon' ? ' ⚔️' : '');
            const rangeText = item.ranged ? `<p>Range: ${item.range} tiles</p>` : '';
            
            if (item.type === 'weapon') {
                itemDiv.innerHTML = `
                    <h4 class="rarity-${item.rarity || 'legendary'}">${item.name}${rangedIcon}</h4>
                    <p>Damage: ${item.damage}</p>
                    ${rangeText}
                    <p>Min Level: ${item.min_level || 1}</p>
                    ${item.lore ? `<p class="lore-text">${item.lore}</p>` : ''}
                    <button class="btn-small" onclick="equipItem(${index})" 
                            ${!canEquip ? 'disabled' : ''}>
                        ${canEquip ? 'Equip' : 'Level Required'}
                    </button>
                `;
            } else {
                itemDiv.innerHTML = `
                    <h4 class="rarity-${item.rarity || 'legendary'}">${item.name}</h4>
                    <p>Defense: ${item.defense}</p>
                    <p>Min Level: ${item.min_level || 1}</p>
                    ${item.lore ? `<p class="lore-text">${item.lore}</p>` : ''}
                    <button class="btn-small" onclick="equipItem(${index})" 
                            ${!canEquip ? 'disabled' : ''}>
                        ${canEquip ? 'Equip' : 'Level Required'}
                    </button>
                `;
            }
            
            inventoryDiv.appendChild(itemDiv);
        });
    }
    
    activeModal = 'inventory';
    selectedIndex = 0;
    modal.classList.add('active');
}


function equipItem(index) {
    const item = inventory[index];
    socket.emit('equip_item', { item });
    inventory.splice(index, 1);
}

function showLoreModal(title, items, type) {
    const modal = document.getElementById('lore-modal');
    const titleEl = document.getElementById('lore-title');
    const contentEl = document.getElementById('lore-content');
    
    titleEl.textContent = title;
    contentEl.innerHTML = '';
    
    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'lore-item';
        
        if (type === 'weapon') {
            itemDiv.innerHTML = `
                <h3 class="rarity-legendary">${item.name}</h3>
                <p><strong>Type:</strong> ${item.type}</p>
                <p><strong>Damage:</strong> ${item.damage}</p>
                <p><strong>Min Level:</strong> ${item.min_level}</p>
                <p class="lore-text">"${item.lore}"</p>
            `;
        } else if (type === 'boss') {
            itemDiv.innerHTML = `
                <h3 class="rarity-legendary">${item.name}</h3>
                <p><strong>Level:</strong> ${item.level}</p>
                <p><strong>HP:</strong> ${item.hp}</p>
                <p><strong>Damage:</strong> ${item.damage}</p>
                <p class="lore-text">"${item.lore}"</p>
            `;
        }
        
        contentEl.appendChild(itemDiv);
    });
    
    modal.classList.add('active');
}

function showLevelUpModal() {
    // Create toast notification instead of modal
    const toast = document.createElement('div');
    toast.className = 'level-up-toast';
    toast.innerHTML = `
        <div class="toast-content">
            <h2>🎉 LEVEL UP! 🎉</h2>
            <p>You reached level ${player.level}!</p>
            <p class="toast-hint">Press L to spend skill points</p>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
