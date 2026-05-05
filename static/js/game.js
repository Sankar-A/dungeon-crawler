// Game state
let socket;
let player = null;
let dungeon = null;
let entities = null;
let enemies = {};
let inventory = [];
let rareWeapons = [];
let rareBosses = [];

// Canvas
const canvas = document.getElementById('dungeon-canvas');
const ctx = canvas ? canvas.getContext('2d') : null;
const TILE_SIZE = 16;
const VIEWPORT_WIDTH = 50;
const VIEWPORT_HEIGHT = 37;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    socket = io();
    
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
        
        document.getElementById('start-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        document.getElementById('game-screen').style.display = 'grid';
        
        updateHUD();
        renderDungeon();
    });
    
    // Movement
    document.addEventListener('keydown', (e) => {
        if (!player) return;
        
        const key = e.key.toLowerCase();
        let direction = null;
        
        if (key === 'w' || key === 'arrowup') direction = 'up';
        else if (key === 's' || key === 'arrowdown') direction = 'down';
        else if (key === 'a' || key === 'arrowleft') direction = 'left';
        else if (key === 'd' || key === 'arrowright') direction = 'right';
        
        if (direction) {
            e.preventDefault();
            socket.emit('move', { direction });
        }
    });
    
    // Player moved
    socket.on('player_moved', (data) => {
        if (data.player_id === socket.id) {
            player.x = data.x;
            player.y = data.y;
            renderDungeon();
        }
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
                // Check if adjacent
                const dx = Math.abs(player.x - enemy.x);
                const dy = Math.abs(player.y - enemy.y);
                
                if (dx <= 1 && dy <= 1) {
                    socket.emit('attack_enemy', { enemy_id: enemyId });
                } else {
                    addLog('Enemy too far away!', 'damage');
                }
                break;
            }
        }
    });
    
    socket.on('combat_result', (data) => {
        player = data.player;
        const result = data.result;
        
        addLog(`You dealt ${result.player_damage} damage!${result.critical ? ' CRITICAL!' : ''}`, 'damage');
        if (result.dodged) {
            addLog('You dodged the attack!', 'heal');
        } else if (result.enemy_damage > 0) {
            addLog(`Enemy dealt ${result.enemy_damage} damage!`, 'damage');
        }
        
        updateHUD();
        renderDungeon();
    });
    
    socket.on('enemy_defeated', (data) => {
        player = data.player;
        delete enemies[data.enemy_id];
        
        addLog(`Enemy defeated! +${data.loot.xp} XP`, 'loot');
        
        if (data.loot.items.length > 0) {
            data.loot.items.forEach(item => {
                inventory.push(item);
                addLog(`Found: ${item.name}!`, 'loot');
            });
        }
        
        if (data.leveled_up) {
            showLevelUpModal();
        }
        
        updateHUD();
        renderDungeon();
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


// Rendering
function renderDungeon() {
    if (!ctx || !dungeon || !player) return;
    
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
                ctx.fillStyle = tile === 0 ? '#333' : '#111';
                ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                
                // Grid lines
                ctx.strokeStyle = '#222';
                ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }
        }
    }
    
    // Draw stairs
    if (entities && entities.stairs) {
        const stairsX = entities.stairs[0] - startX;
        const stairsY = entities.stairs[1] - startY;
        
        if (stairsX >= 0 && stairsX < VIEWPORT_WIDTH && 
            stairsY >= 0 && stairsY < VIEWPORT_HEIGHT) {
            ctx.fillStyle = '#f39c12';
            ctx.fillRect(stairsX * TILE_SIZE + 2, stairsY * TILE_SIZE + 2, 
                        TILE_SIZE - 4, TILE_SIZE - 4);
        }
    }
    
    // Draw enemies
    for (const enemy of Object.values(enemies)) {
        const enemyX = enemy.x - startX;
        const enemyY = enemy.y - startY;
        
        if (enemyX >= 0 && enemyX < VIEWPORT_WIDTH && 
            enemyY >= 0 && enemyY < VIEWPORT_HEIGHT) {
            ctx.fillStyle = enemy.is_boss ? '#9b59b6' : '#e74c3c';
            ctx.fillRect(enemyX * TILE_SIZE + 2, enemyY * TILE_SIZE + 2, 
                        TILE_SIZE - 4, TILE_SIZE - 4);
            
            // HP bar for enemies
            const hpPercent = enemy.hp / enemy.max_hp;
            ctx.fillStyle = '#2ecc71';
            ctx.fillRect(enemyX * TILE_SIZE, enemyY * TILE_SIZE - 3, 
                        TILE_SIZE * hpPercent, 2);
        }
    }
    
    // Draw player
    const playerScreenX = Math.floor(VIEWPORT_WIDTH / 2);
    const playerScreenY = Math.floor(VIEWPORT_HEIGHT / 2);
    ctx.fillStyle = '#3498db';
    ctx.fillRect(playerScreenX * TILE_SIZE + 2, playerScreenY * TILE_SIZE + 2, 
                TILE_SIZE - 4, TILE_SIZE - 4);
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
    
    for (const [skill, level] of Object.entries(player.skills)) {
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skill-item';
        
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
    }
    
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
        equippedDiv.innerHTML += `
            <div class="item-card">
                <h4 class="rarity-${player.weapon.rarity || 'legendary'}">${player.weapon.name}</h4>
                <p>Damage: ${player.weapon.damage}</p>
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
            itemDiv.className = 'item-card';
            
            const canEquip = player.level >= (item.min_level || 1);
            
            itemDiv.innerHTML = `
                <h4 class="rarity-${item.rarity || 'legendary'}">${item.name}</h4>
                <p>${item.type === 'weapon' ? 'Damage: ' + item.damage : 'Defense: ' + item.defense}</p>
                <p>Min Level: ${item.min_level || 1}</p>
                ${item.lore ? `<p class="lore-text">${item.lore}</p>` : ''}
                <button class="btn-small" onclick="equipItem(${index})" 
                        ${!canEquip ? 'disabled' : ''}>
                    ${canEquip ? 'Equip' : 'Level Required'}
                </button>
            `;
            
            inventoryDiv.appendChild(itemDiv);
        });
    }
    
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
    const modal = document.getElementById('level-up-modal');
    document.getElementById('new-level').textContent = player.level;
    modal.classList.add('active');
}
