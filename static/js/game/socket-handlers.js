// Socket event handlers
function setupSocketHandlers() {
    socket.on('character_created', (data) => {
        player = data.player;
        dungeon = data.dungeon;
        entities = data.entities;
        enemies = data.enemies;
        otherPlayers = data.other_players || {};
        inventory = player.inventory || [];
        lootDrops = {};
        
        // Initialize visual position to match actual position
        playerVisualX = player.x;
        playerVisualY = player.y;
        
        document.getElementById('start-screen').classList.remove('active');
        document.getElementById('login-screen').classList.remove('active');
        document.getElementById('character-select-screen').classList.remove('active');
        document.getElementById('character-creation-screen').classList.remove('active');
        
        document.getElementById('game-screen').classList.add('active');
        document.getElementById('game-screen').style.display = 'grid';
        
        updateHUD();
        renderDungeon();
        startAnimationLoop();
    });
    
    socket.on('player_joined', (data) => {
        otherPlayers[data.player_id] = {
            x: data.x,
            y: data.y,
            name: data.name
        };
        renderDungeon();
    });
    
    socket.on('player_left', (data) => {
        delete otherPlayers[data.player_id];
        renderDungeon();
    });
    
    socket.on('player_moved', (data) => {
        if (data.player_id === socket.id) {
            player.x = data.x;
            player.y = data.y;
            // Visual position will interpolate to this in the render loop
            // Don't stop walking here - let keyup handler control it
            // This allows walk animation to continue while keys are held
        } else {
            if (otherPlayers[data.player_id]) {
                otherPlayers[data.player_id].x = data.x;
                otherPlayers[data.player_id].y = data.y;
            }
        }
        renderDungeon();
    });
    
    socket.on('combat_result', (data) => {
        const result = data.result;
        player = data.player;
        const enemyId = data.enemy_id;
        
        console.log('Combat result received:', result, 'enemy_id:', enemyId);
        
        // Create attack animation
        if (enemyId && enemies[enemyId]) {
            const enemy = enemies[enemyId];
            const isRanged = player.weapon && player.weapon.ranged;
            console.log('Creating attack animation - isRanged:', isRanged, 'weapon:', player.weapon);
            createAttackAnimation(player.x, player.y, enemy.x, enemy.y, isRanged);
        }
        
        // Create special attack visual effect if boss used special attack
        if (result.special_attack && enemyId && enemies[enemyId]) {
            const enemy = enemies[enemyId];
            const specialAttack = result.special_attack;
            createSpecialAttackEffect(specialAttack.ability, enemy.x, enemy.y, player.x, player.y);
        }
        
        addLog(`You dealt ${result.player_damage} damage!`, 'combat');
        if (result.enemy_damage > 0) {
            if (result.special_attack) {
                addLog(`${result.special_attack.description}`, 'boss-attack');
                addLog(`Took ${result.enemy_damage} damage!`, 'damage');
            } else {
                addLog(`Enemy dealt ${result.enemy_damage} damage!`, 'damage');
            }
        }
        
        updateHUD();
        renderDungeon();
    });
    
    socket.on('enemy_defeated', (data) => {
        // Create death animation
        if (enemies[data.enemy_id]) {
            const enemy = enemies[data.enemy_id];
            createDeathAnimation(enemy.x, enemy.y, enemy.is_boss);
        }
        
        delete enemies[data.enemy_id];
        
        if (data.loot_drop) {
            lootDrops[data.loot_drop.id] = data.loot_drop;
        }
        
        for (const [pid, xp] of Object.entries(data.xp_distribution)) {
            if (pid === socket.id) {
                addLog(`You gained ${xp} XP!`, 'xp');
            }
        }
        
        if (data.leveled_up_players[socket.id]) {
            showLevelUpModal(data.updated_players[socket.id].level);
        }
        
        if (data.updated_players[socket.id]) {
            player = data.updated_players[socket.id];
        }
        
        updateHUD();
        renderDungeon();
    });
    
    socket.on('enemy_hp_updated', (data) => {
        if (enemies[data.enemy_id]) {
            enemies[data.enemy_id].hp = data.hp;
            enemies[data.enemy_id].max_hp = data.max_hp;
        }
        renderDungeon();
    });
    
    socket.on('reached_stairs', (data) => {
        showConfirmation(
            'Descend Stairs',
            `You reached the stairs to floor ${data.floor + 1}. Descend deeper into the dungeon?`,
            () => {
                socket.emit('descend_stairs');
            }
        );
    });
    
    socket.on('floor_changed', (data) => {
        player = data.player;
        dungeon = data.dungeon;
        entities = data.entities;
        enemies = data.enemies;
        lootDrops = {};
        
        addLog(`Descended to floor ${data.floor}!`, 'floor');
        updateHUD();
        renderDungeon();
    });
    
    socket.on('skill_upgraded', (data) => {
        player = data.player;
        updateHUD();
        showSkillsModal(true);
    });
    
    socket.on('item_equipped', (data) => {
        player = data.player;
        inventory = player.inventory || [];
        updateHUD();
        showInventoryModal(true); // Preserve selection after equipping
    });
    
    socket.on('loot_picked_up', (data) => {
        delete lootDrops[data.loot_id];
        
        if (data.player_id === socket.id) {
            player = data.player;
            inventory = player.inventory || [];
            addLog(`Picked up ${data.gold} gold!`, 'loot');
            for (const item of data.items) {
                addLog(`Found: ${item.name}!`, 'loot');
            }
            
            // Refresh loot modal if it's open
            if (activeModal === 'loot-modal') {
                const nearbyLoot = Object.values(lootDrops).filter(loot => {
                    if (loot.floor !== player.floor) return false;
                    const distance = Math.max(
                        Math.abs(player.x - loot.x),
                        Math.abs(player.y - loot.y)
                    );
                    return distance <= 5;
                });
                
                if (nearbyLoot.length > 0) {
                    // Refresh modal without closing, preserve selection
                    showAreaLootModal(true);
                } else {
                    // Close if no more loot
                    closeModal('loot-modal');
                }
            }
        }
        
        updateHUD();
        renderDungeon();
    });
    
    socket.on('loot_discarded', (data) => {
        delete lootDrops[data.loot_id];
        
        // Refresh loot modal if it's open
        if (activeModal === 'loot-modal') {
            const nearbyLoot = Object.values(lootDrops).filter(loot => {
                if (loot.floor !== player.floor) return false;
                const distance = Math.max(
                    Math.abs(player.x - loot.x),
                    Math.abs(player.y - loot.y)
                );
                return distance <= 5;
            });
            
            if (nearbyLoot.length > 0) {
                // Refresh modal without closing, preserve selection
                showAreaLootModal(true);
            } else {
                // Close if no more loot
                closeModal('loot-modal');
            }
        }
        
        renderDungeon();
    });
    
    socket.on('rare_weapons_list', (data) => {
        showLoreModal('Legendary Weapons', data.weapons);
    });
    
    socket.on('rare_bosses_list', (data) => {
        showLoreModal('Epic Bosses', data.bosses);
    });
}
