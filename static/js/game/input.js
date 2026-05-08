// Input handling
function setupInputHandlers() {
    document.addEventListener('keydown', (e) => {
        if (!player) return;
        
        const key = e.key.toLowerCase();
        
        // Handle modal navigation
        if (activeModal) {
            if (key === 'escape') {
                e.preventDefault();
                closeModal(activeModal);
                return;
            }
            
            if (key === 'w' || key === 'arrowup') {
                e.preventDefault();
                navigateModal(-1);
                return;
            }
            
            if (key === 's' || key === 'arrowdown') {
                e.preventDefault();
                navigateModal(1);
                return;
            }
            
            if (key === 'e' || key === 'enter') {
                e.preventDefault();
                selectModalItem();
                return;
            }
            
            return;
        }
        
        // Movement
        if (key === 'w' || key === 'arrowup') {
            e.preventDefault();
            socket.emit('move', { direction: 'up' });
        } else if (key === 's' || key === 'arrowdown') {
            e.preventDefault();
            socket.emit('move', { direction: 'down' });
        } else if (key === 'a' || key === 'arrowleft') {
            e.preventDefault();
            socket.emit('move', { direction: 'left' });
        } else if (key === 'd' || key === 'arrowright') {
            e.preventDefault();
            socket.emit('move', { direction: 'right' });
        }
        
        // Combat
        else if (key === 'p') {
            e.preventDefault();
            attackClosestEnemy();
        }
        
        // UI
        else if (key === 'l') {
            e.preventDefault();
            showSkillsModal();
        } else if (key === 'i') {
            e.preventDefault();
            showInventoryModal();
        } else if (key === 'f') {
            e.preventDefault();
            showAreaLootModal();
        }
        
        // Debug
        else if (key === 'f1') {
            e.preventDefault();
            debugMode = !debugMode;
            renderDungeon();
        }
    });
}

function attackClosestEnemy() {
    if (!player || !enemies) return;
    
    let closestEnemy = null;
    let closestDistance = Infinity;
    
    for (const [enemyId, enemy] of Object.entries(enemies)) {
        const distance = Math.max(
            Math.abs(player.x - enemy.x),
            Math.abs(player.y - enemy.y)
        );
        
        if (distance < closestDistance) {
            closestDistance = distance;
            closestEnemy = enemyId;
        }
    }
    
    if (closestEnemy) {
        socket.emit('attack_enemy', { enemy_id: closestEnemy });
    } else {
        addLog('No enemies nearby!', 'info');
    }
}
