// Canvas setup
const canvas = document.getElementById('dungeon-canvas');
const ctx = canvas ? canvas.getContext('2d') : null;
const minimapCanvas = document.getElementById('minimap-canvas');
const minimapCtx = minimapCanvas ? minimapCanvas.getContext('2d') : null;
const TILE_SIZE = 32;
const VIEWPORT_WIDTH = 25;
const VIEWPORT_HEIGHT = 18;
const LOOT_RANGE = 5;

// Movement interpolation - linear speed in tiles per second
// Server updates every 50ms (20 times per second)
// Visual speed set to 20 tiles/sec to match server update rate
const MOVE_SPEED = 20.0; // Tiles per second - matches server rate

// Game state management
let player = null;
let dungeon = null;
let entities = null;
let enemies = {};
let otherPlayers = {};
let inventory = [];
let lootDrops = {};
let animations = [];
let debugMode = false;

// Player visual position (for smooth movement)
let playerVisualX = 0;
let playerVisualY = 0;

// Modal state
let activeModal = null;
let selectedIndex = 0;

// Sprite renderer
let spriteRenderer = null;

// Sprite loading
const sprites = {
    playerIdle: null,
    playerWalk: null,
    playerPierceDown: null,
    playerPierceSide: null,
    playerPierceUp: null,
    dungeonTiles: null,
    dungeonProps: null,
    enemySkeleton: null,
    enemyOrc: null,
    enemySkeletonDeath: null,
    enemyOrcDeath: null,
    loaded: false
};

let spritesLoaded = 0;
const totalSprites = 11;

function checkSpritesLoaded() {
    spritesLoaded++;
    if (spritesLoaded === totalSprites) {
        sprites.loaded = true;
        console.log('All sprites loaded');
    }
}

// Initialize sprite renderer
spriteRenderer = new SpriteRenderer();

// Load sprites
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

sprites.dungeonTiles = new Image();
sprites.dungeonTiles.onload = () => checkSpritesLoaded();
sprites.dungeonTiles.onerror = () => checkSpritesLoaded();
sprites.dungeonTiles.src = '/static/images/dungeon-tiles.png';

sprites.dungeonProps = new Image();
sprites.dungeonProps.onload = () => checkSpritesLoaded();
sprites.dungeonProps.onerror = () => checkSpritesLoaded();
sprites.dungeonProps.src = '/static/images/dungeon-props.png';

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
