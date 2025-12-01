# Isometric Tower Defense

Isometric Tower Defense is a strategic simulation game built entirely in Python using the Pygame library. The project focuses on implementing a custom 2.5D isometric rendering engine and optimizing entity management using spatial partitioning for high-performance gameplay.

---

## 📌 Key Features

- **Isometric 2.5D Rendering**: Custom projection engine converting 3D coordinates to 2D screen space with proper depth sorting.  
- **Spatial Partitioning**: Implemented a Spatial Grid system to optimize collision detection and range queries (reducing complexity from O(N²) to near O(1)).  
- **Finite State Machine (FSM)**: Entities (Soldiers, Zombies) utilize FSMs for complex behaviors like idling, tracking, attacking, and dying.  
- **Dynamic Building System**: Place various tower types with unique stats and shield mechanics.  
- **Interactive Camera**: Smooth camera panning (WASD) and zoom controls.

---

## 📁 Directory Structure

Isometric_Tower_Defense/
│
├── main.py
│   • Main entry point for the game.
│   • Handles the game loop, input events (keyboard/mouse), and game states (Round Win/Game Over).
│
├── Renderer.py
│   • Core rendering engine.
│   • Handles Isometric Projection logic, Z-buffering (depth sorting), and UI drawing.
│
├── Spatial.py
│   • Spatial Grid implementation.
│   • Divides the map into cells to optimize performance for collision and targeting.
│
├── AIManager.py
│   • Central brain for game logic.
│   • Calculates targeting logic: Towers finding enemies, Enemies finding soldiers.
│
├── config.py
│   • Global configuration file.
│   • Stores constants: Screen size, Colors, FPS, and balance settings.
│
├── Audio.py
│   • Audio Manager class.
│   • Handles background music playlists and sound effects (priority management).
│
├── Entities/
│   ├── Enemy.py: Zombie logic, animation states, and path tracking.
│   ├── Soldier.py: Defender logic, shooting mechanics, and rotation.
│   └── Tower.py: Structure logic, cooldown management, and shield systems.
│
└── res/
    ├── castle/: Sprites for player bases and towers.
    ├── Zombie/: Animation frames for enemies.
    ├── Soldier/: Animation frames for defenders.
    └── shield_dome_iso.png: Texture for shield effects.

---

## 🚀 Installation & Usage

### 🐍 Requirements
- Python 3.8+
- Pygame

### Installation
```bash
pip install pygame
```

### Run
```bash
python3 main.py
```

---

### **Phần 5: Controls**

```markdown
## 🎮 Controls

- **W, A, S, D**: Pan Camera  
- **1 - 6**: Select Tower Type  
- **Left Click**: Place Tower  
- **Space**: Start Round / Restart Game
```
