# 🗡️ Dungeon Crawler - Multiplayer RPG

A real-time multiplayer dungeon crawler with procedurally generated maps, RPG progression, and epic lore.

## 🎮 Features

### Core Gameplay
- **Procedurally Generated Dungeons** - Every floor is unique using BSP-inspired algorithms
- **Real-time Multiplayer** - Play with others via WebSockets
- **RPG Leveling System** - Gain XP, level up, and increase stats
- **Skills System** - 6 unique skills with multiple upgrade levels
- **Level-Based Gear** - Equipment with level requirements and rarity tiers

### Special Features
- **15 Legendary Weapons** - Each with unique lore and special properties
- **12 Epic Bosses** - Rare bosses with backstories that drop legendary items
- **Infinite Replayability** - Procedural generation with seeded dungeons
- **Boss Floors** - Special boss encounters every 5 floors

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: Vanilla JavaScript, HTML5 Canvas
- **Real-time**: WebSockets (Socket.IO)
- **Deployment**: Render-ready with render.yaml

## 🚀 Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

3. Open browser to `http://localhost:5000`

## 🌐 Deploy to Render

1. Push this code to a Git repository
2. Connect your repo to Render
3. Render will automatically detect `render.yaml`
4. Deploy!

## 🎯 How to Play

- **WASD or Arrow Keys** - Move your character
- **Click on enemies** - Attack (must be adjacent)
- **Reach the stairs** - Descend to the next floor
- **Level up** - Gain skill points to upgrade abilities
- **Collect loot** - Find weapons and armor from defeated enemies

## 📊 Game Systems

### Stats
- **Strength** - Increases physical damage
- **Dexterity** - Improves dodge chance
- **Intelligence** - Boosts magic damage
- **Vitality** - Increases max HP and defense

### Skills
- **Power Strike** - +5 damage per level
- **Quick Reflexes** - +3% dodge per level
- **Arcane Knowledge** - +5 magic damage per level
- **Iron Skin** - +3 defense per level
- **Critical Eye** - +5% crit chance per level
- **Life Drain** - +10% lifesteal per level

### Rarity Tiers
- Common (70% drop rate)
- Uncommon (25% drop rate)
- Rare (5% drop rate)
- Legendary (Boss drops only)

## 🏆 Legendary Weapons

Discover 15 unique legendary weapons, including:
- **Shadowfang** - Dagger of the Nightblade Cult
- **Stormbringer** - Sword crackling with eternal lightning
- **Frostmourne** - The Lich King's cursed blade
- **Eternity** - The First Blade, forged at the dawn of time
- And many more...

## 👹 Epic Bosses

Face 12 legendary bosses with rich lore:
- **The Shadow King** - Ruler of an empire of shadows
- **Volthar the Storm Titan** - Born from the first thunderstorm
- **Kel'Thuzad the Eternal** - The immortal lich
- **Thanatos the Reaper** - Death itself given form
- And more...

## 📝 License

MIT License - Feel free to use and modify!

## 🎨 Credits

Created with ❤️ for dungeon crawling enthusiasts everywhere.
