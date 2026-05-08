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
let activeModal = null; // Track which modal is open ('skills', 'inventory', 'loot', or null)
let selectedIndex = 0; // Track selected item in modal
let deathAnimations = []; // Track enemy death animations
let lootDrops = []; // Track loot drops on the ground { id, x, y, items: [], gold }
const LOOT_RANGE = 5; // Range for area loot in tiles

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
    
    // Initialize authentication
    initAuth();
    setupAuthSocketHandlers();
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('connected', (data) => {
        console.log('Player ID:', data.player_id);
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
            else if (key === 'x') {
                e.preventDefault();
                discardSelectedItem();
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
        else if (key === 'f') {
            // Open area loot modal
            if (!keysPressed[key]) {
                e.preventDefault();
                keysPressed[key] = true;
                showAreaLootModal();
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
        lootDrops = []; // Clear loot drops when changing floors
        
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
            
            // Add loot drop if provided by server
            if (data.loot_drop) {
                lootDrops.push(data.loot_drop);
            }
        }
        
        // Delete enemy for all players
        delete enemies[data.enemy_id];
        
        // Update player data if this player received XP
        if (data.updated_players && data.updated_players[socket.id]) {
            player = data.updated_players[socket.id];
        }
        
        // Handle XP distribution for all players who dealt damage
        if (data.xp_distribution && data.xp_distribution[socket.id]) {
            const xpGained = data.xp_distribution[socket.id];
            addLog(`+${xpGained} XP (damage contribution)`, 'loot');
            
            // Check if this player leveled up
            if (data.leveled_up_players && data.leveled_up_players[socket.id]) {
                showLevelUpModal();
            }
        }
        
        // Update player stats if this is the attacker
        if (data.attacker_id === socket.id) {
            if (data.is_ranged) {
                addLog(`🏹 Enemy defeated with ranged attack!`, 'loot');
            } else {
                addLog(`⚔️ Enemy defeated!`, 'loot');
            }
            
            if (data.loot_drop) {
                addLog(`Loot dropped at (${enemy.x}, ${enemy.y}). Press F to loot nearby items.`, 'loot');
            }
            
            updateHUD();
        } else if (data.xp_distribution && data.xp_distribution[socket.id]) {
            // Other players who dealt damage
            addLog(`Enemy defeated! You contributed to the kill.`, 'loot');
            updateHUD();
        } else {
            // Players who didn't participate
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
    
    // Loot pickup
    socket.on('loot_picked_up', (data) => {
        // Remove loot drop from local array for all players
        lootDrops = lootDrops.filter(drop => drop.id !== data.loot_id);
        
        // Only update inventory for the player who picked it up
        if (data.player_id === socket.id) {
            player = data.player;
            
            if (data.items && data.items.length > 0) {
                data.items.forEach(item => {
                    inventory.push(item);
                    const rangedTag = item.ranged ? ' 🏹' : '';
                    addLog(`Picked up: ${item.name}${rangedTag}!`, 'loot');
                });
            }
            
            if (data.gold > 0) {
                addLog(`+${data.gold} Gold`, 'loot');
            }
            
            updateHUD();
            
            // Refresh loot modal if it's currently open
            if (activeModal === 'loot') {
                showAreaLootModal();
            }
        }
        
        renderDungeon();
    });
    
    // Loot discard
    socket.on('loot_discarded', (data) => {
        // Remove loot drop from local array for all players
        lootDrops = lootDrops.filter(drop => drop.id !== data.loot_id);
        
        // Only show message for the player who discarded it
        if (data.player_id === socket.id) {
            addLog('Loot discarded', 'loot');
            
            // Refresh loot modal if it's currently open
            if (activeModal === 'loot') {
                showAreaLootModal();
            }
        }
        
        renderDungeon();
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
    
    setupCanvas(ctx, canvas);
    const viewport = calculateViewport(player);
    
    renderTiles(ctx, dungeon, viewport, sprites);
    renderStairs(ctx, entities, viewport, sprites, spriteRenderer);
    renderLootDrops(ctx, lootDrops, player, viewport, spriteRenderer);
    renderDeathAnimations(ctx, deathAnimations, viewport, sprites);
    renderEnemies(ctx, enemies, viewport, sprites, spriteRenderer);
    renderOtherPlayers(ctx, otherPlayers, viewport, sprites, spriteRenderer);
    renderPlayer(ctx, player, viewport, sprites, spriteRenderer, attackAnimations, isWalking, walkFrameIndex);
    renderAttackAnimations();
    renderDebugInfo(ctx, player, debugMode);
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
    document.getElementById('player-gold').textContent = player.gold || 0;
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
    } else if (activeModal === 'loot') {
        document.getElementById('loot-modal').classList.remove('active');
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
    } else if (activeModal === 'loot') {
        items = document.querySelectorAll('.loot-item');
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
    } else if (activeModal === 'loot') {
        const items = document.querySelectorAll('.loot-item');
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
            const button = selectedItem.querySelector('button');
            if (button && !button.disabled) {
                button.click();
            }
        }
    }
}

function discardSelectedItem() {
    if (!activeModal) return;
    
    if (activeModal === 'inventory') {
        const items = document.querySelectorAll('.inventory-item');
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
            const discardButton = selectedItem.querySelector('.btn-discard');
            if (discardButton) {
                discardButton.click();
            }
        }
    } else if (activeModal === 'loot') {
        const items = document.querySelectorAll('.loot-item');
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
            const discardButton = selectedItem.querySelector('.btn-discard');
            if (discardButton) {
                discardButton.click();
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
                    <div class="item-actions">
                        <button class="btn-small" onclick="equipItem(${index})" 
                                ${!canEquip ? 'disabled' : ''}>
                            ${canEquip ? 'Equip' : 'Level Required'}
                        </button>
                        <button class="btn-small btn-discard" onclick="discardInventoryItem(${index})">
                            Discard (X)
                        </button>
                    </div>
                `;
            } else {
                itemDiv.innerHTML = `
                    <h4 class="rarity-${item.rarity || 'legendary'}">${item.name}</h4>
                    <p>Defense: ${item.defense}</p>
                    <p>Min Level: ${item.min_level || 1}</p>
                    ${item.lore ? `<p class="lore-text">${item.lore}</p>` : ''}
                    <div class="item-actions">
                        <button class="btn-small" onclick="equipItem(${index})" 
                                ${!canEquip ? 'disabled' : ''}>
                            ${canEquip ? 'Equip' : 'Level Required'}
                        </button>
                        <button class="btn-small btn-discard" onclick="discardInventoryItem(${index})">
                            Discard (X)
                        </button>
                    </div>
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

function showAreaLootModal() {
    if (!player) return;
    
    // Find all loot within range
    const nearbyLoot = lootDrops.filter(loot => {
        const distance = Math.max(Math.abs(player.x - loot.x), Math.abs(player.y - loot.y));
        return distance <= LOOT_RANGE;
    });
    
    if (nearbyLoot.length === 0) {
        // If modal is open and no loot remains, close it
        if (activeModal === 'loot') {
            closeActiveModal();
            addLog('All loot collected!', 'loot');
        } else {
            addLog('No loot nearby!', 'loot');
        }
        return;
    }
    
    const modal = document.getElementById('loot-modal');
    const lootList = document.getElementById('loot-list');
    
    lootList.innerHTML = '';
    
    nearbyLoot.forEach((loot, index) => {
        const lootDiv = document.createElement('div');
        lootDiv.className = 'loot-item';
        if (index === 0) lootDiv.classList.add('selected');
        
        const distance = Math.max(Math.abs(player.x - loot.x), Math.abs(player.y - loot.y));
        
        let itemsHtml = '';
        if (loot.items && loot.items.length > 0) {
            itemsHtml = '<div class="loot-items">';
            loot.items.forEach(item => {
                const rangedIcon = item.ranged ? ' 🏹' : (item.type === 'weapon' ? ' ⚔️' : ' 🛡️');
                const rarityClass = item.rarity || 'common';
                itemsHtml += `<div class="loot-item-detail rarity-${rarityClass}">${item.name}${rangedIcon}</div>`;
            });
            itemsHtml += '</div>';
        }
        
        let rewardsHtml = '';
        if (loot.gold > 0) {
            rewardsHtml = '<div class="loot-rewards">';
            rewardsHtml += `<span class="loot-gold">+${loot.gold} Gold</span>`;
            rewardsHtml += '</div>';
        }
        
        lootDiv.innerHTML = `
            <h4>Loot at (${loot.x}, ${loot.y}) - ${distance} tiles away</h4>
            ${itemsHtml}
            ${rewardsHtml}
            <div class="item-actions">
                <button class="btn-small" onclick="pickupLoot('${loot.id}')">
                    Pick Up
                </button>
                <button class="btn-small btn-discard" onclick="discardLoot('${loot.id}')">
                    Discard (X)
                </button>
            </div>
        `;
        
        lootList.appendChild(lootDiv);
    });
    
    activeModal = 'loot';
    selectedIndex = 0;
    modal.classList.add('active');
}

function pickupLoot(lootId) {
    socket.emit('pickup_loot', { loot_id: lootId });
    // Don't close modal - let player continue picking up loot
}

function discardInventoryItem(index) {
    const item = inventory[index];
    if (confirm(`Discard ${item.name}? This cannot be undone.`)) {
        inventory.splice(index, 1);
        addLog(`Discarded ${item.name}`, 'loot');
        showInventoryModal(); // Refresh the modal
    }
}

function discardLoot(lootId) {
    if (confirm('Discard this loot? This cannot be undone.')) {
        socket.emit('discard_loot', { loot_id: lootId });
    }
}
