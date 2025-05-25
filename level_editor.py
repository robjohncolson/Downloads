import pygame
import sys
import json
import os
import math

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Level Editor")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_large = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 18)

class LevelEditor:
    def __init__(self):
        self.mode = "platform"  # Current editing mode: platform, coin, spike, goal, spawn
        self.platforms = []
        self.coins = []
        self.spikes = []
        self.goal = None
        self.player_spawns = [{"x": 100, "y": 640}, {"x": 150, "y": 640}]
        
        # Drawing state
        self.drawing = False
        self.start_pos = None
        self.current_rect = None
        
        # Level metadata
        self.world = 1
        self.level = 1
        self.level_name = "New Level"
        self.background_type = "day"
        
        # UI
        self.selected_spawn = 0  # Which player spawn is selected (0 or 1)
        
        # Grid
        self.grid_size = 20
        self.show_grid = True
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
    def snap_to_grid(self, pos):
        """Snap position to grid"""
        x, y = pos
        return (
            round(x / self.grid_size) * self.grid_size,
            round(y / self.grid_size) * self.grid_size
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_1:
                    self.mode = "platform"
                elif event.key == pygame.K_2:
                    self.mode = "coin"
                elif event.key == pygame.K_3:
                    self.mode = "spike"
                elif event.key == pygame.K_4:
                    self.mode = "goal"
                elif event.key == pygame.K_5:
                    self.mode = "spawn"
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_level()
                elif event.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_level()
                elif event.key == pygame.K_n and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.new_level()
                elif event.key == pygame.K_DELETE:
                    self.delete_at_mouse()
                elif event.key == pygame.K_TAB:
                    if self.mode == "spawn":
                        self.selected_spawn = 1 - self.selected_spawn  # Toggle between 0 and 1
                elif event.key == pygame.K_b:
                    self.background_type = "night" if self.background_type == "day" else "day"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = self.snap_to_grid(mouse_pos)
                    
                    if self.mode == "platform":
                        self.drawing = True
                        self.start_pos = grid_pos
                    elif self.mode == "coin":
                        self.add_coin(grid_pos)
                    elif self.mode == "spike":
                        self.drawing = True
                        self.start_pos = grid_pos
                    elif self.mode == "goal":
                        self.set_goal(grid_pos)
                    elif self.mode == "spawn":
                        self.set_spawn(grid_pos)
                
                elif event.button == 3:  # Right click - delete
                    self.delete_at_mouse()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drawing:
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = self.snap_to_grid(mouse_pos)
                    
                    if self.mode == "platform":
                        self.add_platform(self.start_pos, grid_pos)
                    elif self.mode == "spike":
                        self.add_spike(self.start_pos, grid_pos)
                    
                    self.drawing = False
                    self.start_pos = None
    
    def add_platform(self, start_pos, end_pos):
        """Add a platform from start to end position"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1) + self.grid_size
        height = abs(y2 - y1) + self.grid_size
        
        if width > 0 and height > 0:
            self.platforms.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "color": [139, 69, 19]
            })
    
    def add_coin(self, pos):
        """Add a coin at position"""
        x, y = pos
        self.coins.append({"x": x, "y": y})
    
    def add_spike(self, start_pos, end_pos):
        """Add a spike from start to end position"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1) + self.grid_size
        height = abs(y2 - y1) + self.grid_size
        
        if width > 0 and height > 0:
            self.spikes.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height
            })
    
    def set_goal(self, pos):
        """Set goal position"""
        x, y = pos
        self.goal = {"x": x, "y": y, "is_door": False}
    
    def set_spawn(self, pos):
        """Set player spawn position"""
        x, y = pos
        self.player_spawns[self.selected_spawn] = {"x": x, "y": y}
    
    def delete_at_mouse(self):
        """Delete object at mouse position"""
        mouse_pos = pygame.mouse.get_pos()
        x, y = mouse_pos
        
        # Check platforms
        for platform in self.platforms[:]:
            if (platform["x"] <= x <= platform["x"] + platform["width"] and
                platform["y"] <= y <= platform["y"] + platform["height"]):
                self.platforms.remove(platform)
                return
        
        # Check coins
        for coin in self.coins[:]:
            if (coin["x"] <= x <= coin["x"] + 30 and
                coin["y"] <= y <= coin["y"] + 30):
                self.coins.remove(coin)
                return
        
        # Check spikes
        for spike in self.spikes[:]:
            if (spike["x"] <= x <= spike["x"] + spike["width"] and
                spike["y"] <= y <= spike["y"] + spike["height"]):
                self.spikes.remove(spike)
                return
        
        # Check goal
        if self.goal:
            if (self.goal["x"] <= x <= self.goal["x"] + 60 and
                self.goal["y"] <= y <= self.goal["y"] + 80):
                self.goal = None
    
    def save_level(self):
        """Save current level to JSON file"""
        if not os.path.exists("levels"):
            os.makedirs("levels")
        
        level_data = {
            "world": self.world,
            "level": self.level,
            "name": self.level_name,
            "background_type": self.background_type,
            "platforms": self.platforms,
            "coins": self.coins,
            "spikes": self.spikes,
            "goal": self.goal or {"x": SCREEN_WIDTH - 100, "y": SCREEN_HEIGHT - 120, "is_door": False},
            "player_spawns": self.player_spawns
        }
        
        filename = f"levels/world{self.world}_level{self.level}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(level_data, f, indent=2)
            print(f"Level saved as {filename}")
        except Exception as e:
            print(f"Error saving level: {e}")
    
    def load_level(self):
        """Load level from JSON file"""
        filename = f"levels/world{self.world}_level{self.level}.json"
        try:
            with open(filename, 'r') as f:
                level_data = json.load(f)
            
            self.world = level_data.get("world", 1)
            self.level = level_data.get("level", 1)
            self.level_name = level_data.get("name", "Loaded Level")
            self.background_type = level_data.get("background_type", "day")
            self.platforms = level_data.get("platforms", [])
            self.coins = level_data.get("coins", [])
            self.spikes = level_data.get("spikes", [])
            self.goal = level_data.get("goal")
            self.player_spawns = level_data.get("player_spawns", [{"x": 100, "y": 640}, {"x": 150, "y": 640}])
            
            print(f"Level loaded from {filename}")
        except Exception as e:
            print(f"Error loading level: {e}")
    
    def new_level(self):
        """Create a new empty level"""
        self.platforms = []
        self.coins = []
        self.spikes = []
        self.goal = None
        self.player_spawns = [{"x": 100, "y": 640}, {"x": 150, "y": 640}]
        self.level_name = "New Level"
        print("New level created")
    
    def draw_grid(self, screen):
        """Draw grid lines"""
        if not self.show_grid:
            return
        
        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, self.grid_size):
            pygame.draw.line(screen, LIGHT_GRAY, (0, y), (SCREEN_WIDTH, y))
    
    def draw_objects(self, screen):
        """Draw all level objects"""
        # Draw platforms
        for platform in self.platforms:
            color = tuple(platform["color"])
            rect = pygame.Rect(platform["x"], platform["y"], platform["width"], platform["height"])
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        
        # Draw coins
        for coin in self.coins:
            center = (coin["x"] + 15, coin["y"] + 15)
            pygame.draw.circle(screen, YELLOW, center, 15)
            pygame.draw.circle(screen, BLACK, center, 15, 2)
        
        # Draw spikes
        for spike in self.spikes:
            rect = pygame.Rect(spike["x"], spike["y"], spike["width"], spike["height"])
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            # Draw spike triangles
            num_spikes = spike["width"] // 10
            for i in range(num_spikes):
                spike_x = spike["x"] + i * 10 + 5
                pygame.draw.polygon(screen, GRAY, [
                    (spike_x - 5, spike["y"] + spike["height"]),
                    (spike_x, spike["y"]),
                    (spike_x + 5, spike["y"] + spike["height"])
                ])
        
        # Draw goal
        if self.goal:
            rect = pygame.Rect(self.goal["x"], self.goal["y"], 60, 80)
            pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            # Draw flag
            pygame.draw.polygon(screen, GREEN, [
                (self.goal["x"] + 35, self.goal["y"]),
                (self.goal["x"] + 60, self.goal["y"] + 20),
                (self.goal["x"] + 35, self.goal["y"] + 40)
            ])
        
        # Draw player spawns
        for i, spawn in enumerate(self.player_spawns):
            color = BLUE if i == 0 else RED
            rect = pygame.Rect(spawn["x"], spawn["y"], 40, 40)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            # Highlight selected spawn
            if i == self.selected_spawn and self.mode == "spawn":
                pygame.draw.rect(screen, WHITE, rect, 4)
    
    def draw_current_drawing(self, screen):
        """Draw the object currently being drawn"""
        if not self.drawing or not self.start_pos:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        grid_pos = self.snap_to_grid(mouse_pos)
        
        x1, y1 = self.start_pos
        x2, y2 = grid_pos
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1) + self.grid_size
        height = abs(y2 - y1) + self.grid_size
        
        rect = pygame.Rect(x, y, width, height)
        
        if self.mode == "platform":
            pygame.draw.rect(screen, BROWN, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        elif self.mode == "spike":
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
    
    def draw_ui(self, screen):
        """Draw user interface"""
        # Background for UI
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(screen, DARK_GRAY, ui_rect)
        pygame.draw.rect(screen, BLACK, ui_rect, 2)
        
        # Mode indicators
        modes = [
            ("1: Platform", "platform", BROWN),
            ("2: Coin", "coin", YELLOW),
            ("3: Spike", "spike", GRAY),
            ("4: Goal", "goal", GREEN),
            ("5: Spawn", "spawn", BLUE)
        ]
        
        x_offset = 10
        for text, mode, color in modes:
            text_color = WHITE if self.mode == mode else LIGHT_GRAY
            text_surface = font_medium.render(text, True, text_color)
            screen.blit(text_surface, (x_offset, 10))
            x_offset += text_surface.get_width() + 20
        
        # Level info
        info_text = f"World: {self.world} Level: {self.level} | {self.level_name} | BG: {self.background_type}"
        info_surface = font_medium.render(info_text, True, WHITE)
        screen.blit(info_surface, (10, 35))
        
        # Instructions
        instructions = [
            "Ctrl+S: Save | Ctrl+L: Load | Ctrl+N: New | Del/RClick: Delete",
            "G: Toggle Grid | B: Toggle Background | Tab: Switch Spawn (in spawn mode)"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = font_small.render(instruction, True, LIGHT_GRAY)
            screen.blit(inst_surface, (10, 60 + i * 20))
        
        # Current mode info
        mode_info = ""
        if self.mode == "spawn":
            mode_info = f"Selected spawn: Player {self.selected_spawn + 1}"
        elif self.mode == "platform":
            mode_info = "Click and drag to create platforms"
        elif self.mode == "coin":
            mode_info = "Click to place coins"
        elif self.mode == "spike":
            mode_info = "Click and drag to create spikes"
        elif self.mode == "goal":
            mode_info = "Click to place goal"
        
        if mode_info:
            mode_surface = font_small.render(mode_info, True, YELLOW)
            screen.blit(mode_surface, (SCREEN_WIDTH - mode_surface.get_width() - 10, 10))
    
    def run(self):
        """Main editor loop"""
        running = True
        
        while running:
            running = self.handle_events()
            
            # Clear screen
            if self.background_type == "night":
                screen.fill((25, 25, 50))  # Night sky
            else:
                screen.fill((135, 206, 235))  # Day sky
            
            # Draw everything
            self.draw_grid(screen)
            self.draw_objects(screen)
            self.draw_current_drawing(screen)
            self.draw_ui(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    editor = LevelEditor()
    editor.run()

if __name__ == "__main__":
    main() 