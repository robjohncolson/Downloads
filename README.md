# Platformer Game with JSON Level System

This platformer game now supports external JSON level files and includes a powerful level editor!

## 🎮 Running the Game

```bash
python3 "pygame_smartboard_starter (1).py"
```

The game will automatically scan the `levels/` directory for JSON level files and load them dynamically.

## 🛠️ Level Editor

### Running the Editor
```bash
python3 level_editor.py
```

### Editor Controls

#### Mode Selection (Number Keys)
- **1**: Platform mode - Click and drag to create platforms
- **2**: Coin mode - Click to place coins
- **3**: Spike mode - Click and drag to create spikes  
- **4**: Goal mode - Click to place the level goal/flag
- **5**: Spawn mode - Click to set player spawn positions

#### File Operations
- **Ctrl+S**: Save current level
- **Ctrl+L**: Load level (loads world{world}_level{level}.json)
- **Ctrl+N**: Create new empty level

#### Editing
- **Left Click**: Place/draw objects
- **Right Click** or **Delete**: Remove objects at cursor
- **Tab**: Switch between Player 1 and Player 2 spawn points (in spawn mode)

#### View Options
- **G**: Toggle grid on/off
- **B**: Toggle background between day/night

#### Navigation
- **ESC**: Exit editor

### Editor Interface
- Top bar shows current mode and level information
- Current mode is highlighted in white
- Instructions are displayed at the bottom
- Grid snapping helps with precise placement

## 📁 Level File Format

Levels are stored as JSON files in the `levels/` directory with the naming convention:
`world{X}_level{Y}.json`

### Example Level Structure
```json
{
  "world": 1,
  "level": 1,
  "name": "Getting Started",
  "background_type": "day",
  "platforms": [
    {
      "x": 0,
      "y": 680,
      "width": 1280,
      "height": 40,
      "color": [139, 69, 19]
    }
  ],
  "coins": [
    {
      "x": 250,
      "y": 540
    }
  ],
  "spikes": [
    {
      "x": 400,
      "y": 665,
      "width": 100,
      "height": 15
    }
  ],
  "goal": {
    "x": 1180,
    "y": 640,
    "is_door": false
  },
  "player_spawns": [
    {
      "x": 100,
      "y": 640
    },
    {
      "x": 150,
      "y": 640
    }
  ]
}
```

### Field Descriptions

#### Level Metadata
- `world`: World number (integer)
- `level`: Level number within world (integer)  
- `name`: Display name for the level (string)
- `background_type`: "day" or "night" (affects background and stars)

#### Game Objects
- `platforms`: Array of platform objects with x, y, width, height, and color
- `coins`: Array of coin positions with x, y coordinates
- `spikes`: Array of spike objects with x, y, width, height
- `goal`: Single goal object with x, y coordinates and is_door flag
- `player_spawns`: Array of exactly 2 spawn points for Player 1 and Player 2

## 🎯 Creating Custom Levels

### Method 1: Using the Level Editor (Recommended)
1. Run `python3 level_editor.py`
2. Use the number keys to switch between modes
3. Click and drag to create platforms and spikes
4. Click to place coins, goals, and spawn points
5. Press Ctrl+S to save your level

### Method 2: Manual JSON Creation
1. Create a new JSON file in the `levels/` directory
2. Follow the naming convention: `world{X}_level{Y}.json`
3. Use the example structure above as a template
4. Ensure all required fields are present

## 🔧 Game Features

### Enhanced Level System
- **Dynamic Level Loading**: Game automatically discovers and loads JSON levels
- **Flexible Level Organization**: Organize levels by world and level number
- **Custom Backgrounds**: Choose between day and night themes
- **Custom Colors**: Set custom colors for platforms
- **Precise Positioning**: Pixel-perfect placement of all game elements

### Level Editor Features
- **Visual Editing**: See exactly how your level will look in-game
- **Grid Snapping**: Automatic alignment to 20-pixel grid
- **Real-time Preview**: Objects appear as you place them
- **Easy Deletion**: Right-click or Delete key to remove objects
- **Background Preview**: Toggle between day/night to see how it looks
- **Spawn Point Management**: Easily set both player starting positions

## 🎮 Game Controls (Unchanged)
- **Player 1**: WASD to move and jump
- **Player 2**: Arrow keys to move and jump
- **R**: Restart current level
- **N**: Next level (when completed)
- **1, 2, 3**: Quick switch to levels 1, 2, 3
- **ESC**: Exit game

## 📂 File Structure
```
├── pygame_smartboard_starter (1).py  # Main game file
├── level_editor.py                   # Level editor
├── levels/                          # Level files directory
│   ├── world1_level1.json
│   ├── world1_level2.json
│   ├── world2_level1.json
│   └── ...
├── level_format.json               # Example level format
└── README.md                       # This file
```

## 🚀 Getting Started

1. **Play existing levels**: Run the main game to try the included levels
2. **Create your first level**: Use the level editor to design a simple level
3. **Test your creation**: Save and then play your level in the main game
4. **Share levels**: JSON files can be easily shared with other players

## 💡 Tips for Level Design

### Good Level Design Principles
- **Progressive Difficulty**: Start easy, gradually increase challenge
- **Clear Path**: Players should understand where to go
- **Fair Challenges**: Difficult sections should be achievable with practice
- **Coin Placement**: Use coins to guide players along the intended path
- **Safe Zones**: Provide rest areas between challenging sections

### Technical Tips
- **Platform Spacing**: Leave enough room for players to jump between platforms
- **Spike Placement**: Don't make spikes unavoidable - always provide a safe path
- **Goal Accessibility**: Ensure the goal is reachable when all coins are collected
- **Spawn Safety**: Place spawn points away from immediate dangers
- **Wall Boundaries**: Include walls (thin platforms) to prevent players from leaving the screen

## 🐛 Troubleshooting

### Level Not Loading
- Check that the JSON file is valid (use a JSON validator)
- Ensure the filename follows the correct naming convention
- Verify all required fields are present in the JSON

### Editor Issues
- Make sure you have write permissions in the levels directory
- Check the console for error messages when saving/loading

### Game Performance
- Large numbers of objects may impact performance
- Keep level complexity reasonable for smooth gameplay

Enjoy creating and playing custom levels! 🎉 