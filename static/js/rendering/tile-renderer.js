// Tile rendering functions

function renderTiles(ctx, dungeon, viewport, sprites) {
    for (let y = 0; y < VIEWPORT_HEIGHT; y++) {
        for (let x = 0; x < VIEWPORT_WIDTH; x++) {
            const worldX = viewport.startX + x;
            const worldY = viewport.startY + y;
            
            if (worldX >= 0 && worldX < dungeon[0].length && 
                worldY >= 0 && worldY < dungeon.length) {
                
                const tile = dungeon[worldY][worldX];
                renderSingleTile(ctx, x, y, worldX, worldY, tile, sprites);
            } else {
                // Draw black for out of bounds
                ctx.fillStyle = '#000';
                ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }
        }
    }
}

function renderSingleTile(ctx, screenX, screenY, worldX, worldY, tile, sprites) {
    if (sprites.loaded && sprites.dungeonTiles && sprites.dungeonTiles.complete) {
        if (tile === 0) {
            renderFloorTile(ctx, screenX, screenY, worldX, worldY, sprites);
        } else {
            renderWallTile(ctx, screenX, screenY, worldX, worldY, sprites);
        }
    } else {
        // Fallback to colored tiles
        ctx.fillStyle = tile === 0 ? '#4a4a4a' : '#1a1a1a';
        ctx.fillRect(screenX * TILE_SIZE, screenY * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
}

function renderFloorTile(ctx, screenX, screenY, worldX, worldY, sprites) {
    const floorVariants = [
        [0, 0],   // Basic stone floor
        [16, 0],  // Variant 1
        [32, 0],  // Variant 2
        [48, 0],  // Variant 3
    ];
    const variantIndex = ((worldX + worldY) % floorVariants.length);
    const [tileX, tileY] = floorVariants[variantIndex];
    
    ctx.drawImage(
        sprites.dungeonTiles,
        tileX, tileY, 16, 16,
        screenX * TILE_SIZE, screenY * TILE_SIZE, TILE_SIZE, TILE_SIZE
    );
}

function renderWallTile(ctx, screenX, screenY, worldX, worldY, sprites) {
    const wallVariants = [
        [0, 80],   // Basic wall (row 5)
        [16, 80],  // Variant 1
        [32, 80],  // Variant 2
        [0, 96],   // Variant 3 (row 6)
    ];
    const variantIndex = ((worldX * 2 + worldY) % wallVariants.length);
    const [tileX, tileY] = wallVariants[variantIndex];
    
    ctx.drawImage(
        sprites.dungeonTiles,
        tileX, tileY, 16, 16,
        screenX * TILE_SIZE, screenY * TILE_SIZE, TILE_SIZE, TILE_SIZE
    );
}
