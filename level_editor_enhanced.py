import pygame
import json
import math
import os
import glob
import re

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
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
BROWN = (139, 69, 19)
ORANGE = (255, 150, 50)
CYAN = (100, 255, 255)

class LevelBrowser:
    def __init__(self, editor):
        self.editor = editor
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)
        
        # Browser state
        self.mode = "load"  # "load" or "save"
        self.selected_index = 0
        self.scroll_offset = 0
        self.levels = []
        self.save_filename = ""
        self.typing_filename = False
        
        # UI dimensions - will be updated based on screen size
        self.update_dimensions()
        
        self.refresh_levels()
    
    def update_dimensions(self):
        """Update UI dimensions based on current screen size"""
        screen_width, screen_height = self.editor.screen.get_size()
        
        # Scale browser to fit screen while maintaining proportions
        browser_width = min(880, screen_width - 200)
        browser_height = min(520, screen_height - 200)
        browser_x = (screen_width - browser_width) // 2
        browser_y = (screen_height - browser_height) // 2
        
        self.browser_rect = pygame.Rect(browser_x, browser_y, browser_width, browser_height)
        
        # List takes up left side of browser
        list_width = min(400, browser_width // 2 - 20)
        list_height = browser_height - 180
        self.list_rect = pygame.Rect(browser_x + 20, browser_y + 160, list_width, list_height)
        
        # Preview takes up right side
        preview_width = browser_width - list_width - 60
        preview_height = list_height
        self.preview_rect = pygame.Rect(browser_x + list_width + 40, browser_y + 160, preview_width, preview_height)
    
    def refresh_levels(self):
        """Scan the levels directory and build a list of available levels"""
        self.levels = []
        
        if not os.path.exists("levels"):
            return
        
        # Get all JSON files in levels directory
        level_files = glob.glob("levels/*.json")
        level_files.sort()
        
        for filepath in level_files:
            try:
                with open(filepath, 'r') as f:
                    level_data = json.load(f)
                
                filename = os.path.basename(filepath)
                
                # Extract world and level from filename if possible
                match = re.match(r'world(\d+)_level(\d+)\.json', filename)
                if match:
                    world, level = int(match.group(1)), int(match.group(2))
                else:
                    world, level = level_data.get("world", 0), level_data.get("level", 0)
                
                self.levels.append({
                    "filename": filename,
                    "filepath": filepath,
                    "name": level_data.get("name", "Unnamed Level"),
                    "world": world,
                    "level": level,
                    "background": level_data.get("background_type", "day"),
                    "platforms": len(level_data.get("platforms", [])),
                    "coins": len(level_data.get("coins", [])),
                    "spikes": len(level_data.get("spikes", [])),
                    "data": level_data
                })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        
        # Sort by world, then level
        self.levels.sort(key=lambda x: (x["world"], x["level"]))
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False  # Close browser
            
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                self.adjust_scroll()
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.levels) - 1, self.selected_index + 1)
                self.adjust_scroll()
            
            elif event.key == pygame.K_RETURN:
                if self.mode == "load" and self.levels:
                    self.load_selected_level()
                    return False
                elif self.mode == "save":
                    if self.typing_filename:
                        self.save_level()
                        return False
                    else:
                        self.typing_filename = True
            
            elif event.key == pygame.K_TAB:
                self.mode = "save" if self.mode == "load" else "load"
                self.typing_filename = False
            
            elif event.key == pygame.K_F5:
                self.refresh_levels()
            
            # Handle filename typing for save mode
            elif self.mode == "save" and self.typing_filename:
                if event.key == pygame.K_BACKSPACE:
                    self.save_filename = self.save_filename[:-1]
                elif event.unicode.isprintable():
                    self.save_filename += event.unicode
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking in the level list
                if self.list_rect.collidepoint(mouse_pos):
                    relative_y = mouse_pos[1] - self.list_rect.y
                    item_height = 25
                    clicked_index = (relative_y + self.scroll_offset) // item_height
                    
                    if 0 <= clicked_index < len(self.levels):
                        self.selected_index = clicked_index
                        
                        # Double-click to load
                        if self.mode == "load":
                            self.load_selected_level()
                            return False
        
        return True
    
    def adjust_scroll(self):
        """Adjust scroll to keep selected item visible"""
        item_height = 25
        visible_items = self.list_rect.height // item_height
        
        if self.selected_index < self.scroll_offset // item_height:
            self.scroll_offset = self.selected_index * item_height
        elif self.selected_index >= (self.scroll_offset // item_height) + visible_items:
            self.scroll_offset = (self.selected_index - visible_items + 1) * item_height
    
    def load_selected_level(self):
        """Load the currently selected level"""
        if not self.levels or self.selected_index >= len(self.levels):
            return
        
        level_data = self.levels[self.selected_index]["data"]
        
        # Load into editor
        self.editor.world = level_data.get("world", 1)
        self.editor.level = level_data.get("level", 1)
        self.editor.level_name = level_data.get("name", "Loaded Level")
        self.editor.background_type = level_data.get("background_type", "day")
        self.editor.platforms = level_data.get("platforms", [])
        self.editor.coins = level_data.get("coins", [])
        self.editor.spikes = level_data.get("spikes", [])
        self.editor.goal = level_data.get("goal", {"x": WINDOW_WIDTH - 100, "y": WINDOW_HEIGHT - 120, "is_door": False})
        self.editor.player_spawns = level_data.get("player_spawns", [{"x": 100, "y": WINDOW_HEIGHT - 100}, {"x": 150, "y": WINDOW_HEIGHT - 100}])
        
        filename = self.levels[self.selected_index]["filename"]
        print(f"Loaded: {filename}")
        print(f"Level: {self.editor.level_name} (World {self.editor.world}, Level {self.editor.level})")
    
    def save_level(self):
        """Save the current level with the specified filename"""
        if not self.save_filename:
            return
        
        # Ensure .json extension
        filename = self.save_filename
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = f"levels/{filename}"
        
        # Create levels directory if it doesn't exist
        os.makedirs("levels", exist_ok=True)
        
        level_data = {
            "world": self.editor.world,
            "level": self.editor.level,
            "name": self.editor.level_name,
            "background_type": self.editor.background_type,
            "platforms": self.editor.platforms,
            "coins": self.editor.coins,
            "spikes": self.editor.spikes,
            "goal": self.editor.goal,
            "player_spawns": self.editor.player_spawns
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(level_data, f, indent=2)
            print(f"Saved: {filepath}")
            self.refresh_levels()
        except Exception as e:
            print(f"Save error: {e}")
    
    def draw(self, screen):
        # Update dimensions in case screen size changed
        self.update_dimensions()
        
        # Get current screen dimensions
        screen_width, screen_height = screen.get_size()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw main browser window
        pygame.draw.rect(screen, DARK_GRAY, self.browser_rect)
        pygame.draw.rect(screen, WHITE, self.browser_rect, 3)
        
        # Draw title
        title = "Load Level" if self.mode == "load" else "Save Level"
        title_surface = self.title_font.render(title, True, WHITE)
        title_x = self.browser_rect.x + (self.browser_rect.width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, self.browser_rect.y + 10))
        
        # Draw mode tabs
        tab_width = 100
        load_tab = pygame.Rect(self.browser_rect.x + 20, self.browser_rect.y + 50, tab_width, 30)
        save_tab = pygame.Rect(self.browser_rect.x + 130, self.browser_rect.y + 50, tab_width, 30)
        
        load_color = WHITE if self.mode == "load" else GRAY
        save_color = WHITE if self.mode == "save" else GRAY
        
        pygame.draw.rect(screen, load_color, load_tab, 2)
        pygame.draw.rect(screen, save_color, save_tab, 2)
        
        load_text = self.font.render("Load", True, load_color)
        save_text = self.font.render("Save", True, save_color)
        
        screen.blit(load_text, (load_tab.x + 35, load_tab.y + 5))
        screen.blit(save_text, (save_tab.x + 35, save_tab.y + 5))
        
        # Draw level list
        self.draw_level_list(screen)
        
        # Draw preview panel
        self.draw_preview(screen)
        
        # Draw save filename input if in save mode
        if self.mode == "save":
            self.draw_save_input(screen)
        
        # Draw instructions
        self.draw_instructions(screen)
    
    def draw_level_list(self, screen):
        # Draw list background
        pygame.draw.rect(screen, BLACK, self.list_rect)
        pygame.draw.rect(screen, WHITE, self.list_rect, 2)
        
        # Draw list header
        header_text = self.font.render("Available Levels", True, WHITE)
        screen.blit(header_text, (self.list_rect.x + 10, self.list_rect.y - 25))
        
        if not self.levels:
            no_levels_text = self.font.render("No levels found", True, GRAY)
            text_x = self.list_rect.x + (self.list_rect.width - no_levels_text.get_width()) // 2
            text_y = self.list_rect.y + (self.list_rect.height - no_levels_text.get_height()) // 2
            screen.blit(no_levels_text, (text_x, text_y))
            return
        
        # Draw level items
        item_height = 25
        visible_items = self.list_rect.height // item_height
        start_index = self.scroll_offset // item_height
        
        for i in range(start_index, min(start_index + visible_items + 1, len(self.levels))):
            level = self.levels[i]
            y = self.list_rect.y + (i * item_height) - self.scroll_offset
            
            if y + item_height < self.list_rect.y or y > self.list_rect.bottom:
                continue
            
            # Highlight selected item
            if i == self.selected_index:
                highlight_rect = pygame.Rect(self.list_rect.x, y, self.list_rect.width, item_height)
                pygame.draw.rect(screen, BLUE, highlight_rect)
            
            # Draw level info
            world_level = f"W{level['world']}L{level['level']}"
            name = level['name'][:30] + "..." if len(level['name']) > 30 else level['name']
            
            world_text = self.small_font.render(world_level, True, WHITE)
            name_text = self.small_font.render(name, True, WHITE)
            
            screen.blit(world_text, (self.list_rect.x + 5, y + 2))
            screen.blit(name_text, (self.list_rect.x + 60, y + 2))
    
    def draw_preview(self, screen):
        # Draw preview background
        pygame.draw.rect(screen, BLACK, self.preview_rect)
        pygame.draw.rect(screen, WHITE, self.preview_rect, 2)
        
        # Draw preview header
        header_text = self.font.render("Level Preview", True, WHITE)
        screen.blit(header_text, (self.preview_rect.x + 10, self.preview_rect.y - 25))
        
        if not self.levels or self.selected_index >= len(self.levels):
            return
        
        level = self.levels[self.selected_index]
        
        # Draw level details
        y_pos = self.preview_rect.y + 10
        details = [
            f"Name: {level['name']}",
            f"World: {level['world']}, Level: {level['level']}",
            f"Background: {level['background']}",
            f"Platforms: {level['platforms']}",
            f"Coins: {level['coins']}",
            f"Spikes: {level['spikes']}",
            f"File: {level['filename']}"
        ]
        
        for detail in details:
            text = self.small_font.render(detail, True, WHITE)
            screen.blit(text, (self.preview_rect.x + 10, y_pos))
            y_pos += 20
        
        # Draw mini level preview - adjust size based on available space
        preview_height = max(150, self.preview_rect.height - 200)
        preview_area = pygame.Rect(self.preview_rect.x + 10, y_pos + 20, 
                                 self.preview_rect.width - 20, preview_height)
        pygame.draw.rect(screen, DARK_GRAY, preview_area)
        pygame.draw.rect(screen, WHITE, preview_area, 1)
        
        # Scale factor for mini preview
        scale_x = preview_area.width / WINDOW_WIDTH
        scale_y = preview_area.height / WINDOW_HEIGHT
        scale = min(scale_x, scale_y)
        
        # Draw platforms in preview
        for platform in level['data'].get('platforms', []):
            x = preview_area.x + platform['x'] * scale
            y = preview_area.y + platform['y'] * scale
            w = platform['width'] * scale
            h = platform['height'] * scale
            
            if w > 1 and h > 1:  # Only draw if visible
                pygame.draw.rect(screen, BROWN, (x, y, w, h))
        
        # Draw coins in preview
        for coin in level['data'].get('coins', []):
            x = preview_area.x + coin['x'] * scale
            y = preview_area.y + coin['y'] * scale
            radius = max(1, int(15 * scale))
            
            if radius > 0:
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), radius)
        
        # Draw goal in preview
        goal = level['data'].get('goal')
        if goal:
            x = preview_area.x + goal['x'] * scale
            y = preview_area.y + goal['y'] * scale
            w = max(1, int(60 * scale))
            h = max(1, int(80 * scale))
            
            if w > 0 and h > 0:
                pygame.draw.rect(screen, GREEN, (x, y, w, h))
    
    def draw_save_input(self, screen):
        # Draw filename input box
        input_rect = pygame.Rect(self.browser_rect.x + 250, self.browser_rect.y + 90, 300, 30)
        pygame.draw.rect(screen, WHITE if self.typing_filename else GRAY, input_rect, 2)
        
        # Draw label
        label_text = self.font.render("Filename:", True, WHITE)
        screen.blit(label_text, (input_rect.x - 80, input_rect.y + 5))
        
        # Draw filename
        display_text = self.save_filename
        if self.typing_filename and pygame.time.get_ticks() % 1000 < 500:
            display_text += "|"  # Blinking cursor
        
        filename_text = self.font.render(display_text, True, BLACK if self.typing_filename else WHITE)
        screen.blit(filename_text, (input_rect.x + 5, input_rect.y + 5))
    
    def draw_instructions(self, screen):
        instructions = [
            "↑↓: Navigate list",
            "Enter: Load/Save level",
            "Tab: Switch Load/Save",
            "F5: Refresh list",
            "Esc: Close browser"
        ]
        
        y_pos = self.browser_rect.bottom + 10
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            screen.blit(text, (self.browser_rect.x, y_pos))
            y_pos += 18

class LevelEditor:
    def __init__(self):
        # Display settings
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Platformer Level Editor")
        
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
        
        # Camera - removed restrictive bounds
        self.camera_x = 0
        self.camera_y = 0
        
        # Grid
        self.show_grid = True
        self.snap_to_grid = True
        
        # Browser
        self.browser = None
        self.show_browser = False
        
        # Help overlay
        self.show_help = False
        
        print("=== Enhanced Platformer Level Editor ===")
        print("1-5: Switch modes (Platform/Coin/Spike/Goal/Spawn)")
        print("Mouse: Left click - Place/Select, Right click - Delete")
        print("WASD: Move camera, G: Toggle grid, Tab: Switch spawn point")
        print("Ctrl+S: Save As, Ctrl+L: Load Browser, Ctrl+N: New level")
        print("B: Toggle background (day/night), F11: Toggle fullscreen")
        print("F: Frame all objects, R: Reset camera, H: Toggle help")
        print("ESC: Exit")
        print("========================================")
    
    def calculate_level_bounds(self):
        """Calculate the actual bounds of all objects in the level"""
        if not (self.platforms or self.coins or self.spikes or self.goal):
            return {"min_x": -500, "max_x": 1780, "min_y": -500, "max_y": 1220}
        
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        # Check platforms
        for platform in self.platforms:
            min_x = min(min_x, platform["x"])
            max_x = max(max_x, platform["x"] + platform["width"])
            min_y = min(min_y, platform["y"])
            max_y = max(max_y, platform["y"] + platform["height"])
        
        # Check coins
        for coin in self.coins:
            min_x = min(min_x, coin["x"] - 20)
            max_x = max(max_x, coin["x"] + 20)
            min_y = min(min_y, coin["y"] - 20)
            max_y = max(max_y, coin["y"] + 20)
        
        # Check spikes
        for spike in self.spikes:
            min_x = min(min_x, spike["x"])
            max_x = max(max_x, spike["x"] + spike["width"])
            min_y = min(min_y, spike["y"])
            max_y = max(max_y, spike["y"] + spike["height"])
        
        # Check goal
        if self.goal:
            min_x = min(min_x, self.goal["x"])
            max_x = max(max_x, self.goal["x"] + 60)
            min_y = min(min_y, self.goal["y"])
            max_y = max(max_y, self.goal["y"] + 80)
        
        # Check spawns
        for spawn in self.player_spawns:
            min_x = min(min_x, spawn["x"] - 25)
            max_x = max(max_x, spawn["x"] + 25)
            min_y = min(min_y, spawn["y"] - 25)
            max_y = max(max_y, spawn["y"] + 25)
        
        # Add padding
        padding = 200
        return {
            "min_x": min_x - padding,
            "max_x": max_x + padding,
            "min_y": min_y - padding,
            "max_y": max_y + padding
        }
    
    def frame_all_objects(self):
        """Center camera to show all objects in the level"""
        bounds = self.calculate_level_bounds()
        screen_width, screen_height = self.screen.get_size()
        
        # Calculate the actual content size
        content_width = bounds["max_x"] - bounds["min_x"]
        content_height = bounds["max_y"] - bounds["min_y"]
        
        # If content is smaller than screen, center it
        if content_width < screen_width:
            center_x = (bounds["min_x"] + bounds["max_x"]) / 2
            self.camera_x = center_x - screen_width / 2
        else:
            # If content is larger, show from the left edge with some margin
            self.camera_x = bounds["min_x"] - 100
        
        if content_height < screen_height:
            center_y = (bounds["min_y"] + bounds["max_y"]) / 2
            self.camera_y = center_y - screen_height / 2
        else:
            # If content is larger, show from the top edge with some margin
            self.camera_y = bounds["min_y"] - 100
        
        print(f"Framed level: bounds X({bounds['min_x']:.0f} to {bounds['max_x']:.0f}) Y({bounds['min_y']:.0f} to {bounds['max_y']:.0f})")
        print(f"Content size: {content_width:.0f} x {content_height:.0f}")
        print(f"Screen size: {screen_width} x {screen_height}")
        print(f"Camera positioned at ({self.camera_x:.0f}, {self.camera_y:.0f})")
    
    def handle_events(self):
        # Handle browser events first if browser is open
        if self.show_browser and self.browser:
            for event in pygame.event.get():
                if not self.browser.handle_events(event):
                    self.show_browser = False
                    self.browser = None
            return True
        
        keys = pygame.key.get_pressed()
        
        # Camera movement - no constraints, allow free movement
        camera_speed = 10 if keys[pygame.K_LSHIFT] else 5
        if keys[pygame.K_w]:
            self.camera_y -= camera_speed
        if keys[pygame.K_s]:
            self.camera_y += camera_speed
        if keys[pygame.K_a]:
            self.camera_x -= camera_speed
        if keys[pygame.K_d]:
            self.camera_x += camera_speed
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_f:
                    self.frame_all_objects()
                elif event.key == pygame.K_r:
                    self.camera_x = 0
                    self.camera_y = 0
                    print("Camera reset to origin")
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                    print(f"Help overlay: {'ON' if self.show_help else 'OFF'}")
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
        self.camera_x = 0
        self.camera_y = 0
        print("Created new level")
    
    def draw_grid(self):
        if not self.show_grid:
            return
        
        # Get current screen dimensions
        screen_width, screen_height = self.screen.get_size()
        
        # Calculate visible grid bounds
        start_x = (self.camera_x // GRID_SIZE) * GRID_SIZE
        start_y = (self.camera_y // GRID_SIZE) * GRID_SIZE
        end_x = start_x + screen_width + GRID_SIZE
        end_y = start_y + screen_height + GRID_SIZE
        
        # Draw vertical lines
        for x in range(int(start_x), int(end_x), GRID_SIZE):
            screen_x = x - self.camera_x
            if 0 <= screen_x <= screen_width:
                color = GRAY if (x // GRID_SIZE) % 5 == 0 else LIGHT_GRAY
                pygame.draw.line(self.screen, color, (screen_x, 0), (screen_x, screen_height))
        
        # Draw horizontal lines
        for y in range(int(start_y), int(end_y), GRID_SIZE):
            screen_y = y - self.camera_y
            if 0 <= screen_y <= screen_height:
                color = GRAY if (y // GRID_SIZE) % 5 == 0 else LIGHT_GRAY
                pygame.draw.line(self.screen, color, (0, screen_y), (screen_width, screen_y))
    
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
        # Get current screen dimensions
        screen_width, screen_height = self.screen.get_size()
        
        # Background panel
        ui_rect = pygame.Rect(10, 10, 350, 280)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), ui_rect)
        pygame.draw.rect(self.screen, WHITE, ui_rect, 2)
        
        # UI text
        y_pos = 20
        bounds = self.calculate_level_bounds()
        texts = [
            f"Mode: {self.mode.title()}",
            f"Level: {self.level_name}",
            f"World: {self.world} Level: {self.level}",
            f"Background: {self.background_type}",
            f"Platforms: {len(self.platforms)}",
            f"Coins: {len(self.coins)}",
            f"Spikes: {len(self.spikes)}",
            f"Grid: {'ON' if self.show_grid else 'OFF'}",
            f"Camera: ({self.camera_x:.0f}, {self.camera_y:.0f})",
            f"Display: {'Fullscreen' if self.fullscreen else 'Windowed'} ({screen_width}x{screen_height})",
            f"Level bounds: X({bounds['min_x']:.0f} to {bounds['max_x']:.0f}) Y({bounds['min_y']:.0f} to {bounds['max_y']:.0f})"
        ]
        
        if self.mode == "spawn":
            texts.append(f"Selected Spawn: {self.selected_spawn + 1}")
        
        for text in texts:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (20, y_pos))
            y_pos += 20
    
    def draw_help_overlay(self):
        """Draw the help overlay with all shortcut keys"""
        if not self.show_help:
            return
        
        # Get current screen dimensions
        screen_width, screen_height = self.screen.get_size()
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Help panel dimensions
        panel_width = min(800, screen_width - 100)
        panel_height = min(600, screen_height - 100)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Draw help panel
        help_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_GRAY, help_rect)
        pygame.draw.rect(self.screen, WHITE, help_rect, 3)
        
        # Title
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("Level Editor - Shortcut Keys", True, WHITE)
        title_x = panel_x + (panel_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, panel_y + 20))
        
        # Help content in two columns
        left_x = panel_x + 30
        right_x = panel_x + panel_width // 2 + 20
        start_y = panel_y + 80
        
        # Left column - Mode and Object Controls
        left_content = [
            ("MODES:", WHITE),
            ("1 - Platform Mode", LIGHT_GRAY),
            ("2 - Coin Mode", LIGHT_GRAY),
            ("3 - Spike Mode", LIGHT_GRAY),
            ("4 - Goal Mode", LIGHT_GRAY),
            ("5 - Spawn Mode", LIGHT_GRAY),
            ("", WHITE),
            ("MOUSE CONTROLS:", WHITE),
            ("Left Click - Place/Select object", LIGHT_GRAY),
            ("Right Click - Delete object", LIGHT_GRAY),
            ("Drag (Platform/Spike) - Draw rectangle", LIGHT_GRAY),
            ("", WHITE),
            ("CAMERA:", WHITE),
            ("W/A/S/D - Move camera", LIGHT_GRAY),
            ("Shift + WASD - Move faster", LIGHT_GRAY),
            ("F - Frame all objects", LIGHT_GRAY),
            ("R - Reset camera to origin", LIGHT_GRAY),
        ]
        
        # Right column - File and Display Controls
        right_content = [
            ("FILE OPERATIONS:", WHITE),
            ("Ctrl+S - Save level", LIGHT_GRAY),
            ("Ctrl+L - Load level", LIGHT_GRAY),
            ("Ctrl+N - New level", LIGHT_GRAY),
            ("", WHITE),
            ("DISPLAY:", WHITE),
            ("G - Toggle grid", LIGHT_GRAY),
            ("B - Toggle background (day/night)", LIGHT_GRAY),
            ("F11 - Toggle fullscreen", LIGHT_GRAY),
            ("H - Toggle this help", LIGHT_GRAY),
            ("", WHITE),
            ("SPAWN MODE:", WHITE),
            ("Tab - Switch between spawn points", LIGHT_GRAY),
            ("", WHITE),
            ("OTHER:", WHITE),
            ("ESC - Exit editor", LIGHT_GRAY),
        ]
        
        # Draw left column
        y_pos = start_y
        for text, color in left_content:
            if text:
                if color == WHITE:  # Headers
                    surface = self.font.render(text, True, color)
                else:  # Regular items
                    surface = self.small_font.render(text, True, color)
                self.screen.blit(surface, (left_x, y_pos))
            y_pos += 25 if color == WHITE else 20
        
        # Draw right column
        y_pos = start_y
        for text, color in right_content:
            if text:
                if color == WHITE:  # Headers
                    surface = self.font.render(text, True, color)
                else:  # Regular items
                    surface = self.small_font.render(text, True, color)
                self.screen.blit(surface, (right_x, y_pos))
            y_pos += 25 if color == WHITE else 20
        
        # Footer instruction
        footer_text = self.font.render("Press H to close this help", True, YELLOW)
        footer_x = panel_x + (panel_width - footer_text.get_width()) // 2
        footer_y = panel_y + panel_height - 40
        self.screen.blit(footer_text, (footer_x, footer_y))
    
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
            
            # Draw help overlay if open
            self.draw_help_overlay()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Get the current display info to use native resolution
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            print(f"Switched to fullscreen mode ({info.current_w}x{info.current_h})")
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            print(f"Switched to windowed mode ({WINDOW_WIDTH}x{WINDOW_HEIGHT})")
    
    def snap_position(self, pos):
        """Snap position to grid if snap_to_grid is enabled"""
        if self.snap_to_grid:
            x, y = pos
            return (round(x / GRID_SIZE) * GRID_SIZE, round(y / GRID_SIZE) * GRID_SIZE)
        return pos

def main():
    try:
        print("Starting Enhanced Level Editor...")
        editor = LevelEditor()
        editor.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 