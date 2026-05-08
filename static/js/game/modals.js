// Modal management
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        activeModal = null;
        selectedIndex = 0;
    }
}

function navigateModal(direction) {
    if (!activeModal) return;
    
    let items = document.querySelectorAll(`.${activeModal}-item`);
    if (items.length === 0) return;
    
    items[selectedIndex].classList.remove('selected');
    
    selectedIndex += direction;
    if (selectedIndex < 0) selectedIndex = items.length - 1;
    if (selectedIndex >= items.length) selectedIndex = 0;
    
    items[selectedIndex].classList.add('selected');
    items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

function selectModalItem() {
    if (!activeModal) return;
    
    let items = document.querySelectorAll(`.${activeModal}-item`);
    if (items.length === 0 || selectedIndex >= items.length) return;
    
    items[selectedIndex].click();
}

function showSkillsModal() {
    if (!player) return;
    
    const modal = document.getElementById('skills-modal');
    const list = document.getElementById('skills-list');
    const pointsSpan = document.getElementById('modal-skill-points');
    
    list.innerHTML = '';
    pointsSpan.textContent = player.skill_points;
    
    const skills = ['strength', 'dexterity', 'intelligence', 'vitality'];
    
    skills.forEach((skill, index) => {
        const level = player.skills[skill] || 0;
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skills-item skill-item';
        if (index === 0) skillDiv.classList.add('selected');
        
        skillDiv.innerHTML = `
            <span>${skill.charAt(0).toUpperCase() + skill.slice(1)}: ${level}</span>
            <button onclick="upgradeSkill('${skill}')" ${player.skill_points === 0 ? 'disabled' : ''}>
                Upgrade (+1)
            </button>
        `;
        
        list.appendChild(skillDiv);
    });
    
    activeModal = 'skills';
    selectedIndex = 0;
    modal.style.display = 'block';
}

function showInventoryModal() {
    if (!player) return;
    
    const modal = document.getElementById('inventory-modal');
    const equipped = document.getElementById('equipped-items');
    const items = document.getElementById('inventory-items');
    
    equipped.innerHTML = '<h3>Equipped</h3>';
    items.innerHTML = '<h3>Inventory</h3>';
    
    if (player.weapon) {
        const weaponDiv = document.createElement('div');
        weaponDiv.className = 'inventory-item';
        weaponDiv.innerHTML = `
            <strong>${player.weapon.name}</strong>
            <div>Damage: ${player.weapon.damage}</div>
            ${player.weapon.range > 1 ? `<div>Range: ${player.weapon.range}</div>` : ''}
        `;
        equipped.appendChild(weaponDiv);
    }
    
    if (player.armor) {
        const armorDiv = document.createElement('div');
        armorDiv.className = 'inventory-item';
        armorDiv.innerHTML = `
            <strong>${player.armor.name}</strong>
            <div>Defense: ${player.armor.defense}</div>
        `;
        equipped.appendChild(armorDiv);
    }
    
    if (inventory.length === 0) {
        items.innerHTML += '<p>No items in inventory</p>';
    } else {
        inventory.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'inventory-item';
            itemDiv.innerHTML = `
                <strong>${item.name}</strong>
                <div>${item.type === 'weapon' ? `Damage: ${item.damage}` : `Defense: ${item.defense}`}</div>
                <button onclick="equipItem(${index})">Equip</button>
                <button onclick="discardInventoryItem(${index})">Discard</button>
            `;
            items.appendChild(itemDiv);
        });
    }
    
    modal.style.display = 'block';
}

function showAreaLootModal() {
    if (!player) return;
    
    const modal = document.getElementById('loot-modal');
    const list = document.getElementById('loot-list');
    
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
        nearbyLoot.forEach((loot, index) => {
            const lootDiv = document.createElement('div');
            lootDiv.className = 'loot-item';
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
    }
    
    modal.style.display = 'block';
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
    
    modal.style.display = 'block';
}

function showLevelUpModal(newLevel) {
    const modal = document.getElementById('level-up-modal');
    document.getElementById('new-level').textContent = newLevel;
    modal.style.display = 'block';
    
    document.getElementById('level-up-ok').onclick = () => {
        modal.style.display = 'none';
    };
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
            inventory.splice(index, 1);
            addLog(`Discarded ${item.name}`, 'loot');
            showInventoryModal();
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
