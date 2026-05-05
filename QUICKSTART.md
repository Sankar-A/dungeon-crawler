# ⚡ Quick Start Guide

## 🎯 Get Playing in 3 Minutes

### Option 1: Local Play (Fastest)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python app.py

# 3. Open your browser
# Go to: http://localhost:5000
```

That's it! You're playing!

### Option 2: Deploy to Render (Share with Friends)

```bash
# 1. Create a GitHub repo and push code
git init
git add .
git commit -m "Dungeon Crawler RPG"
git remote add origin <your-repo-url>
git push -u origin main

# 2. Go to render.com
# - Sign up/login
# - Click "New +" → "Web Service"
# - Connect your GitHub repo
# - Click "Create Web Service"

# 3. Wait 2-3 minutes for deployment
# Share the URL with friends!
```

## 🎮 How to Play

### Controls
- **W/↑** - Move Up
- **S/↓** - Move Down
- **A/←** - Move Left
- **D/→** - Move Right
- **Click Enemy** - Attack (must be adjacent)

### Objectives
1. **Explore** the procedurally generated dungeon
2. **Fight** enemies to gain XP and level up
3. **Collect** loot and legendary weapons
4. **Reach** the stairs to descend deeper
5. **Defeat** epic bosses every 5 floors
6. **Survive** as long as you can!

### Tips for Beginners
- 🗡️ **Upgrade skills** when you level up
- ❤️ **HP fully restores** when you descend floors
- 👹 **Bosses appear** every 5 floors (10, 15, 20...)
- 🎁 **Legendary weapons** drop from bosses
- 📊 **Check your stats** regularly in the HUD
- 🛡️ **Equip better gear** as you find it

### Skill Recommendations

**For Beginners:**
1. Iron Skin (survive longer)
2. Power Strike (kill faster)
3. Life Drain (sustain in combat)

**For Advanced:**
1. Critical Eye (massive damage)
2. Quick Reflexes (avoid damage)
3. Power Strike (maximize crits)

## 🏆 Goals

### Short Term
- [ ] Reach floor 5
- [ ] Defeat your first boss
- [ ] Obtain a legendary weapon
- [ ] Reach level 10

### Medium Term
- [ ] Reach floor 20
- [ ] Defeat 3 different bosses
- [ ] Collect 5 legendary weapons
- [ ] Max out a skill tree

### Long Term
- [ ] Reach floor 50
- [ ] Defeat all 12 bosses
- [ ] Collect all 15 legendary weapons
- [ ] Reach level 50

## 🐛 Troubleshooting

### Server won't start
```bash
# Make sure Python 3.11+ is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't connect to game
- Check that server is running on port 5000
- Try accessing `http://127.0.0.1:5000` instead
- Disable browser extensions that block WebSockets
- Check firewall settings

### Game is laggy
- Close other browser tabs
- Reduce browser zoom to 100%
- Try a different browser (Chrome recommended)
- Check your internet connection

## 📚 Learn More

- **Full Features**: See `FEATURES.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Game Mechanics**: See `README.md`

## 🎉 Have Fun!

This is a complete, playable multiplayer dungeon crawler. Enjoy exploring, fighting, and collecting legendary loot!

**Pro Tip**: The game gets harder the deeper you go. Don't rush - take time to level up and upgrade your skills!
