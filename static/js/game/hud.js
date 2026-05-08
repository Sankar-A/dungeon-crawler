// HUD management
function updateHUD() {
    if (!player) return;
    
    document.getElementById('player-name').textContent = player.name;
    document.getElementById('player-level').textContent = player.level;
    document.getElementById('current-floor').textContent = player.floor;
    document.getElementById('player-gold').textContent = player.gold;
    
    document.getElementById('player-hp').textContent = player.hp;
    document.getElementById('player-max-hp').textContent = player.max_hp;
    document.getElementById('player-xp').textContent = player.xp;
    document.getElementById('player-xp-next').textContent = player.level * 100;
    
    const hpPercent = (player.hp / player.max_hp) * 100;
    document.getElementById('hp-bar').style.width = hpPercent + '%';
    
    const xpPercent = (player.xp / (player.level * 100)) * 100;
    document.getElementById('xp-bar').style.width = xpPercent + '%';
    
    const str = 10 + (player.skills.strength || 0) * 2;
    const dex = 10 + (player.skills.dexterity || 0) * 2;
    const int = 10 + (player.skills.intelligence || 0) * 2;
    const vit = 10 + (player.skills.vitality || 0) * 2;
    
    document.getElementById('player-str').textContent = str;
    document.getElementById('player-dex').textContent = dex;
    document.getElementById('player-int').textContent = int;
    document.getElementById('player-vit').textContent = vit;
    
    document.getElementById('skill-points').textContent = player.skill_points;
}

function addLog(message, type = 'info') {
    const logMessages = document.getElementById('log-messages');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = message;
    logMessages.appendChild(logEntry);
    logMessages.scrollTop = logMessages.scrollHeight;
    
    if (logMessages.children.length > 50) {
        logMessages.removeChild(logMessages.firstChild);
    }
}
