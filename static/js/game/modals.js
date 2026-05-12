// Modal management
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        activeModal = null;
        selectedIndex = 0;
    }
}

function navigateModal(direction) {
    if (!activeModal || confirmationModalOpen) return; // Don't navigate if confirmation is open
    
    let items = document.querySelectorAll(`.${activeModal}-item`);
    if (items.length === 0) return;
    
    // Remove selected class from current item
    if (items[selectedIndex]) {
        items[selectedIndex].classList.remove('selected');
    }
    
    selectedIndex += direction;
    if (selectedIndex < 0) selectedIndex = items.length - 1;
    if (selectedIndex >= items.length) selectedIndex = 0;
    
    items[selectedIndex].classList.add('selected');
    items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

function selectModalItemPositive() {
    if (!activeModal || confirmationModalOpen) return; // Don't select if confirmation is open
    
    let items = document.querySelectorAll(`.${activeModal}-item`);
    if (items.length === 0 || selectedIndex >= items.length) return;
    
    console.log('E pressed - activeModal:', activeModal, 'selectedIndex:', selectedIndex);
    
    // Find the first button (positive action: upgrade, equip, pickup)
    const button = items[selectedIndex].querySelector('button:not([disabled])');
    if (button) {
        console.log('Clicking first button:', button.textContent);
        button.click();
    }
}

function selectModalItemNegative() {
    if (!activeModal || confirmationModalOpen) return; // Don't select if confirmation is open
    
    let items = document.querySelectorAll(`.${activeModal}-item`);
    if (items.length === 0 || selectedIndex >= items.length) return;
    
    console.log('X pressed - activeModal:', activeModal, 'selectedIndex:', selectedIndex);
    
    // Find all buttons and click the second one (negative action: discard)
    const buttons = items[selectedIndex].querySelectorAll('button:not([disabled])');
    
    console.log('Found', buttons.length, 'button(s):', Array.from(buttons).map(b => b.textContent));
    
    // Only click if there are at least 2 buttons (positive and negative actions)
    if (buttons.length >= 2) {
        console.log('Clicking second button:', buttons[1].textContent);
        buttons[1].click();
    } else {
        console.log('X pressed but only', buttons.length, 'button(s) found - ignoring');
    }
}

function showSkillsModal(preserveSelection = false) {
    if (!player) return;
    
    const modal = document.getElementById('skills-modal');
    const list = document.getElementById('skills-list');
    const pointsSpan = document.getElementById('modal-skill-points');
    
    // Save current selection if preserving
    const currentSelection = preserveSelection ? selectedIndex : 0;
    
    list.innerHTML = '';
    pointsSpan.textContent = player.skill_points;
    
    // Define skills with descriptions
    const skills = [
        { key: 'power_strike', name: 'Power Strike', desc: '+5 damage per level' },
        { key: 'quick_reflexes', name: 'Quick Reflexes', desc: '+3% dodge chance per level' },
        { key: 'arcane_knowledge', name: 'Arcane Knowledge', desc: 'Magic damage bonus' },
        { key: 'iron_skin', name: 'Iron Skin', desc: '+3 defense per level' },
        { key: 'critical_eye', name: 'Critical Eye', desc: '+5% crit chance per level' },
        { key: 'life_drain', name: 'Life Drain', desc: '+10% lifesteal per level' }
    ];
    
    skills.forEach((skill, index) => {
        const level = player.skills[skill.key] || 0;
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skills-modal-item skill-item';
        if (index === currentSelection) skillDiv.classList.add('selected');
        
        skillDiv.innerHTML = `
            <div>
                <strong>${skill.name}</strong>: Level ${level}
                <div style="font-size: 0.85rem; color: #bbb; margin-top: 0.25rem;">${skill.desc}</div>
            </div>
            <button onclick="upgradeSkill('${skill.key}')" ${player.skill_points === 0 ? 'disabled' : ''}>
                Upgrade (+1)
            </button>
        `;
        
        list.appendChild(skillDiv);
    });
    
    // Add Blink skill tree section
    const blinkHeader = document.createElement('h4');
    blinkHeader.textContent = 'Blink Ability';
    blinkHeader.style.marginTop = '1.5rem';
    blinkHeader.style.color = '#8800ff';
    list.appendChild(blinkHeader);
    
    const blinkTiers = [
        { level: 1, name: 'Blink I', range: 3, cooldown: 15, cost: 3, special: '' },
        { level: 2, name: 'Blink II', range: 4, cooldown: 12, cost: 3, special: '' },
        { level: 3, name: 'Blink III', range: 5, cooldown: 10, cost: 3, special: '' },
        { level: 4, name: 'Blink Master', range: 5, cooldown: 8, cost: 5, special: 'Can teleport through enemies' }
    ];
    
    const currentBlinkLevel = player.skills.blink || 0;
    
    blinkTiers.forEach((tier, index) => {
        const isUnlocked = currentBlinkLevel >= tier.level;
        const canUpgrade = currentBlinkLevel === tier.level - 1 && player.skill_points >= tier.cost;
        const isLocked = currentBlinkLevel < tier.level - 1;
        
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skills-modal-item skill-item';
        if (skills.length + index === currentSelection) skillDiv.classList.add('selected');
        
        let statusIcon = '';
        let statusColor = '';
        if (isUnlocked) {
            statusIcon = '✓';
            statusColor = '#00ff00';
        } else if (isLocked) {
            statusIcon = '🔒';
            statusColor = '#888';
        }
        
        skillDiv.innerHTML = `
            <div>
                <strong style="color: ${statusColor}">${statusIcon} ${tier.name}</strong>
                <div style="font-size: 0.85rem; color: #bbb; margin-top: 0.25rem;">
                    Range: ${tier.range} tiles | Cooldown: ${tier.cooldown}s
                    ${tier.special ? `<br><span style="color: #8800ff;">${tier.special}</span>` : ''}
                </div>
                ${isUnlocked ? '<div style="font-size: 0.85rem; color: #00ff00;">Unlocked - Press B to activate</div>' : ''}
            </div>
            ${!isUnlocked ? `
                <button onclick="upgradeSkill('blink')" 
                        ${!canUpgrade ? 'disabled' : ''}
                        ${isLocked ? 'title="Unlock previous tier first"' : ''}>
                    Unlock (${tier.cost} SP)
                </button>
            ` : '<div style="color: #00ff00;">Active</div>'}
        `;
        
        list.appendChild(skillDiv);
    });
    
    activeModal = 'skills-modal';
    selectedIndex = currentSelection;
    modal.classList.add('active');
}

function showInventoryModal(preserveSelection = false) {
    if (!player) return;
    
    const modal = document.getElementById('inventory-modal');
    const equipped = document.getElementById('equipped-items');
    const items = document.getElementById('inventory-items');
    
    // Save current selection if preserving
    const currentSelection = preserveSelection ? Math.min(selectedIndex, inventory.length - 1) : 0;
    
    equipped.innerHTML = '<h3>Equipped</h3>';
    items.innerHTML = '<h3>Inventory</h3>';
    
    if (player.weapon) {
        const weaponDiv = document.createElement('div');
        weaponDiv.className = 'equipped-item'; // Changed class to avoid selection
        weaponDiv.innerHTML = `
            <strong>${player.weapon.name}</strong>
            <div>Damage: ${player.weapon.damage}</div>
            ${player.weapon.range > 1 ? `<div>Range: ${player.weapon.range}</div>` : ''}
        `;
        equipped.appendChild(weaponDiv);
    }
    
    if (player.armor) {
        const armorDiv = document.createElement('div');
        armorDiv.className = 'equipped-item'; // Changed class to avoid selection
        armorDiv.innerHTML = `
            <strong>${player.armor.name}</strong>
            <div>Defense: ${player.armor.defense}</div>
        `;
        equipped.appendChild(armorDiv);
    }
    
    if (inventory.length === 0) {
        items.innerHTML += '<p>No items in inventory</p>';
        selectedIndex = 0;
    } else {
        // Separate resistance potions from equipment
        const resistancePotions = inventory.filter(item => 
            item.type === 'consumable' && item.subtype === 'resistance_potion'
        );
        const equipment = inventory.filter(item => 
            item.type !== 'consumable' || item.subtype !== 'resistance_potion'
        );
        
        // Display resistance potions section
        if (resistancePotions.length > 0) {
            const potionHeader = document.createElement('h4');
            potionHeader.textContent = 'Resistance Potions';
            potionHeader.style.marginTop = '1rem';
            items.appendChild(potionHeader);
            
            resistancePotions.forEach((potion, index) => {
                const actualIndex = inventory.indexOf(potion);
                const itemDiv = document.createElement('div');
                itemDiv.className = 'inventory-modal-item inventory-item';
                if (actualIndex === currentSelection) {
                    itemDiv.classList.add('selected');
                }
                
                const elementIcon = getElementIcon(potion.element);
                const elementColor = getElementColor(potion.element);
                const reduction = Math.round(potion.reduction * 100);
                
                // Check if resistance is already active
                const hasActiveResistance = player.active_resistance && player.active_resistance.element;
                const isDisabled = hasActiveResistance ? 'disabled' : '';
                const tooltip = hasActiveResistance ? 'Cannot use while resistance active' : '';
                
                itemDiv.innerHTML = `
                    <div>
                        <strong style="color: ${elementColor}">${elementIcon} ${potion.element.toUpperCase()} Resistance</strong>
                        <div>Reduces ${potion.element} damage by ${reduction}%</div>
                        <div>Duration: ${potion.duration} turns</div>
                    </div>
                    <div class="item-actions">
                        <button onclick="useResistancePotion(${actualIndex})" ${isDisabled} title="${tooltip}">Use</button>
                        <button onclick="discardInventoryItem(${actualIndex})" class="btn-discard">Discard</button>
                    </div>
                `;
                items.appendChild(itemDiv);
            });
        }
        
        // Display equipment section
        if (equipment.length > 0) {
            const equipHeader = document.createElement('h4');
            equipHeader.textContent = 'Equipment';
            equipHeader.style.marginTop = '1rem';
            items.appendChild(equipHeader);
            
            equipment.forEach((item, index) => {
                const actualIndex = inventory.indexOf(item);
                const itemDiv = document.createElement('div');
                itemDiv.className = 'inventory-modal-item inventory-item';
                if (actualIndex === currentSelection) {
                    itemDiv.classList.add('selected');
                }
                
                // Determine if it's a weapon or armor
                const isWeapon = item.damage !== undefined;
                const isArmor = item.defense !== undefined;
                
                // Build stats display
                let statsHtml = '';
                if (isWeapon) {
                    statsHtml = `<div>Damage: ${item.damage}</div>`;
                    if (item.ranged && item.range) {
                        statsHtml += `<div>Range: ${item.range}</div>`;
                    }
                } else if (isArmor) {
                    statsHtml = `<div>Defense: ${item.defense}</div>`;
                }
                
                itemDiv.innerHTML = `
                    <strong>${item.name}</strong>
                    ${statsHtml}
                    <button onclick="equipItem(${actualIndex})">Equip</button>
                    <button onclick="discardInventoryItem(${actualIndex})">Discard</button>
                `;
                items.appendChild(itemDiv);
            });
        }
        
        selectedIndex = currentSelection;
    }
    
    activeModal = 'inventory-modal';
    modal.classList.add('active');
}

// Helper functions for resistance potions
function getElementIcon(element) {
    const icons = {
        fire: '🔥',
        frost: '❄️',
        lightning: '⚡',
        poison: '☠️',
        shadow: '🌑',
        holy: '✨',
        void: '🌀'
    };
    return icons[element] || '🛡️';
}

function getElementColor(element) {
    const colors = {
        fire: '#ff4400',
        frost: '#00ccff',
        lightning: '#ffff00',
        poison: '#00ff00',
        shadow: '#8800ff',
        holy: '#ffdd00',
        void: '#aa00ff'
    };
    return colors[element] || '#ffffff';
}

function useResistancePotion(index) {
    socket.emit('use_resistance_potion', { potion_index: index });
    closeModal('inventory-modal');
}

function showAreaLootModal(preserveSelection = false) {
    if (!player) return;
    
    const modal = document.getElementById('loot-modal');
    const list = document.getElementById('loot-list');
    
    // Save current selection if preserving
    const currentSelection = preserveSelection ? selectedIndex : 0;
    
    list.innerHTML = '';
    
    const nearbyLoot = Object.values(lootDrops).filter(loot => {
        if (loot.floor !== player.floor) return false;
        const distance = Math.max(
            Math.abs(player.x - loot.x),
            Math.abs(player.y - loot.y)
        );
        return distance <= 5;
    });
    
    if (nearbyLoot.length === 0) {
        list.innerHTML = '<p>No loot nearby (within 5 tiles)</p>';
    } else {
        // Adjust selection if it's out of bounds
        const adjustedSelection = Math.min(currentSelection, nearbyLoot.length - 1);
        
        nearbyLoot.forEach((loot, index) => {
            const lootDiv = document.createElement('div');
            lootDiv.className = 'loot-modal-item loot-item';
            if (index === adjustedSelection) lootDiv.classList.add('selected');
            
            const distance = Math.max(
                Math.abs(player.x - loot.x),
                Math.abs(player.y - loot.y)
            );
            
            lootDiv.innerHTML = `
                <div><strong>Loot (${distance} tiles away)</strong></div>
                <div>Gold: ${loot.gold}</div>
                ${loot.items.length > 0 ? `<div>Items: ${loot.items.map(i => i.name).join(', ')}</div>` : ''}
                <button onclick="pickupLoot('${loot.id}')">Pick Up</button>
                <button onclick="discardLoot('${loot.id}')">Discard</button>
            `;
            
            list.appendChild(lootDiv);
        });
        
        selectedIndex = adjustedSelection;
    }
    
    activeModal = 'loot-modal';
    modal.classList.add('active');
}

function showLoreModal(title, items) {
    const modal = document.getElementById('lore-modal');
    const titleEl = document.getElementById('lore-title');
    const content = document.getElementById('lore-content');
    
    titleEl.textContent = title;
    content.innerHTML = '';
    
    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'lore-item';
        itemDiv.innerHTML = `
            <h3>${item.name}</h3>
            <p>${item.description}</p>
            ${item.damage ? `<p>Damage: ${item.damage}</p>` : ''}
            ${item.range ? `<p>Range: ${item.range}</p>` : ''}
            ${item.level ? `<p>Level: ${item.level}</p>` : ''}
            ${item.hp ? `<p>HP: ${item.hp}</p>` : ''}
            ${item.attack ? `<p>Attack: ${item.attack}</p>` : ''}
            ${item.defense ? `<p>Defense: ${item.defense}</p>` : ''}
        `;
        content.appendChild(itemDiv);
    });
    
    modal.classList.add('active');
}

function showLevelUpModal(newLevel) {
    const modal = document.getElementById('level-up-modal');
    const okBtn = document.getElementById('level-up-ok');
    document.getElementById('new-level').textContent = newLevel;
    modal.classList.add('active');
    
    // Remove old listener
    const newOkBtn = okBtn.cloneNode(true);
    okBtn.parentNode.replaceChild(newOkBtn, okBtn);
    
    const closeModal = () => {
        modal.classList.remove('active');
        document.removeEventListener('keydown', keyHandler);
    };
    
    newOkBtn.onclick = closeModal;
    
    // Keyboard shortcut: E or Enter to continue
    const keyHandler = (e) => {
        const key = e.key.toLowerCase();
        if (key === 'e' || key === 'enter' || key === 'escape') {
            e.preventDefault();
            closeModal();
        }
    };
    document.addEventListener('keydown', keyHandler);
}

function upgradeSkill(skillName) {
    socket.emit('upgrade_skill', { skill: skillName });
}

function equipItem(index) {
    const item = inventory[index];
    socket.emit('equip_item', { item });
}

function pickupLoot(lootId) {
    socket.emit('pickup_loot', { loot_id: lootId });
}

function discardInventoryItem(index) {
    const item = inventory[index];
    showConfirmation(
        'Discard Item',
        `Discard ${item.name}? This action cannot be undone.`,
        () => {
            // Send discard request to server
            socket.emit('discard_inventory_item', { item_index: index });
        }
    );
}

function discardLoot(lootId) {
    showConfirmation(
        'Discard Loot',
        'Discard this loot? This action cannot be undone.',
        () => {
            socket.emit('discard_loot', { loot_id: lootId });
        }
    );
}

document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', function() {
        const modal = this.closest('.modal');
        if (modal) {
            closeModal(modal.id);
        }
    });
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});
