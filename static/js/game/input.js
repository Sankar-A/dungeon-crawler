// Input handling
let lastMoveTime = 0;
let lastAttackTime = 0;
const MOVE_INTERVAL = 50; // Send move commands every 50ms for smooth movement
const ATTACK_COOLDOWN = 800; // ms between attacks

let keysPressed = {}; // Track which keys are currently held down
let moveInterval = null;
let attackInterval = null;
let currentDirection = null; // Track current movement direction

function setupInputHandlers() {
    document.addEventListener('keydown', (e) => {
        if (!player) return;
        
        const key = e.key.toLowerCase();
        
        // Prevent repeat events when key is held
        if (keysPressed[key]) return;
        keysPressed[key] = true;
        
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
                selectModalItemPositive();
                return;
            }
            
            if (key === 'x') {
                e.preventDefault();
                selectModalItemNegative();
                return;
            }
            
            return;
        }
        
        // Movement - start continuous movement
        if (key === 'w' || key === 'arrowup') {
            e.preventDefault();
            handleMove('up');
            if (!moveInterval) {
                moveInterval = setInterval(() => {
                    handleMove('up');
                }, MOVE_INTERVAL);
            }
        } else if (key === 's' || key === 'arrowdown') {
            e.preventDefault();
            handleMove('down');
            if (!moveInterval) {
                moveInterval = setInterval(() => {
                    handleMove('down');
                }, MOVE_INTERVAL);
            }
        } else if (key === 'a' || key === 'arrowleft') {
            e.preventDefault();
            handleMove('left');
            if (!moveInterval) {
                moveInterval = setInterval(() => {
                    handleMove('left');
                }, MOVE_INTERVAL);
            }
        } else if (key === 'd' || key === 'arrowright') {
            e.preventDefault();
            handleMove('right');
            if (!moveInterval) {
                moveInterval = setInterval(() => {
                    handleMove('right');
                }, MOVE_INTERVAL);
            }
        }
        
        // Combat - start continuous attacking
        else if (key === 'p') {
            e.preventDefault();
            const currentTime = Date.now();
            if (currentTime - lastAttackTime >= ATTACK_COOLDOWN) {
                attackClosestEnemy();
                lastAttackTime = currentTime;
            }
            if (!attackInterval) {
                attackInterval = setInterval(() => {
                    const now = Date.now();
                    if (now - lastAttackTime >= ATTACK_COOLDOWN) {
                        attackClosestEnemy();
                        lastAttackTime = now;
                    }
                }, ATTACK_COOLDOWN);
            }
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
    
    document.addEventListener('keyup', (e) => {
        const key = e.key.toLowerCase();
        keysPressed[key] = false;
        
        // Stop movement when any movement key is released
        if (['w', 's', 'a', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(key)) {
            // Check if any movement key is still pressed
            const stillMoving = ['w', 's', 'a', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright']
                .some(k => keysPressed[k]);
            
            if (!stillMoving) {
                stopWalking();
                if (moveInterval) {
                    clearInterval(moveInterval);
                    moveInterval = null;
                }
            }
        }
        
        // Stop attacking when P is released
        if (key === 'p') {
            if (attackInterval) {
                clearInterval(attackInterval);
                attackInterval = null;
            }
        }
    });
}

function handleMove(direction) {
    if (!player || activeModal) return;
    
    // Check which direction key is currently pressed
    const directionKeys = {
        'up': ['w', 'arrowup'],
        'down': ['s', 'arrowdown'],
        'left': ['a', 'arrowleft'],
        'right': ['d', 'arrowright']
    };
    
    // Only move if the corresponding key is still pressed
    if (!directionKeys[direction].some(k => keysPressed[k])) {
        return;
    }
    
    startWalking();
    socket.emit('move', { direction });
}

function startWalking() {
    isWalking = true;
}

function stopWalking() {
    isWalking = false;
    walkFrameIndex = 0;
    
    // Snap visual position to actual position when stopping
    if (player) {
        playerVisualX = player.x;
        playerVisualY = player.y;
    }
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
