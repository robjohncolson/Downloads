import pygame
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound playback

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

# Load sounds
try:
    # Try to load MP3 files
    coin_sound = pygame.mixer.Sound("coin.mp3")  # Use your MP3 file
    level_complete_sound = pygame.mixer.Sound("level_complete.mp3")  # Use your MP3 file
    jump_sound = pygame.mixer.Sound("jump.mp3")  # Use your MP3 file
    
    # Set volume
    coin_sound.set_volume(0.5)
    level_complete_sound.set_volume(0.7)
    jump_sound.set_volume(0.4)
    
    print("Successfully loaded MP3 sound files")
except Exception as e:
    print(f"Warning: Sound files could not be loaded: {e}")
    print("Game will run without sound.")
    # Create dummy sound objects that do nothing when played
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    coin_sound = DummySound()
    level_complete_sound = DummySound()
    jump_sound = DummySound()

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
        self.touching_wall = False  # New attribute to track wall contact
        self.can_wall_jump = False  # New attribute to allow wall jumping
        self.wall_slide_speed = 2  # Slower falling speed when wall sliding
        self.wall_jump_direction = 0  # Direction to bounce when wall jumping
        self.last_wall_id = None  # Track the last wall we jumped from
        self.bounce_timer = 0  # Timer to enforce bounce direction
        self.ignore_wall_contact = False  # Flag to ignore wall contact during bounce
        self.has_wall_jumped = False  # Flag to track if player has performed a wall jump
        
    def update(self, platforms, coins, keys_pressed, other_players=None):
        # Handle bounce timer
        if self.bounce_timer > 0:
            self.bounce_timer -= 1
            # Force velocity in bounce direction while timer is active - back to default force
            self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5  # Back to default 1.5
            
            # While bouncing, ignore wall contact with the same wall
            self.ignore_wall_contact = True
        else:
            self.ignore_wall_contact = False
        
        # Handle input
        if self.player_num == 1:
            if keys_pressed[pygame.K_a]:
                self.vel_x = -MOVE_SPEED
            elif keys_pressed[pygame.K_d]:
                self.vel_x = MOVE_SPEED
            else:
                self.vel_x *= FRICTION
                
            # Check if player can jump
            can_normal_jump = self.on_ground or self.standing_on_player
            can_do_wall_jump = self.can_wall_jump and not self.has_wall_jumped
            
            if keys_pressed[pygame.K_w] and self.bounce_timer <= 0 and (can_normal_jump or can_do_wall_jump):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
                
                if self.can_wall_jump and not self.has_wall_jumped:
                    # Apply horizontal bounce away from wall with default force
                    self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5  # Back to default 1.5
                    self.can_wall_jump = False  # Use up the wall jump
                    self.has_wall_jumped = True  # Mark that player has wall jumped
                    # Briefly prevent player from overriding the bounce direction
                    self.bounce_timer = 10  # Back to original 10 frames
                
                jump_sound.play()  # Play jump sound
                
        elif self.player_num == 2:
            if keys_pressed[pygame.K_LEFT]:
                self.vel_x = -MOVE_SPEED
            elif keys_pressed[pygame.K_RIGHT]:
                self.vel_x = MOVE_SPEED
            else:
                self.vel_x *= FRICTION
                
            # Check if player can jump
            can_normal_jump = self.on_ground or self.standing_on_player
            can_do_wall_jump = self.can_wall_jump and not self.has_wall_jumped
            
            if keys_pressed[pygame.K_UP] and self.bounce_timer <= 0 and (can_normal_jump or can_do_wall_jump):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
                
                if self.can_wall_jump and not self.has_wall_jumped:
                    # Apply horizontal bounce away from wall with default force
                    self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5  # Back to default 1.5
                    self.can_wall_jump = False  # Use up the wall jump
                    self.has_wall_jumped = True  # Mark that player has wall jumped
                    # Briefly prevent player from overriding the bounce direction
                    self.bounce_timer = 10  # Back to original 10 frames
                
                jump_sound.play()  # Play jump sound
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Remove wall sliding - players now fall at normal speed when touching walls
        # if self.touching_wall and self.vel_y > 0 and not self.on_ground:
        #     self.vel_y = self.wall_slide_speed
        
        # Move horizontally
        self.rect.x += int(self.vel_x)
        
        # Check for horizontal collisions
        self.touching_wall = False  # Reset wall contact status
        current_wall_id = None
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    # Only set touching_wall if we're not ignoring wall contact
                    if not (self.ignore_wall_contact and id(platform) == self.last_wall_id):
                        self.touching_wall = True
                        self.wall_jump_direction = -1  # Bounce left when jumping
                        current_wall_id = id(platform)  # Use platform's memory address as unique ID
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    # Only set touching_wall if we're not ignoring wall contact
                    if not (self.ignore_wall_contact and id(platform) == self.last_wall_id):
                        self.touching_wall = True
                        self.wall_jump_direction = 1  # Bounce right when jumping
                        current_wall_id = id(platform)  # Use platform's memory address as unique ID
                self.vel_x = 0
        
        # Enable wall jump if touching a wall, not on ground, and it's a different wall
        # AND player hasn't already used their wall jump
        if self.touching_wall and not self.on_ground and current_wall_id != self.last_wall_id and not self.has_wall_jumped:
            self.can_wall_jump = True
            self.last_wall_id = current_wall_id  # Remember this wall
        else:
            # If player has already wall jumped, don't allow another wall jump
            if self.has_wall_jumped:
                self.can_wall_jump = False
        
        # Move vertically
        self.rect.y += int(self.vel_y)
        
        # Check for vertical collisions
        self.on_ground = False
        self.standing_on_player = False
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                self.vel_y = 0
        
        # Check if standing on another player
        if other_players:
            for other in other_players:
                if (self.rect.bottom == other.rect.top + 1 and 
                    self.rect.right > other.rect.left and 
                    self.rect.left < other.rect.right):
                    self.standing_on_player = True
        
        # Collect coins
        for coin in coins[:]:  # Create a copy of the list to safely remove items
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.collected_coins += 1
                coin_sound.play()  # Play coin sound
        
        # Reset jumping state and wall jump tracking if on ground
        if self.on_ground:
            self.is_jumping = False
            self.last_wall_id = None  # Reset wall tracking when touching ground
            self.has_wall_jumped = False  # Reset wall jump flag when touching ground
            
    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vel_x = 0
        self.vel_y = 0
        self.last_wall_id = None
        self.has_wall_jumped = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Draw eyes
        eye_size = 8
        pygame.draw.circle(screen, WHITE, (self.rect.left + 12, self.rect.top + 15), eye_size)
        pygame.draw.circle(screen, WHITE, (self.rect.right - 12, self.rect.top + 15), eye_size)
        
        # Draw pupils
        pupil_size = 4
        pygame.draw.circle(screen, BLACK, (self.rect.left + 12, self.rect.top + 15), pupil_size)
        pygame.draw.circle(screen, BLACK, (self.rect.right - 12, self.rect.top + 15), pupil_size)
        
        # Draw mouth
        mouth_y = self.rect.top + 28
        pygame.draw.arc(screen, BLACK, (self.rect.left + 10, mouth_y, 20, 10), 0, math.pi, 2)
        
        # Visual indicator for wall sliding
        if self.touching_wall and not self.on_ground:
            # Show a visual indicator on the side where the wall is
            if self.wall_jump_direction == -1:  # Wall is on the right
                pygame.draw.rect(screen, WHITE, (self.rect.right - 3, self.rect.y + 5, 3, self.rect.height - 10))
            elif self.wall_jump_direction == 1:  # Wall is on the left
                pygame.draw.rect(screen, WHITE, (self.rect.left, self.rect.y + 5, 3, self.rect.height - 10))

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

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_levels = 3  # Total number of levels
        
    def next_level(self):
        if self.current_level < self.max_levels:
            self.current_level += 1
            return True
        return False
    
    def reset(self):
        self.current_level = 1
        
    def get_level(self):
        if self.current_level == 1:
            return create_level_1()
        elif self.current_level == 2:
            return create_level_2()
        elif self.current_level == 3:
            return create_level_3()

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
    
    total_coins = len(coins)  # Count the total coins
    
    return platforms, coins, total_coins

def create_level_2():
    platforms = [
        # Floor
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
        
        # Platforms - more accessible arrangement with longer platforms
        Platform(100, SCREEN_HEIGHT - 150, 200, 20),  # Made longer (150->200)
        Platform(400, SCREEN_HEIGHT - 200, 200, 20),  # Made longer (150->200)
        Platform(600, SCREEN_HEIGHT - 250, 200, 20),  # Moved left from 700 to 600
        Platform(300, SCREEN_HEIGHT - 350, 150, 20),  # Moved down from 400 to 350
        Platform(600, SCREEN_HEIGHT - 450, 150, 20),
        Platform(200, SCREEN_HEIGHT - 550, 150, 20),
        # Add connecting platforms to make level completable
        Platform(500, SCREEN_HEIGHT - 650, 400, 20),  # Top platform with goal
        # Add some connecting platforms - removing both problematic bridges
        # Platform(250, SCREEN_HEIGHT - 350, 50, 20),  # Removed this bridge
        # Platform(550, SCREEN_HEIGHT - 350, 50, 20),  # Removing this bridge that blocks progress
        Platform(450, SCREEN_HEIGHT - 550, 50, 20),  # Bridge
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    # Adjust coin position for the moved platform
    coins = [
        Coin(150, SCREEN_HEIGHT - 200),
        Coin(450, SCREEN_HEIGHT - 250),
        Coin(650, SCREEN_HEIGHT - 300),  # Adjusted for moved platform
        Coin(350, SCREEN_HEIGHT - 400),  # Adjusted for moved platform
        Coin(650, SCREEN_HEIGHT - 500),
        Coin(250, SCREEN_HEIGHT - 600),
        Coin(550, SCREEN_HEIGHT - 700),
        Coin(700, SCREEN_HEIGHT - 700),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins

def create_level_3():
    platforms = [
        # Floor - with gaps!
        Platform(0, SCREEN_HEIGHT - 40, 300, 40),
        Platform(400, SCREEN_HEIGHT - 40, 300, 40),
        Platform(800, SCREEN_HEIGHT - 40, 300, 40),
        
        # Platforms - complex arrangement
        Platform(150, SCREEN_HEIGHT - 150, 100, 20),
        Platform(350, SCREEN_HEIGHT - 200, 100, 20),
        Platform(550, SCREEN_HEIGHT - 250, 100, 20),
        Platform(750, SCREEN_HEIGHT - 300, 100, 20),
        Platform(950, SCREEN_HEIGHT - 350, 100, 20),
        Platform(750, SCREEN_HEIGHT - 450, 100, 20),
        Platform(550, SCREEN_HEIGHT - 550, 100, 20),
        Platform(350, SCREEN_HEIGHT - 650, 100, 20),
        Platform(150, SCREEN_HEIGHT - 750, 800, 20),  # Top platform with goal
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
        
        # Additional obstacles
        Platform(300, SCREEN_HEIGHT - 350, 20, 150),  # Vertical obstacle
        Platform(700, SCREEN_HEIGHT - 600, 20, 150),  # Vertical obstacle
    ]
    
    coins = [
        Coin(200, SCREEN_HEIGHT - 200),
        Coin(400, SCREEN_HEIGHT - 250),
        Coin(600, SCREEN_HEIGHT - 300),
        Coin(800, SCREEN_HEIGHT - 350),
        Coin(1000, SCREEN_HEIGHT - 400),
        Coin(800, SCREEN_HEIGHT - 500),
        Coin(600, SCREEN_HEIGHT - 600),
        Coin(400, SCREEN_HEIGHT - 700),
        Coin(200, SCREEN_HEIGHT - 800),
        Coin(600, SCREEN_HEIGHT - 800),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins

def update_goal_position(level):
    if level == 1:
        return Goal(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120)
    elif level == 2:
        return Goal(700, SCREEN_HEIGHT - 730)  # Positioned directly on the top platform
    elif level == 3:
        return Goal(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 830)  # At the top platform for level 3

def main():
    # Create game objects
    player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, 1)
    player2 = Player(150, SCREEN_HEIGHT - 100, RED, 2)
    
    level_manager = LevelManager()
    platforms, coins, total_coins = level_manager.get_level()
    
    # Set goal position based on level
    goal = update_goal_position(level_manager.current_level)
    
    running = True
    game_complete = False
    all_levels_complete = False
    
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
                    
                    if all_levels_complete:
                        level_manager.reset()
                        all_levels_complete = False
                    
                    platforms, coins, total_coins = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_level)  # Update goal position
                    game_complete = False
                elif event.key == pygame.K_n and game_complete and not all_levels_complete:
                    # Next level
                    if level_manager.next_level():
                        player1.respawn()
                        player2.respawn()
                        player1.collected_coins = 0
                        player2.collected_coins = 0
                        platforms, coins, total_coins = level_manager.get_level()
                        goal = update_goal_position(level_manager.current_level)  # Update goal position
                        game_complete = False
                    else:
                        all_levels_complete = True
                # Level selection shortcuts
                elif event.key == pygame.K_1:
                    # Switch to level 1
                    level_manager.current_level = 1
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins, total_coins = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
                elif event.key == pygame.K_2:
                    # Switch to level 2
                    level_manager.current_level = 2
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins, total_coins = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
                elif event.key == pygame.K_3:
                    # Switch to level 3
                    level_manager.current_level = 3
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins, total_coins = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
        
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
        collected_coins = player1.collected_coins + player2.collected_coins
        score_text = font_medium.render(f"Coins: {collected_coins}/{total_coins}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Display current level
        level_text = font_medium.render(f"Level: {level_manager.current_level}/{level_manager.max_levels}", True, BLACK)
        screen.blit(level_text, (20, 60))
        
        # Draw instructions
        instructions = [
            "Player 1: WASD to move",
            "Player 2: Arrow keys to move",
            "Players can stand on each other to reach higher platforms!",
            "Jump off walls to reach higher areas!",
            "Collect all coins and reach the flag together!",
            "Press 1, 2, or 3 to switch levels, R to restart, ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = font_small.render(instruction, True, BLACK)
            screen.blit(inst_text, (20, SCREEN_HEIGHT - 100 + i * 25))
        
        if game_complete:
            if all_levels_complete:
                # Final victory message
                victory_text = font_large.render("ALL LEVELS COMPLETE!", True, GREEN)
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
                pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
                screen.blit(victory_text, victory_rect)
                
                continue_text = font_medium.render("Press R to play again from level 1", True, BLACK)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
                screen.blit(continue_text, continue_rect)
            else:
                # Level complete message
                victory_text = font_large.render(f"LEVEL {level_manager.current_level} COMPLETE!", True, GREEN)
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
                pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
                screen.blit(victory_text, victory_rect)
                
                if level_manager.current_level < level_manager.max_levels:
                    continue_text = font_medium.render("Press N for next level or R to replay", True, BLACK)
                else:
                    continue_text = font_medium.render("Press N to finish or R to replay", True, BLACK)
                    
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
                screen.blit(continue_text, continue_rect)
        
        # Play level complete sound when game is won
        if (player1.rect.colliderect(goal.rect) and 
            player2.rect.colliderect(goal.rect) and 
            len(coins) == 0 and
            not game_complete):  # Only play once when first completing
            level_complete_sound.play()
            game_complete = True
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
