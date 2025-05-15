import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the display
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# You can switch between fullscreen and windowed mode
FULLSCREEN = True

if FULLSCREEN:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
else:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Classroom Platformer")

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

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Physics constants
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
FRICTION = 0.9

class Player:
    def __init__(self, x, y, color, player_num):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.color = color
        self.is_jumping = False
        self.on_ground = False
        self.player_num = player_num
        self.spawn_x = x
        self.spawn_y = y
        self.collected_coins = 0
        self.standing_on_player = False  # New attribute to track if standing on another player
        
    def update(self, platforms, coins, keys_pressed, other_players=None):
        # Handle input
        if self.player_num == 1:
            if keys_pressed[pygame.K_a]:
                self.vel_x = -MOVE_SPEED
            elif keys_pressed[pygame.K_d]:
                self.vel_x = MOVE_SPEED
            else:
                self.vel_x *= FRICTION
                
            if keys_pressed[pygame.K_w] and (self.on_ground or self.standing_on_player):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
        else:  # Player 2
            if keys_pressed[pygame.K_LEFT]:
                self.vel_x = -MOVE_SPEED
            elif keys_pressed[pygame.K_RIGHT]:
                self.vel_x = MOVE_SPEED
            else:
                self.vel_x *= FRICTION
                
            if keys_pressed[pygame.K_UP] and (self.on_ground or self.standing_on_player):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
        
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 20:  # Terminal velocity
            self.vel_y = 20
        
        # Move horizontally
        self.rect.x += self.vel_x
        self.check_platform_collisions(platforms, 'horizontal')
        if other_players:
            self.check_player_collisions(other_players, 'horizontal')
        
        # Move vertically
        self.rect.y += self.vel_y
        self.on_ground = False
        self.standing_on_player = False
        self.check_platform_collisions(platforms, 'vertical')
        if other_players:
            self.check_player_collisions(other_players, 'vertical')
        
        # Collect coins
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.collected_coins += 1
        
        # Keep player on screen
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        
        # Reset if fallen off screen
        if self.rect.y > SCREEN_HEIGHT:
            self.respawn()
    
    def check_platform_collisions(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                    self.vel_x = 0
                elif direction == 'vertical':
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.is_jumping = False
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
    
    def check_player_collisions(self, other_players, direction):
        for player in other_players:
            if player != self and self.rect.colliderect(player.rect):
                if direction == 'horizontal':
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = player.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = player.rect.right
                    self.vel_x = 0
                elif direction == 'vertical':
                    if self.vel_y > 0:  # Falling onto another player
                        # Only stand on top if we're mostly above them
                        if self.rect.bottom - self.vel_y <= player.rect.top + 10:
                            self.rect.bottom = player.rect.top
                            self.vel_y = 0
                            self.standing_on_player = True
                            self.is_jumping = False
                    elif self.vel_y < 0:  # Jumping into player from below
                        self.rect.top = player.rect.bottom
                        self.vel_y = 0
    
    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vel_x = 0
        self.vel_y = 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Draw player number
        text = font_small.render(f"P{self.player_num}", True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
        # Visual indicator when standing on another player
        if self.standing_on_player:
            pygame.draw.rect(screen, WHITE, (self.rect.x, self.rect.bottom - 3, self.rect.width, 3))

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = YELLOW
        self.angle = 0
    
    def update(self):
        self.angle += 2
    
    def draw(self, screen):
        # Draw rotating coin
        center = self.rect.center
        points = []
        for i in range(8):
            angle = self.angle + i * 45
            x = center[0] + 15 * math.cos(math.radians(angle))
            y = center[1] + 15 * math.sin(math.radians(angle))
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, BLACK, points, 2)

class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 80)
        self.color = GREEN
    
    def draw(self, screen):
        # Draw flag pole
        pygame.draw.rect(screen, BROWN, (self.rect.x + 25, self.rect.y, 10, self.rect.height))
        # Draw flag
        pygame.draw.polygon(screen, self.color, [
            (self.rect.x + 35, self.rect.y),
            (self.rect.x + 60, self.rect.y + 20),
            (self.rect.x + 35, self.rect.y + 40)
        ])

def create_level_1():
    platforms = [
        # Floor
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
        
        # Platforms
        Platform(200, SCREEN_HEIGHT - 150, 200, 20),
        Platform(500, SCREEN_HEIGHT - 250, 200, 20),
        Platform(800, SCREEN_HEIGHT - 350, 200, 20),
        Platform(400, SCREEN_HEIGHT - 450, 300, 20),
        Platform(100, SCREEN_HEIGHT - 550, 200, 20),
        Platform(900, SCREEN_HEIGHT - 550, 200, 20),
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        Coin(250, SCREEN_HEIGHT - 200),
        Coin(550, SCREEN_HEIGHT - 300),
        Coin(850, SCREEN_HEIGHT - 400),
        Coin(450, SCREEN_HEIGHT - 500),
        Coin(150, SCREEN_HEIGHT - 600),
        Coin(950, SCREEN_HEIGHT - 600),
    ]
    
    return platforms, coins

def main():
    # Create game objects
    player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, 1)
    player2 = Player(150, SCREEN_HEIGHT - 100, RED, 2)
    
    platforms, coins = create_level_1()
    goal = Goal(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120)
    
    running = True
    game_complete = False
    
    while running:
        keys_pressed = pygame.key.get_pressed()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset level
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins = create_level_1()
                    game_complete = False
        
        if not game_complete:
            # Update game objects
            player1.update(platforms, coins, keys_pressed, [player2])
            player2.update(platforms, coins, keys_pressed, [player1])
            
            for coin in coins:
                coin.update()
            
            # Check win condition
            if (player1.rect.colliderect(goal.rect) and 
                player2.rect.colliderect(goal.rect) and 
                len(coins) == 0):
                game_complete = True
        
        # Draw everything
        screen.fill((135, 206, 235))  # Sky blue
        
        # Draw platforms
        for platform in platforms:
            platform.draw(screen)
        
        # Draw coins
        for coin in coins:
            coin.draw(screen)
        
        # Draw goal
        goal.draw(screen)
        
        # Draw players
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw UI
        score_text = font_medium.render(f"Coins: {player1.collected_coins + player2.collected_coins}/{6 - len(coins)}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Draw instructions
        instructions = [
            "Player 1: WASD to move",
            "Player 2: Arrow keys to move",
            "Players can stand on each other to reach higher platforms!",
            "Collect all coins and reach the flag together!",
            "Press R to restart level, ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = font_small.render(instruction, True, BLACK)
            screen.blit(inst_text, (20, SCREEN_HEIGHT - 100 + i * 25))
        
        if game_complete:
            # Victory message
            victory_text = font_large.render("LEVEL COMPLETE!", True, GREEN)
            victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
            pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
            screen.blit(victory_text, victory_rect)
            
            continue_text = font_medium.render("Press R to play again", True, BLACK)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            screen.blit(continue_text, continue_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
