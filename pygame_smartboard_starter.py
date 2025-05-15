import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Set up the display
# Use full screen for the smartboard
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# You can switch between fullscreen and windowed mode
FULLSCREEN = True

if FULLSCREEN:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
else:
    # For testing on desktop
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Smartboard App")

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Font for text
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Interactive elements list
buttons = []
drawing_points = []
is_drawing = False

# Button class for interactive elements
class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.is_hovered = False
        self.callback = None
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

# Create buttons
def create_buttons():
    buttons.clear()
    
    # Clear button
    clear_btn = Button(50, 50, 150, 60, "Clear", RED)
    clear_btn.callback = clear_drawing
    buttons.append(clear_btn)
    
    # Exit button
    exit_btn = Button(SCREEN_WIDTH - 200, 50, 150, 60, "Exit", RED)
    exit_btn.callback = quit_app
    buttons.append(exit_btn)
    
    # Color buttons
    colors = [
        ("Red", RED, 50, 150),
        ("Green", GREEN, 50, 230),
        ("Blue", BLUE, 50, 310),
        ("Black", BLACK, 50, 390),
    ]
    
    for i, (name, color, x, y) in enumerate(colors):
        btn = Button(x, y, 150, 60, name, color, WHITE if color != BLACK else WHITE)
        btn.callback = lambda c=color: set_draw_color(c)
        buttons.append(btn)

# Drawing functions
current_draw_color = BLACK

def set_draw_color(color):
    global current_draw_color
    current_draw_color = color

def clear_drawing():
    global drawing_points
    drawing_points.clear()

def quit_app():
    pygame.quit()
    sys.exit()

# Main game loop
def main():
    global is_drawing
    
    create_buttons()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    pygame.display.toggle_fullscreen()
            
            # Handle button events
            for button in buttons:
                button.handle_event(event)
            
            # Handle drawing
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on drawing area (not on buttons)
                    on_button = any(btn.rect.collidepoint(event.pos) for btn in buttons)
                    if not on_button:
                        is_drawing = True
                        drawing_points.append((event.pos, current_draw_color))
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_drawing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if is_drawing:
                    # Check if not on button area
                    on_button = any(btn.rect.collidepoint(event.pos) for btn in buttons)
                    if not on_button:
                        drawing_points.append((event.pos, current_draw_color))
        
        # Clear screen
        screen.fill(WHITE)
        
        # Draw all points
        for i in range(1, len(drawing_points)):
            if drawing_points[i-1][1] == drawing_points[i][1]:  # Same color
                pygame.draw.line(screen, drawing_points[i][1], 
                               drawing_points[i-1][0], drawing_points[i][0], 5)
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        # Draw title
        title_text = font_large.render("Smartboard Drawing App", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw instructions
        instructions = [
            "Touch to draw, select colors on the left",
            "Press ESC to exit, F to toggle fullscreen"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = font_small.render(instruction, True, GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60 + i*25))
            screen.blit(inst_text, inst_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
