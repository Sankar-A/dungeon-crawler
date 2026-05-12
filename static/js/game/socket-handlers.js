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
    
    socket.on('equip_failed', (data) => {
        console.error('Equip failed:', data);
        addLog(`Cannot equip: ${data.reason}`, 'error');
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
    
    // Telegraph event handlers
    socket.on('telegraph_started', (data) => {
        console.log('Telegraph started:', data);
        
        // Show telegraph UI
        if (telegraphUI) {
            telegraphUI.show(data);
        }
        
        // Add attack zone visualization
        if (attackZoneRenderer && data.attack_zone_tiles) {
            attackZoneRenderer.addZone(data.attack_zone_tiles, data.ability.attack_zone?.type || 'none');
        }
        
        // Add telegraph warning effect above boss
        if (effectRenderer && data.boss_position) {
            effectRenderer.addTelegraphWarning(
                data.boss_position.x,
                data.boss_position.y,
                data.ability.name
            );
        }
        
        // Add combat log message
        addLog(`${data.boss_name} is preparing ${data.ability.name}!`, 'boss-attack');
    });
    
    socket.on('telegraph_updated', (data) => {
        console.log('Telegraph updated:', data);
        
        // Update countdown
        if (telegraphUI) {
            telegraphUI.update(data.turns_remaining);
        }
    });
    
    socket.on('telegraph_ended', (data) => {
        console.log('Telegraph ended:', data);
        
        // Hide telegraph UI
        if (telegraphUI) {
            telegraphUI.hide();
        }
        
        // Clear attack zones
        if (attackZoneRenderer) {
            attackZoneRenderer.clearZones();
        }
        
        // Remove telegraph warning
        if (effectRenderer) {
            effectRenderer.removeTelegraphWarning();
        }
        
        // Add combat log message
        const result = data.execution_result;
        if (result.avoided) {
            addLog(`You avoided ${data.ability_name} by staying out of range!`, 'success');
        } else {
            addLog(`${data.ability_name} unleashed!`, 'boss-attack');
            if (result.damage > 0) {
                addLog(`Took ${result.damage} damage!`, 'damage');
            }
        }
    });
    
    socket.on('telegraph_cancelled', (data) => {
        console.log('Telegraph cancelled:', data);
        
        // Clean up all telegraph UI elements
        if (telegraphUI) {
            telegraphUI.hide();
        }
        if (attackZoneRenderer) {
            attackZoneRenderer.clearZones();
        }
        if (effectRenderer) {
            effectRenderer.removeTelegraphWarning();
        }
    });
    
    // Blink event handlers
    socket.on('blink_activated', (data) => {
        console.log('Blink activated:', data);
        
        // Add blink effects at start and end positions
        if (effectRenderer) {
            effectRenderer.addBlinkEffect(data.old_position.x, data.old_position.y, 'start');
            effectRenderer.addBlinkEffect(data.new_position.x, data.new_position.y, 'end');
        }
        
        // Update player position if it's us
        if (data.player_id === socket.id) {
            player.x = data.new_position.x;
            player.y = data.new_position.y;
            playerVisualX = data.new_position.x;
            playerVisualY = data.new_position.y;
        } else if (otherPlayers[data.player_id]) {
            // Update other player position
            otherPlayers[data.player_id].x = data.new_position.x;
            otherPlayers[data.player_id].y = data.new_position.y;
        }
        
        // Add combat log message
        addLog(`${data.player_name} blinked ${data.distance} tiles!`, 'info');
        
        renderDungeon();
    });
    
    socket.on('blink_cooldown_started', (data) => {
        console.log('Blink cooldown started:', data);
        
        // Start cooldown UI
        if (cooldownUI) {
            cooldownUI.startCooldown(data.cooldown);
        }
    });
    
    socket.on('blink_failed', (data) => {
        console.log('Blink failed:', data);
        
        // Display error message
        addLog(`Blink failed: ${data.reason}`, 'error');
        
        // Exit blink targeting mode if active
        if (blinkTargetingMode) {
            blinkTargetingMode = false;
            validBlinkTiles = [];
            renderDungeon();
        }
    });
    
    socket.on('blink_range_response', (data) => {
        console.log('Blink range response:', data);
        
        // Store valid tiles for targeting
        validBlinkTiles = data.valid_tiles || [];
        
        // Trigger blink targeting UI update (will be rendered in game loop)
        renderDungeon();
    });
    
    // Resistance event handlers
    socket.on('resistance_activated', (data) => {
        console.log('Resistance activated:', data);
        
        // Show resistance UI
        if (resistanceUI) {
            resistanceUI.show(data);
        }
        
        // Update player state if it's us
        if (data.player_id === socket.id) {
            player = data.player;
        }
        
        // Add combat log message
        let message = `${data.player_name} activated ${data.element.toUpperCase()} resistance!`;
        if (data.replaced_element) {
            message += ` (replaced ${data.replaced_element.toUpperCase()})`;
        }
        addLog(message, 'info');
        
        updateHUD();
    });
    
    socket.on('resistance_expired', (data) => {
        console.log('Resistance expired:', data);
        
        // Hide resistance UI if it's us
        if (data.player_id === socket.id && resistanceUI) {
            resistanceUI.hide();
        }
        
        // Add combat log message
        addLog(`${data.element.toUpperCase()} resistance expired`, 'info');
    });
    
    // Avoidance combat log event handlers
    socket.on('attack_avoided', (data) => {
        console.log('Attack avoided:', data);
        
        // Add success message to combat log
        if (data.player_id === socket.id) {
            addLog(`You avoided ${data.ability_name} by staying out of range!`, 'success');
        } else {
            addLog(`${data.player_name} avoided ${data.ability_name}!`, 'info');
        }
    });
    
    socket.on('damage_resisted', (data) => {
        console.log('Damage resisted:', data);
        
        // Add resistance info message to combat log
        if (data.player_id === socket.id) {
            addLog(`Your ${data.element.toUpperCase()} resistance reduced damage by ${data.reduction_amount} (${data.reduction_percent}%)!`, 'info');
        } else {
            addLog(`${data.player_name}'s resistance reduced damage by ${data.reduction_percent}%`, 'info');
        }
    });
    
    // Inventory discard event handler
    socket.on('inventory_item_discarded', (data) => {
        console.log('Inventory item discarded:', data);
        
        // Update player and inventory
        player = data.player;
        inventory = player.inventory || [];
        
        // Add log message
        addLog(`Discarded ${data.item_name}`, 'loot');
        
        // Adjust selectedIndex if needed
        if (selectedIndex >= inventory.length) {
            selectedIndex = Math.max(0, inventory.length - 1);
        }
        
        // Refresh the modal, preserving selection
        if (activeModal === 'inventory-modal') {
            showInventoryModal(true);
        }
        
        updateHUD();
    });
}
