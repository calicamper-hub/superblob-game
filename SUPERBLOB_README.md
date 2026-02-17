# Super Blob - Pygame Slingshot Game

**Created by Emma Wilkinson**

## 📝 Game Description
Super Blob is a physics-based slingshot game where you rescue mini blobs by destroying buildings. Features multiple characters, upgrades, two unique worlds, and comic book-style storytelling.

## 🎮 Game Features

### Characters (5 Total)
1. **SUPERBLOB** (Free) - Balanced hero with orange cape and "SB" logo
2. **ALEX** (20 blobs) - Super bouncy with black spiky hair
3. **LUCY** (25 blobs) - Efficient power drain with long blonde hair
4. **EVIL MOB** (35 blobs) - Can smash through buildings with green mask
5. **RICHARD** (50 blobs) - Magnetic pull with gray skin, orange curly hair, and glasses

### Worlds
- **CITY**: Buildings and skyscrapers, golden boss building, gate obstacle at level 10+
- **VILLAGE**: Houses with red roofs, countryside setting, moving gas clouds (2-4 depending on level)

### Upgrade System
- **Character Upgrades** (2x character cost)
  - Alex: Even bouncier (0.95 bounce)
  - Lucy: Super efficient (0.15 power drain)
  - Evil Mob: Smash bosses 30% faster
  - Richard: Stronger magnet (7.5 pull strength)

- **Mini Blob Count Upgrades**
  - Base: 6 mini blobs
  - Upgrade 1 (150): 7 mini blobs
  - Upgrade 2 (300): 8 mini blobs
  - Upgrade 3 (600): 9 mini blobs
  - Upgrade 4 (1200): 10 mini blobs

### Game Mechanics
- **Size Growth**: Character grows every 5 mini blobs collected (resets per level)
- **Power System**:
  - Base: 100 power
  - +10 max power per 10 blobs collected in run
  - Village bonus: +10 max power per 7 blobs collected in level
- **Boss Requirements**:
  - City: level × 10 power (10, 20, 30...)
  - Village: level × 15 power (15, 30, 45...)
- **Fail State**: Running out of power restarts from level 1

### Village Features
- Gas clouds that drain 20 power on contact
- Progressive difficulty: 2 clouds (levels 1-4), 3 clouds (5-7), 4 clouds (8+)
- Taller houses (220-280 height)
- No gate obstacle
- Unique village-themed comics (8 variants)

## 📋 File Information
- **Filename**: `superblob_game.py`
- **Size**: ~128KB (~2,600 lines of code)
- **Dependencies**: pygame, math, random
- **Created**: 2024
- **Last Updated**: February 16, 2026

## 🎯 How to Play
1. Run: `python superblob_game.py`
2. Drag blob to aim, release to launch
3. Collect gray mini-blobs to gain power
4. Destroy buildings - save power for GOLD boss!
5. Click mid-flight to catch and re-launch
6. Unlock characters and buy upgrades with rescued blobs

## 🐛 Known Issues (From Code Audit)
### Critical
- Missing global declarations in some functions (retry_level, reset_game)
- max_power calculation inconsistency for village retries

### Important
- Many magic numbers should be constants
- Main game loop is 1,677 lines (needs refactoring)
- Duplicate code in character/building drawing

### Minor
- Confusing color variable names (BLUE/RED/GREEN are actually gray)
- Performance: Background gradient redrawn every frame

## 💾 Backup Strategy
1. Keep dated backups: `superblob_game_backup_YYYYMMDD.py`
2. Consider using Git for version control
3. Store in cloud storage (Dropbox, Google Drive, iCloud)

## 🎨 Graphics Style
- Comic book panels between levels
- Clean character designs with capes/hair
- Detailed buildings with windows
- Village countryside with trees and flowers
- Professional UI with rounded buttons

## 📊 Game Balance
- Character costs: 0, 20, 25, 35, 50
- Upgrade costs: 40, 50, 70, 100 (2x character cost)
- Mini blob upgrades: 150, 300, 600, 1200 (exponential)
- Village ~50% harder than city (boss power requirements)

## 🏆 Progression
1. Start with Super Blob in City
2. Collect mini blobs to unlock characters
3. Beat City level 12 to unlock Village
4. Purchase upgrades to enhance abilities
5. Increase mini blob count for more power

---

**Game Stats:**
- 2 Worlds
- 5 Characters
- 9 Upgrade Options
- 16 Comic Variants (8 per world)
- Infinite levels with scaling difficulty

**Enjoy the game!** 🎮✨
