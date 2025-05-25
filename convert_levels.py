#!/usr/bin/env python3
import json
import os

# Screen dimensions (from the old code)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def create_level_json(world, level, name, background_type, platforms, coins, spikes, goal_pos, player_spawns):
    """Convert level data to JSON format"""
    
    # Convert platform data
    platform_list = []
    for platform in platforms:
        platform_list.append({
            "x": platform[0],
            "y": platform[1], 
            "width": platform[2],
            "height": platform[3],
            "color": [139, 69, 19]  # Brown color
        })
    
    # Convert coin data
    coin_list = []
    for coin in coins:
        coin_list.append({
            "x": coin[0],
            "y": coin[1]
        })
    
    # Convert spike data
    spike_list = []
    for spike in spikes:
        spike_list.append({
            "x": spike[0],
            "y": spike[1],
            "width": spike[2] if len(spike) > 2 else 30,
            "height": spike[3] if len(spike) > 3 else 15
        })
    
    # Create level data structure
    level_data = {
        "world": world,
        "level": level,
        "name": name,
        "background_type": background_type,
        "platforms": platform_list,
        "coins": coin_list,
        "spikes": spike_list,
        "goal": {
            "x": goal_pos[0],
            "y": goal_pos[1],
            "is_door": goal_pos[2] if len(goal_pos) > 2 else False
        },
        "player_spawns": player_spawns
    }
    
    return level_data

def save_level(level_data):
    """Save level data to JSON file"""
    filename = f"levels/world{level_data['world']}_level{level_data['level']}.json"
    
    # Create levels directory if it doesn't exist
    os.makedirs("levels", exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(level_data, f, indent=2)
    
    print(f"Created: {filename}")

# World 1 Level 3
platforms_1_3 = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Floor
    (100, SCREEN_HEIGHT - 150, 200, 20),
    (400, SCREEN_HEIGHT - 250, 200, 20),
    (100, SCREEN_HEIGHT - 350, 200, 20),
    (400, SCREEN_HEIGHT - 450, 200, 20),
    (100, SCREEN_HEIGHT - 550, 200, 20),
    (400, SCREEN_HEIGHT - 650, 200, 20),
    (100, SCREEN_HEIGHT - 750, 800, 20),  # Top platform
    (300, SCREEN_HEIGHT - 200, 50, 20),   # Bridge
    (300, SCREEN_HEIGHT - 400, 50, 20),   # Bridge
    (300, SCREEN_HEIGHT - 600, 50, 20),   # Bridge
    (0, 0, 20, SCREEN_HEIGHT - 40),       # Left wall
    (SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),  # Right wall
]

coins_1_3 = [
    (150, SCREEN_HEIGHT - 200),
    (450, SCREEN_HEIGHT - 300),
    (150, SCREEN_HEIGHT - 400),
    (450, SCREEN_HEIGHT - 500),
    (150, SCREEN_HEIGHT - 600),
    (450, SCREEN_HEIGHT - 700),
    (250, SCREEN_HEIGHT - 800),
    (550, SCREEN_HEIGHT - 800),
]

level_1_3 = create_level_json(
    1, 3, "Spiral Challenge", "day", 
    platforms_1_3, coins_1_3, [],
    (700, SCREEN_HEIGHT - 830, True),  # Goal with door
    [{"x": 50, "y": SCREEN_HEIGHT - 100}, {"x": 100, "y": SCREEN_HEIGHT - 100}]
)

# World 2 Level 2
platforms_2_2 = [
    (0, SCREEN_HEIGHT - 40, 200, 40),    # Floor with gaps
    (400, SCREEN_HEIGHT - 40, 200, 40),
    (800, SCREEN_HEIGHT - 40, 200, 40),
    (150, SCREEN_HEIGHT - 150, 150, 20),  # Lower platforms
    (350, SCREEN_HEIGHT - 200, 150, 20),
    (550, SCREEN_HEIGHT - 250, 150, 20),
    (750, SCREEN_HEIGHT - 300, 150, 20),
    (200, SCREEN_HEIGHT - 350, 20, 150),  # Vertical walls
    (400, SCREEN_HEIGHT - 400, 20, 150),
    (600, SCREEN_HEIGHT - 450, 20, 150),
    (800, SCREEN_HEIGHT - 500, 20, 150),
    (250, SCREEN_HEIGHT - 350, 100, 20),  # Helper platforms
    (450, SCREEN_HEIGHT - 400, 100, 20),
    (650, SCREEN_HEIGHT - 450, 100, 20),
    (100, SCREEN_HEIGHT - 450, 150, 20),  # Upper platforms
    (300, SCREEN_HEIGHT - 500, 150, 20),
    (500, SCREEN_HEIGHT - 550, 150, 20),
    (700, SCREEN_HEIGHT - 600, 300, 20),  # Final platform
    (0, 0, 20, SCREEN_HEIGHT - 40),      # Walls
    (SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
]

coins_2_2 = [
    (175, SCREEN_HEIGHT - 200),
    (375, SCREEN_HEIGHT - 250),
    (575, SCREEN_HEIGHT - 300),
    (775, SCREEN_HEIGHT - 350),
    (300, SCREEN_HEIGHT - 400),
    (500, SCREEN_HEIGHT - 450),
    (700, SCREEN_HEIGHT - 500),
    (150, SCREEN_HEIGHT - 500),
    (350, SCREEN_HEIGHT - 550),
    (550, SCREEN_HEIGHT - 600),
    (800, SCREEN_HEIGHT - 650),
]

spikes_2_2 = [
    (250, SCREEN_HEIGHT - 40, 100, 15),
    (650, SCREEN_HEIGHT - 40, 100, 15),
    (200, SCREEN_HEIGHT - 150 - 15, 30, 15),
    (600, SCREEN_HEIGHT - 250 - 15, 30, 15),
    (350, SCREEN_HEIGHT - 500 - 15, 30, 15),
]

level_2_2 = create_level_json(
    2, 2, "Wall Jump Challenge", "night",
    platforms_2_2, coins_2_2, spikes_2_2,
    (850, SCREEN_HEIGHT - 680),
    [{"x": 50, "y": SCREEN_HEIGHT - 100}, {"x": 100, "y": SCREEN_HEIGHT - 100}]
)

# World 2 Level 3
platforms_2_3 = [
    (0, SCREEN_HEIGHT - 40, 150, 40),     # Floor with gaps
    (350, SCREEN_HEIGHT - 40, 150, 40),
    (700, SCREEN_HEIGHT - 40, 150, 40),
    (150, SCREEN_HEIGHT - 200, 20, 160),  # Wall jump maze
    (170, SCREEN_HEIGHT - 200, 150, 20),
    (500, SCREEN_HEIGHT - 200, 20, 160),
    (350, SCREEN_HEIGHT - 200, 150, 20),
    (850, SCREEN_HEIGHT - 200, 20, 160),
    (700, SCREEN_HEIGHT - 200, 150, 20),
    (250, SCREEN_HEIGHT - 350, 150, 20),  # Middle section
    (600, SCREEN_HEIGHT - 350, 150, 20),
    (400, SCREEN_HEIGHT - 450, 200, 20),
    (200, SCREEN_HEIGHT - 550, 150, 20),  # Upper section
    (650, SCREEN_HEIGHT - 550, 150, 20),
    (350, SCREEN_HEIGHT - 650, 300, 20),  # Top platform
    (0, 0, 20, SCREEN_HEIGHT - 40),      # Walls
    (SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
]

coins_2_3 = [
    (250, SCREEN_HEIGHT - 250),
    (450, SCREEN_HEIGHT - 250),
    (750, SCREEN_HEIGHT - 250),
    (300, SCREEN_HEIGHT - 400),
    (700, SCREEN_HEIGHT - 400),
    (500, SCREEN_HEIGHT - 500),
    (250, SCREEN_HEIGHT - 600),
    (700, SCREEN_HEIGHT - 600),
    (500, SCREEN_HEIGHT - 700),
]

spikes_2_3 = [
    (150, SCREEN_HEIGHT - 40, 200, 15),
    (500, SCREEN_HEIGHT - 40, 200, 15),
    (400, SCREEN_HEIGHT - 450 - 15, 50, 15),
    (400, SCREEN_HEIGHT - 650 - 15, 50, 15),
]

level_2_3 = create_level_json(
    2, 3, "Maze Master", "night",
    platforms_2_3, coins_2_3, spikes_2_3,
    (500, SCREEN_HEIGHT - 700, True),  # Goal with door
    [{"x": 75, "y": SCREEN_HEIGHT - 100}, {"x": 125, "y": SCREEN_HEIGHT - 100}]
)

# World 3 Level 1
platforms_3_1 = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Floor
    (200, SCREEN_HEIGHT - 150, 200, 20),        # Floating platforms
    (500, SCREEN_HEIGHT - 250, 200, 20),
    (800, SCREEN_HEIGHT - 350, 200, 20),
    (300, SCREEN_HEIGHT - 450, 200, 20),        # Upper platforms
    (600, SCREEN_HEIGHT - 550, 400, 20),
]

coins_3_1 = [
    (300, SCREEN_HEIGHT - 200),
    (600, SCREEN_HEIGHT - 300),
    (900, SCREEN_HEIGHT - 400),
    (400, SCREEN_HEIGHT - 500),
    (700, SCREEN_HEIGHT - 600),
    (900, SCREEN_HEIGHT - 600),
]

spikes_3_1 = [
    (400, SCREEN_HEIGHT - 150 - 15, 50, 15),
    (700, SCREEN_HEIGHT - 250 - 15, 50, 15),
]

level_3_1 = create_level_json(
    3, 1, "Sky Islands", "day",
    platforms_3_1, coins_3_1, spikes_3_1,
    (900, SCREEN_HEIGHT - 600),
    [{"x": 100, "y": SCREEN_HEIGHT - 100}, {"x": 150, "y": SCREEN_HEIGHT - 100}]
)

# World 3 Level 2
platforms_3_2 = [
    (0, SCREEN_HEIGHT - 40, 300, 40),     # Floor with gaps
    (500, SCREEN_HEIGHT - 40, 300, 40),
    (900, SCREEN_HEIGHT - 40, 300, 40),
    (200, SCREEN_HEIGHT - 200, 150, 20),  # Middle platforms
    (450, SCREEN_HEIGHT - 300, 150, 20),
    (700, SCREEN_HEIGHT - 400, 150, 20),
    (300, SCREEN_HEIGHT - 500, 200, 20),  # Upper platforms
    (600, SCREEN_HEIGHT - 600, 400, 20),
    (0, 0, 20, SCREEN_HEIGHT - 40),      # Walls
    (SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
]

coins_3_2 = [
    (250, SCREEN_HEIGHT - 250),
    (500, SCREEN_HEIGHT - 350),
    (750, SCREEN_HEIGHT - 450),
    (400, SCREEN_HEIGHT - 550),
    (700, SCREEN_HEIGHT - 650),
    (900, SCREEN_HEIGHT - 650),
]

spikes_3_2 = [
    (300, SCREEN_HEIGHT - 40, 200, 15),
    (800, SCREEN_HEIGHT - 40, 100, 15),
    (350, SCREEN_HEIGHT - 200 - 15, 50, 15),
    (600, SCREEN_HEIGHT - 300 - 15, 50, 15),
]

level_3_2 = create_level_json(
    3, 2, "Floating Fortress", "day",
    platforms_3_2, coins_3_2, spikes_3_2,
    (900, SCREEN_HEIGHT - 650),
    [{"x": 100, "y": SCREEN_HEIGHT - 100}, {"x": 150, "y": SCREEN_HEIGHT - 100}]
)

# World 3 Level 3 - Final Boss Level
platforms_3_3 = [
    (50, SCREEN_HEIGHT - 40, 100, 40),    # Starting platform
    (250, SCREEN_HEIGHT - 120, 80, 20),   # Floating islands
    (450, SCREEN_HEIGHT - 180, 80, 20),
    (650, SCREEN_HEIGHT - 240, 80, 20),
    (850, SCREEN_HEIGHT - 300, 80, 20),
    (100, SCREEN_HEIGHT - 350, 20, 200),  # Wall jump section
    (300, SCREEN_HEIGHT - 350, 20, 200),
    (100, SCREEN_HEIGHT - 350, 220, 20),  # Top connector
    (400, SCREEN_HEIGHT - 400, 40, 20),   # Narrow platforms
    (500, SCREEN_HEIGHT - 450, 40, 20),
    (600, SCREEN_HEIGHT - 500, 40, 20),
    (700, SCREEN_HEIGHT - 550, 40, 20),
    (800, SCREEN_HEIGHT - 600, 40, 20),
    (700, SCREEN_HEIGHT - 650, 150, 20),  # Zigzag pattern
    (450, SCREEN_HEIGHT - 700, 150, 20),
    (700, SCREEN_HEIGHT - 750, 150, 20),
    (450, SCREEN_HEIGHT - 800, 150, 20),
    (300, SCREEN_HEIGHT - 850, 100, 20),  # Final platform
    (0, 0, 20, SCREEN_HEIGHT),           # Walls
    (SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT),
    (200, SCREEN_HEIGHT - 200, 100, 20),  # Trap platforms
    (500, SCREEN_HEIGHT - 300, 100, 20),
    (300, SCREEN_HEIGHT - 500, 100, 20),
    (900, SCREEN_HEIGHT - 450, 100, 20),
]

coins_3_3 = [
    (100, SCREEN_HEIGHT - 100),           # Starting coin
    (280, SCREEN_HEIGHT - 170),          # Floating islands
    (480, SCREEN_HEIGHT - 230),
    (680, SCREEN_HEIGHT - 290),
    (200, SCREEN_HEIGHT - 400),          # Wall jump area
    (150, SCREEN_HEIGHT - 450),
    (420, SCREEN_HEIGHT - 450),          # Narrow platforms
    (520, SCREEN_HEIGHT - 500),
    (620, SCREEN_HEIGHT - 550),
    (720, SCREEN_HEIGHT - 600),
    (750, SCREEN_HEIGHT - 700),          # Zigzag pattern
    (500, SCREEN_HEIGHT - 750),
    (750, SCREEN_HEIGHT - 800),
    (350, SCREEN_HEIGHT - 900),          # Final coin
]

spikes_3_3 = [
    (150, SCREEN_HEIGHT - 40, 100, 15),   # Gap spikes
    (220, SCREEN_HEIGHT - 200 - 15, 60, 15),  # Trap platform spikes
    (520, SCREEN_HEIGHT - 300 - 15, 60, 15),
    (320, SCREEN_HEIGHT - 500 - 15, 60, 15),
    (920, SCREEN_HEIGHT - 450 - 15, 60, 15),
    (440, SCREEN_HEIGHT - 400, 60, 15),   # Between narrow platforms
    (540, SCREEN_HEIGHT - 450, 60, 15),
    (640, SCREEN_HEIGHT - 500, 60, 15),
    (740, SCREEN_HEIGHT - 550, 60, 15),
    (600, SCREEN_HEIGHT - 650 - 15, 50, 15),  # Zigzag spikes
    (550, SCREEN_HEIGHT - 700 - 15, 50, 15),
    (600, SCREEN_HEIGHT - 750 - 15, 50, 15),
    (400, SCREEN_HEIGHT - 850, 50, 15),   # Final spike
]

level_3_3 = create_level_json(
    3, 3, "Ultimate Challenge", "day",
    platforms_3_3, coins_3_3, spikes_3_3,
    (350, SCREEN_HEIGHT - 900),
    [{"x": 75, "y": SCREEN_HEIGHT - 100}, {"x": 125, "y": SCREEN_HEIGHT - 100}]
)

# Save all levels
if __name__ == "__main__":
    print("Converting old level functions to JSON format...")
    save_level(level_1_3)
    save_level(level_2_2)
    save_level(level_2_3)
    save_level(level_3_1)
    save_level(level_3_2)
    save_level(level_3_3)
    print("All missing levels have been created!") 