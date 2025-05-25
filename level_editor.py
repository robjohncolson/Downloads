import pygame
import json
import math
import os

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
GRID_SIZE = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
BROWN = (139, 69, 19)
ORANGE = (255, 150, 50)
CYAN = (100, 255, 255)

class LevelEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Platformer Level Editor")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Level data
        self.platforms = []
        self.coins = []
        self.spikes = []
        self.goal = {"x": WINDOW_WIDTH - 100, "y": WINDOW_HEIGHT - 120, "is_door": False}
        self.player_spawns = [{"x": 100, "y": WINDOW_HEIGHT - 100}, {"x": 150, "y": WINDOW_HEIGHT - 100}]
        
        # Editor state
        self.mode = "platform"  # "platform", "coin", "spike", "goal", "spawn"
        self.selected_object = None
        self.selected_spawn = 0
        
        # Drawing state
        self.drawing = False
        self.start_pos = None
        
        # Level metadata
        self.world = 1
        self.level = 1
        self.level_name = "New Level"
        self.background_type = "day"
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Grid
        self.show_grid = True
        self.snap_to_grid = True
        
        # Browser state
        self.show_browser = False
        self.browser = None
        
        print("=== Platformer Level Editor ===")
        print("1-5: Switch modes (Platform/Coin/Spike/Goal/Spawn)")
        print("Mouse: Left click - Place/Select, Right click - Delete")
        print("WASD: Move camera, G: Toggle grid, Tab: Switch spawn point")
        print("Ctrl+S: Save, Ctrl+L: Load, Ctrl+N: New level")
        print("B: Toggle background (day/night)")
        print("ESC: Exit")
        print("===============================")
    
    def snap_position(self, pos):
        if self.snap_to_grid:
            x, y = pos
            return (round(x / GRID_SIZE) * GRID_SIZE, round(y / GRID_SIZE) * GRID_SIZE)
        return pos
    
    def handle_events(self):
        # Handle browser events first if browser is open
        if self.show_browser and self.browser:
            for event in pygame.event.get():
                if not self.browser.handle_events(event):
                    self.show_browser = False
                    self.browser = None
            return True
        
        keys = pygame.key.get_pressed()
        
        # Camera movement
        if keys[pygame.K_w]:
            self.camera_y -= 5
        if keys[pygame.K_s]:
            self.camera_y += 5
        if keys[pygame.K_a]:
            self.camera_x -= 5
        if keys[pygame.K_d]:
            self.camera_x += 5
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_1:
                    self.mode = "platform"
                    print("Platform mode")
                elif event.key == pygame.K_2:
                    self.mode = "coin"
                    print("Coin mode")
                elif event.key == pygame.K_3:
                    self.mode = "spike"
                    print("Spike mode")
                elif event.key == pygame.K_4:
                    self.mode = "goal"
                    print("Goal mode")
                elif event.key == pygame.K_5:
                    self.mode = "spawn"
                    print("Spawn mode")
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                    print(f"Grid: {'ON' if self.show_grid else 'OFF'}")
                elif event.key == pygame.K_TAB:
                    if self.mode == "spawn":
                        self.selected_spawn = 1 - self.selected_spawn
                        print(f"Selected spawn: {self.selected_spawn + 1}")
                elif event.key == pygame.K_b:
                    self.background_type = "night" if self.background_type == "day" else "day"
                    print(f"Background: {self.background_type}")
                elif event.key == pygame.K_s and keys[pygame.K_LCTRL]:
                    # Open save browser
                    self.browser = LevelBrowser(self)
                    self.browser.mode = "save"
                    self.show_browser = True
                    print("Opening save browser...")
                elif event.key == pygame.K_l and keys[pygame.K_LCTRL]:
                    # Open load browser
                    self.browser = LevelBrowser(self)
                    self.browser.mode = "load"
                    self.show_browser = True
                    print("Opening load browser...")
                elif event.key == pygame.K_n and keys[pygame.K_LCTRL]:
                    self.new_level()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                world_pos = (mouse_pos[0] + self.camera_x, mouse_pos[1] + self.camera_y)
                
                if event.button == 1:  # Left click
                    self.handle_left_click(world_pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(world_pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drawing:
                    mouse_pos = pygame.mouse.get_pos()
                    world_pos = (mouse_pos[0] + self.camera_x, mouse_pos[1] + self.camera_y)
                    self.finish_drawing(world_pos)
        
        return True
    
    def handle_left_click(self, world_pos):
        pos = self.snap_position(world_pos)
        
        if self.mode == "platform":
            self.drawing = True
            self.start_pos = pos
        elif self.mode == "coin":
            self.add_coin(pos)
        elif self.mode == "spike":
            self.drawing = True
            self.start_pos = pos
        elif self.mode == "goal":
            self.set_goal(pos)
        elif self.mode == "spawn":
            self.set_spawn(pos)
    
    def handle_right_click(self, world_pos):
        # Delete object at position
        self.delete_at_position(world_pos)
    
    def finish_drawing(self, world_pos):
        if not self.drawing or not self.start_pos:
            return
        
        end_pos = self.snap_position(world_pos)
        
        if self.mode == "platform":
            self.add_platform(self.start_pos, end_pos)
        elif self.mode == "spike":
            self.add_spike(self.start_pos, end_pos)
        
        self.drawing = False
        self.start_pos = None
    
    def add_platform(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1) + GRID_SIZE
        height = abs(y2 - y1) + GRID_SIZE
        
        if width > 0 and height > 0:
            self.platforms.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "color": [139, 69, 19]
            })
            print(f"Added platform at ({x}, {y}) size {width}x{height}")
    
    def add_coin(self, pos):
        x, y = pos
        self.coins.append({"x": x, "y": y})
        print(f"Added coin at ({x}, {y})")
    
    def add_spike(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1) + GRID_SIZE
        height = abs(y2 - y1) + GRID_SIZE
        
        if width > 0 and height > 0:
            self.spikes.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height
            })
            print(f"Added spike at ({x}, {y}) size {width}x{height}")
    
    def set_goal(self, pos):
        x, y = pos
        self.goal = {"x": x, "y": y, "is_door": False}
        print(f"Set goal at ({x}, {y})")
    
    def set_spawn(self, pos):
        x, y = pos
        self.player_spawns[self.selected_spawn] = {"x": x, "y": y}
        print(f"Set spawn {self.selected_spawn + 1} at ({x}, {y})")
    
    def delete_at_position(self, world_pos):
        x, y = world_pos
        
        # Check platforms
        for i, platform in enumerate(self.platforms):
            px, py, pw, ph = platform["x"], platform["y"], platform["width"], platform["height"]
            if px <= x <= px + pw and py <= y <= py + ph:
                del self.platforms[i]
                print("Deleted platform")
                return
        
        # Check coins
        for i, coin in enumerate(self.coins):
            cx, cy = coin["x"], coin["y"]
            if abs(x - cx) < 30 and abs(y - cy) < 30:
                del self.coins[i]
                print("Deleted coin")
                return
        
        # Check spikes
        for i, spike in enumerate(self.spikes):
            sx, sy, sw, sh = spike["x"], spike["y"], spike["width"], spike["height"]
            if sx <= x <= sx + sw and sy <= y <= sy + sh:
                del self.spikes[i]
                print("Deleted spike")
                return
    
    def save_level(self):
        filename = f"levels/world{self.world}_level{self.level}.json"
        
        # Create levels directory if it doesn't exist
        os.makedirs("levels", exist_ok=True)
        
        level_data = {
            "world": self.world,
            "level": self.level,
            "name": self.level_name,
            "background_type": self.background_type,
            "platforms": self.platforms,
            "coins": self.coins,
            "spikes": self.spikes,
            "goal": self.goal,
            "player_spawns": self.player_spawns
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(level_data, f, indent=2)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_level(self):
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
            self.goal = level_data.get("goal", {"x": WINDOW_WIDTH - 100, "y": WINDOW_HEIGHT - 120, "is_door": False})
            self.player_spawns = level_data.get("player_spawns", [{"x": 100, "y": WINDOW_HEIGHT - 100}, {"x": 150, "y": WINDOW_HEIGHT - 100}])
            
            print(f"Loaded: {filename}")
            print(f"Platforms: {len(self.platforms)}, Coins: {len(self.coins)}, Spikes: {len(self.spikes)}")
            
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Load error: {e}")
    
    def new_level(self):
        self.platforms = []
        self.coins = []
        self.spikes = []
        self.goal = {"x": WINDOW_WIDTH - 100, "y": WINDOW_HEIGHT - 120, "is_door": False}
        self.player_spawns = [{"x": 100, "y": WINDOW_HEIGHT - 100}, {"x": 150, "y": WINDOW_HEIGHT - 100}]
        self.level_name = "New Level"
        self.background_type = "day"
        self.world = 1
        self.level = 1
        print("Created new level")
    
    def draw_grid(self):
        if not self.show_grid:
            return
        
        # Calculate visible grid bounds
        start_x = (self.camera_x // GRID_SIZE) * GRID_SIZE
        start_y = (self.camera_y // GRID_SIZE) * GRID_SIZE
        end_x = start_x + WINDOW_WIDTH + GRID_SIZE
        end_y = start_y + WINDOW_HEIGHT + GRID_SIZE
        
        # Draw vertical lines
        for x in range(int(start_x), int(end_x), GRID_SIZE):
            screen_x = x - self.camera_x
            if 0 <= screen_x <= WINDOW_WIDTH:
                color = GRAY if (x // GRID_SIZE) % 5 == 0 else LIGHT_GRAY
                pygame.draw.line(self.screen, color, (screen_x, 0), (screen_x, WINDOW_HEIGHT))
        
        # Draw horizontal lines
        for y in range(int(start_y), int(end_y), GRID_SIZE):
            screen_y = y - self.camera_y
            if 0 <= screen_y <= WINDOW_HEIGHT:
                color = GRAY if (y // GRID_SIZE) % 5 == 0 else LIGHT_GRAY
                pygame.draw.line(self.screen, color, (0, screen_y), (WINDOW_WIDTH, screen_y))
    
    def world_to_screen(self, world_pos):
        return (world_pos[0] - self.camera_x, world_pos[1] - self.camera_y)
    
    def draw_objects(self):
        # Draw platforms
        for platform in self.platforms:
            x, y = self.world_to_screen((platform["x"], platform["y"]))
            rect = pygame.Rect(x, y, platform["width"], platform["height"])
            pygame.draw.rect(self.screen, BROWN, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw coins
        for coin in self.coins:
            x, y = self.world_to_screen((coin["x"], coin["y"]))
            pygame.draw.circle(self.screen, YELLOW, (int(x), int(y)), 15)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 15, 2)
        
        # Draw spikes
        for spike in self.spikes:
            x, y = self.world_to_screen((spike["x"], spike["y"]))
            rect = pygame.Rect(x, y, spike["width"], spike["height"])
            pygame.draw.rect(self.screen, RED, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw goal
        if self.goal:
            x, y = self.world_to_screen((self.goal["x"], self.goal["y"]))
            rect = pygame.Rect(x, y, 60, 80)
            pygame.draw.rect(self.screen, GREEN, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw player spawns
        for i, spawn in enumerate(self.player_spawns):
            x, y = self.world_to_screen((spawn["x"], spawn["y"]))
            color = BLUE if i == 0 else RED
            if i == self.selected_spawn and self.mode == "spawn":
                pygame.draw.circle(self.screen, YELLOW, (int(x), int(y)), 25, 3)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 20)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 20, 2)
    
    def draw_current_drawing(self):
        if self.drawing and self.start_pos:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = (mouse_pos[0] + self.camera_x, mouse_pos[1] + self.camera_y)
            end_pos = self.snap_position(world_pos)
            
            start_screen = self.world_to_screen(self.start_pos)
            end_screen = self.world_to_screen(end_pos)
            
            x = min(start_screen[0], end_screen[0])
            y = min(start_screen[1], end_screen[1])
            width = abs(end_screen[0] - start_screen[0])
            height = abs(end_screen[1] - start_screen[1])
            
            color = BROWN if self.mode == "platform" else RED
            pygame.draw.rect(self.screen, color, (x, y, width, height), 2)
    
    def draw_ui(self):
        # Background panel
        ui_rect = pygame.Rect(10, 10, 350, 220)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), ui_rect)
        pygame.draw.rect(self.screen, WHITE, ui_rect, 2)
        
        # UI text
        y_pos = 20
        texts = [
            f"Mode: {self.mode.title()}",
            f"Level: {self.level_name}",
            f"World: {self.world} Level: {self.level}",
            f"Background: {self.background_type}",
            f"Platforms: {len(self.platforms)}",
            f"Coins: {len(self.coins)}",
            f"Spikes: {len(self.spikes)}",
            f"Grid: {'ON' if self.show_grid else 'OFF'}",
            f"Camera: ({self.camera_x}, {self.camera_y})"
        ]
        
        if self.mode == "spawn":
            texts.append(f"Selected Spawn: {self.selected_spawn + 1}")
        
        for text in texts:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (20, y_pos))
            y_pos += 20
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            
            # Clear screen
            if self.background_type == "night":
                self.screen.fill((25, 25, 50))
            else:
                self.screen.fill((135, 206, 235))
            
            # Draw everything
            self.draw_grid()
            self.draw_objects()
            self.draw_current_drawing()
            self.draw_ui()
            
            # Draw browser overlay if open
            if self.show_browser and self.browser:
                self.browser.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    try:
        print("Starting Level Editor...")
        editor = LevelEditor()
        editor.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 