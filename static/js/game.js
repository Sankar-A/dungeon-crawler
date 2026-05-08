// Main game initialization
const socket = io();

// Initialize game
function initGame() {
    setupAuthSocketHandlers();
    setupSocketHandlers();
    setupInputHandlers();
    initAuth();
    
    document.getElementById('view-weapons-btn').addEventListener('click', () => {
        socket.emit('get_rare_weapons');
    });
    
    document.getElementById('view-bosses-btn').addEventListener('click', () => {
        socket.emit('get_rare_bosses');
    });
}

// Start game when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGame);
} else {
    initGame();
}
