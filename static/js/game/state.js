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

// Modal state
let activeModal = null;
let selectedIndex = 0;

// Sprite loading
const sprites = {
    playerIdle: null,
    playerRun: null,
    dungeonTiles: null,
    dungeonProps: null,
    enemies: null
};

let spritesLoaded = 0;
const totalSprites = 5;

function checkSpritesLoaded() {
    spritesLoaded++;
    if (spritesLoaded === totalSprites) {
        console.log('All sprites loaded');
    }
}

// Load sprites
sprites.playerIdle = new Image();
sprites.playerIdle.onload = () => checkSpritesLoaded();
sprites.playerIdle.src = '/static/images/player-idle.png';

sprites.playerRun = new Image();
sprites.playerRun.onload = () => checkSpritesLoaded();
sprites.playerRun.src = '/static/images/player-run.png';

sprites.dungeonTiles = new Image();
sprites.dungeonTiles.onload = () => checkSpritesLoaded();
sprites.dungeonTiles.src = '/static/images/dungeon-tiles.png';

sprites.dungeonProps = new Image();
sprites.dungeonProps.onload = () => checkSpritesLoaded();
sprites.dungeonProps.src = '/static/images/dungeon-props.png';

sprites.enemies = new Image();
sprites.enemies.onload = () => checkSpritesLoaded();
sprites.enemies.src = '/static/images/enemies.png';
