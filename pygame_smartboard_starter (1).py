import pygame
import sys
import math
import random

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
EXPLOSION_COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (255, 255, 255)]  # Red, Orange, Yellow, White

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

# Synthesized sound generation functions
def generate_tone(frequency, duration, sample_rate=22050, volume=0.5):
    """Generate a sine wave tone"""
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        wave = 4096 * volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        arr.append([int(wave), int(wave)])
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_coin_sound():
    """Generate a pleasant coin collection sound - ascending notes"""
    sample_rate = 22050
    duration = 0.3
    frames = int(duration * sample_rate)
    arr = []
    
    # Two ascending tones
    freq1, freq2 = 523, 659  # C5 to E5
    
    for i in range(frames):
        t = i / sample_rate
        # First tone fades out, second tone fades in
        if t < 0.15:
            wave1 = 2048 * 0.3 * math.sin(2 * math.pi * freq1 * t) * (1 - t/0.15)
            wave2 = 2048 * 0.3 * math.sin(2 * math.pi * freq2 * t) * (t/0.15)
        else:
            wave1 = 0
            wave2 = 2048 * 0.3 * math.sin(2 * math.pi * freq2 * t) * ((0.3-t)/0.15)
        
        wave = wave1 + wave2
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_jump_sound():
    """Generate a quick jump sound - rising pitch"""
    sample_rate = 22050
    duration = 0.2
    frames = int(duration * sample_rate)
    arr = []
    
    start_freq, end_freq = 200, 400
    
    for i in range(frames):
        t = i / sample_rate
        # Frequency rises over time
        freq = start_freq + (end_freq - start_freq) * (t / duration)
        # Volume decreases over time
        volume = 0.2 * (1 - t / duration)
        wave = 2048 * volume * math.sin(2 * math.pi * freq * t)
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_level_complete_sound():
    """Generate a victory fanfare - major chord progression"""
    sample_rate = 22050
    duration = 1.0
    frames = int(duration * sample_rate)
    arr = []
    
    # C major chord progression: C-E-G, then C-F-A, then C-E-G (higher)
    chord1 = [262, 330, 392]  # C4-E4-G4
    chord2 = [262, 349, 440]  # C4-F4-A4
    chord3 = [523, 659, 784]  # C5-E5-G5
    
    for i in range(frames):
        t = i / sample_rate
        wave = 0
        
        if t < 0.33:
            # First chord
            for freq in chord1:
                wave += 1024 * 0.3 * math.sin(2 * math.pi * freq * t)
        elif t < 0.66:
            # Second chord
            for freq in chord2:
                wave += 1024 * 0.3 * math.sin(2 * math.pi * freq * t)
        else:
            # Third chord
            for freq in chord3:
                wave += 1024 * 0.3 * math.sin(2 * math.pi * freq * t)
        
        # Apply envelope
        envelope = math.sin(math.pi * (t % 0.33) / 0.33)
        wave *= envelope
        
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_explosion_sound():
    """Generate an explosion sound - noise burst with falling pitch"""
    sample_rate = 22050
    duration = 0.8
    frames = int(duration * sample_rate)
    arr = []
    
    for i in range(frames):
        t = i / sample_rate
        # Start with high frequency noise, drop to low rumble
        freq = 800 * (1 - t / duration) + 50
        # Add noise component
        noise = random.uniform(-1, 1) * 0.5
        # Add sine wave component
        sine = math.sin(2 * math.pi * freq * t)
        # Combine and apply envelope
        volume = 0.8 * (1 - t / duration) ** 0.5
        wave = 3072 * volume * (0.7 * noise + 0.3 * sine)
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

# Generate synthesized sounds
try:
    import numpy
    
    coin_sound = generate_coin_sound()
    level_complete_sound = generate_level_complete_sound()
    jump_sound = generate_jump_sound()
    explosion_sound = generate_explosion_sound()
    
    print("Successfully generated synthesized sounds")
except ImportError:
    print("Warning: NumPy not available for sound synthesis. Installing fallback sounds...")
    # Fallback to simple tones without numpy
    try:
        coin_sound = generate_tone(523, 0.2, volume=0.3)  # C5 note
        level_complete_sound = generate_tone(659, 0.5, volume=0.5)  # E5 note
        jump_sound = generate_tone(300, 0.1, volume=0.2)  # Lower tone
        explosion_sound = generate_tone(100, 0.3, volume=0.8)  # Low rumble
        print("Using simple tone fallbacks")
    except Exception as e:
        print(f"Warning: Could not generate sounds: {e}")
        print("Game will run without sound.")
        # Create dummy sound objects that do nothing when played
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
        
        coin_sound = DummySound()
        level_complete_sound = DummySound()
        jump_sound = DummySound()
        explosion_sound = DummySound()
except Exception as e:
    print(f"Warning: Sound synthesis failed: {e}")
    print("Game will run without sound.")
    # Create dummy sound objects that do nothing when played
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    coin_sound = DummySound()
    level_complete_sound = DummySound()
    jump_sound = DummySound()
    explosion_sound = DummySound()

# Add these constants for the night sky
NIGHT_SKY = (25, 25, 50)  # Dark blue for night sky
STAR_COLOR = (255, 255, 200)  # Yellowish white for stars

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
        self.happy_face = False  # New attribute to track if player should show happy face
        self.is_dying = False
        self.death_timer = 0
        self.death_particles = []
        self.death_sound_played = False
        self.death_phase = 0  # 0: surprised, 1: move to center, 2: explode
        self.death_center_x = 0  # Target x position for center movement
        self.death_center_y = 0  # Target y position for center movement
        self.surprised_face = False  # For the "OH!" expression
        self.eye_direction = 0  # -1 for left, 0 for center, 1 for right
        
    def update(self, platforms, coins, keys_pressed, other_players=None):
        # If player is in dying animation, update particles and return
        if self.is_dying:
            self.update_death_animation()
            return
            
        # Handle bounce timer
        if self.bounce_timer > 0:
            self.bounce_timer -= 1
            # Force velocity in bounce direction while timer is active
            self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5
            
            # While bouncing, ignore wall contact with the same wall
            self.ignore_wall_contact = True
        else:
            self.ignore_wall_contact = False
        
        # Handle input
        if self.player_num == 1:
            if keys_pressed[pygame.K_a]:
                self.vel_x = -MOVE_SPEED
                self.eye_direction = -1  # Look left
            elif keys_pressed[pygame.K_d]:
                self.vel_x = MOVE_SPEED
                self.eye_direction = 1   # Look right
            else:
                self.vel_x *= FRICTION
                self.eye_direction = 0   # Look center when not moving
                
            # Check if player can jump
            can_normal_jump = self.on_ground or self.standing_on_player
            can_do_wall_jump = self.can_wall_jump
            
            if keys_pressed[pygame.K_w] and self.bounce_timer <= 0 and (can_normal_jump or can_do_wall_jump):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
                
                if self.can_wall_jump:
                    # Apply horizontal bounce away from wall
                    self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5
                    self.can_wall_jump = False  # Use up the wall jump
                    # Briefly prevent player from overriding the bounce direction
                    self.bounce_timer = 10
                
                jump_sound.play()  # Play jump sound
                
        elif self.player_num == 2:
            if keys_pressed[pygame.K_LEFT]:
                self.vel_x = -MOVE_SPEED
                self.eye_direction = -1  # Look left
            elif keys_pressed[pygame.K_RIGHT]:
                self.vel_x = MOVE_SPEED
                self.eye_direction = 1   # Look right
            else:
                self.vel_x *= FRICTION
                self.eye_direction = 0   # Look center when not moving
                
            # Check if player can jump
            can_normal_jump = self.on_ground or self.standing_on_player
            can_do_wall_jump = self.can_wall_jump
            
            if keys_pressed[pygame.K_UP] and self.bounce_timer <= 0 and (can_normal_jump or can_do_wall_jump):
                self.vel_y = JUMP_STRENGTH
                self.is_jumping = True
                
                if self.can_wall_jump:
                    # Apply horizontal bounce away from wall
                    self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5
                    self.can_wall_jump = False  # Use up the wall jump
                    # Briefly prevent player from overriding the bounce direction
                    self.bounce_timer = 10
                
                jump_sound.play()  # Play jump sound
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Remove wall sliding - players now fall at normal speed when touching walls
        # if self.touching_wall and self.vel_y > 0 and not self.on_ground:
        #     self.vel_y = self.wall_slide_speed
        
        # Move horizontally
        self.rect.x += int(self.vel_x)
        
        # Check for horizontal collisions with platforms
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
        
        # Check for horizontal collisions with other players
        if other_players:
            for other in other_players:
                if self.rect.colliderect(other.rect):
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = other.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = other.rect.right
                    self.vel_x = 0
        
        # Enable wall jump if touching a wall and not on ground
        if self.touching_wall and not self.on_ground and current_wall_id != self.last_wall_id:
            self.can_wall_jump = True
            self.last_wall_id = current_wall_id  # Remember this wall
        
        # Move vertically
        self.rect.y += int(self.vel_y)
        
        # Check for vertical collisions with platforms
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
        
        # Check for vertical collisions with other players
        if other_players:
            for other in other_players:
                if self.rect.colliderect(other.rect):
                    if self.vel_y > 0:  # Falling onto other player
                        self.rect.bottom = other.rect.top
                        self.standing_on_player = True
                        self.vel_y = 0
                    elif self.vel_y < 0:  # Jumping into other player from below
                        self.rect.top = other.rect.bottom
                        self.vel_y = 0
        
        # Check if standing on another player (separate check for when already positioned)
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
        
        # Check if player has fallen off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.start_death_animation()
            return
        
    def start_death_animation(self):
        self.is_dying = True
        self.death_timer = 90  # Longer animation (1.5 seconds)
        self.death_particles = []
        self.death_sound_played = False
        self.death_phase = 0  # Start with surprised face
        self.surprised_face = True
        
        # Set target position (straight up from current position)
        self.death_center_x = self.rect.centerx  # Keep same X position
        self.death_center_y = SCREEN_HEIGHT // 3  # Go up to 1/3 of screen height
        
        # Play explosion sound at higher volume
        explosion_sound.set_volume(1.0)  # Ensure maximum volume
        explosion_sound.play()
    
    def update_death_animation(self):
        # Update death animation phases
        if self.death_phase == 0:  # Surprised face phase
            if self.death_timer <= 75:  # After 15 frames (0.25 seconds)
                self.death_phase = 1  # Move upward phase
        
        elif self.death_phase == 1:  # Move upward phase
            # Calculate distance to target height
            dy = self.death_center_y - self.rect.centery
            
            # Apply upward movement (faster at first, then slowing)
            move_speed = abs(dy) * 0.15  # Move 15% of remaining distance each frame
            if move_speed < 3 and dy < 0:  # Minimum speed when moving up
                move_speed = 3
            
            # Only move if we haven't reached the target
            if abs(dy) > 5:
                self.rect.y += int(dy * move_speed / abs(dy))
            
            # When close to target height, start growth phase
            if abs(dy) < 20:
                self.death_phase = 2  # Growth phase
        
        elif self.death_phase == 2:  # Growth phase
            # Calculate growth factor (from 1x to 3x over 30 frames) - much smaller expansion
            remaining_growth_time = max(0, self.death_timer - 15)  # Last 15 frames reserved for explosion
            if remaining_growth_time > 0:
                # Grow from 1x to 3x size (much more reasonable)
                growth_progress = (30 - remaining_growth_time) / 30
                growth_factor = 1 + 2 * growth_progress  # 1 to 3 instead of 1 to 20
                
                # Store original center for consistent positioning
                center_x = self.rect.centerx
                center_y = self.rect.centery
                
                # Update rectangle size while keeping center position
                new_width = int(40 * growth_factor)
                new_height = int(40 * growth_factor)
                self.rect.width = new_width
                self.rect.height = new_height
                self.rect.centerx = center_x
                self.rect.centery = center_y
                
                # If we've reached near maximum size, create explosion
                if growth_factor >= 2.8:
                    # Create explosion particles
                    for _ in range(80):  # Fewer particles for smaller explosion
                        particle = ExplosionParticle(self.rect.centerx, self.rect.centery)
                        # Smaller explosion
                        particle.size = random.randint(3, 8)  # Smaller particles
                        particle.vel_x = random.uniform(-10, 10)  # Moderate speed particles
                        particle.vel_y = random.uniform(-10, 10)  # Particles in all directions
                        self.death_particles.append(particle)
                    
                    # Play explosion sound again for the final explosion
                    explosion_sound.play()
                    
                    # White flash effect
                    self.death_phase = 3  # White flash and explosion phase
                    self.white_flash_timer = 10  # Flash for 10 frames
        
        elif self.death_phase == 3:  # White flash and explosion phase
            # Decrement white flash timer
            if hasattr(self, 'white_flash_timer'):
                self.white_flash_timer -= 1
        
        # Update all particles
        for particle in self.death_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.death_particles.remove(particle)
        
        # Decrement timer
        self.death_timer -= 1
        
        # When animation is complete, respawn
        if self.death_timer <= 0:
            self.is_dying = False
            self.surprised_face = False
            # Reset size before respawning
            self.rect.width = 40
            self.rect.height = 40
            self.respawn()
    
    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vel_x = 0
        self.vel_y = 0
        self.last_wall_id = None
        self.can_wall_jump = False    # Reset can_wall_jump on respawn
        
    def draw(self, screen):
        # If in white flash phase, draw a fading white overlay
        if self.is_dying and self.death_phase == 3 and hasattr(self, 'white_flash_timer') and self.white_flash_timer > 0:
            # Create a white surface with alpha for the flash
            flash_alpha = min(200, self.white_flash_timer * 25)  # Max 200 alpha, fading out
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, flash_alpha))
            screen.blit(flash_surface, (0, 0))
        
        if self.is_dying:
            if self.death_phase < 3 and self.death_timer > 15:  # Still showing player with surprised face
                # Draw player body
                pygame.draw.rect(screen, self.color, self.rect)
                pygame.draw.rect(screen, BLACK, self.rect, 2)
                
                # Scale eye and mouth sizes based on player size
                scale_factor = self.rect.width / 40
                
                # Draw surprised eyes (bigger)
                eye_size = int(10 * scale_factor)
                left_eye_x = self.rect.left + int(12 * scale_factor)
                right_eye_x = self.rect.right - int(12 * scale_factor)
                eye_y = self.rect.top + int(15 * scale_factor)
                
                pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_size)
                pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_size)
                
                # Draw surprised pupils (smaller)
                pupil_size = int(3 * scale_factor)
                pygame.draw.circle(screen, BLACK, (left_eye_x, eye_y), pupil_size)
                pygame.draw.circle(screen, BLACK, (right_eye_x, eye_y), pupil_size)
                
                # Draw surprised "O" mouth (larger circle)
                mouth_size = int(8 * scale_factor)
                mouth_y = self.rect.top + int(28 * scale_factor)
                
                # Draw a filled black circle for the mouth - keep it black inside
                pygame.draw.circle(screen, BLACK, (self.rect.centerx, mouth_y), mouth_size)
            
            # Draw explosion particles
            for particle in self.death_particles:
                particle.draw(screen)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            
            # Draw eyes
            eye_size = 8
            left_eye_center = (self.rect.left + 12, self.rect.top + 15)
            right_eye_center = (self.rect.right - 12, self.rect.top + 15)
            pygame.draw.circle(screen, WHITE, left_eye_center, eye_size)
            pygame.draw.circle(screen, WHITE, right_eye_center, eye_size)
            
            # Draw pupils with directional movement
            pupil_size = 4
            pupil_offset = 2  # How far pupils move from center
            
            # Calculate pupil positions based on eye direction
            if self.eye_direction == -1:  # Looking left
                left_pupil_pos = (left_eye_center[0] - pupil_offset, left_eye_center[1])
                right_pupil_pos = (right_eye_center[0] - pupil_offset, right_eye_center[1])
            elif self.eye_direction == 1:  # Looking right
                left_pupil_pos = (left_eye_center[0] + pupil_offset, left_eye_center[1])
                right_pupil_pos = (right_eye_center[0] + pupil_offset, right_eye_center[1])
            else:  # Looking center
                left_pupil_pos = left_eye_center
                right_pupil_pos = right_eye_center
            
            pygame.draw.circle(screen, BLACK, left_pupil_pos, pupil_size)
            pygame.draw.circle(screen, BLACK, right_pupil_pos, pupil_size)
            
            # Draw mouth - happy face if all coins collected, normal face otherwise
            mouth_y = self.rect.top + 28
            if self.happy_face:
                # Draw happy mouth (smile)
                pygame.draw.arc(screen, BLACK, (self.rect.left + 10, mouth_y - 5, 20, 15), math.pi, 2*math.pi, 2)
            else:
                # Draw normal mouth (straight line)
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
    def __init__(self, x, y, is_door=False):
        self.rect = pygame.Rect(x, y, 60, 80)
        self.color = GREEN
        self.is_door = is_door  # Flag to determine if this is a door or flag
        self.door_open = False  # Track if door is open
    
    def draw(self, screen):
        if self.is_door:
            # Draw door
            door_width = 60
            door_height = 80
            
            if self.door_open:
                # Draw open door (door frame only)
                pygame.draw.rect(screen, BROWN, (self.rect.x, self.rect.y, door_width, door_height), 5)
                # Draw open door (showing passage)
                pygame.draw.rect(screen, BLACK, (self.rect.x + 5, self.rect.y + 5, door_width - 10, door_height - 10))
                # Add some light effect to show it's open
                pygame.draw.polygon(screen, (255, 255, 200), [
                    (self.rect.x + 10, self.rect.y + 10),
                    (self.rect.x + door_width - 10, self.rect.y + 10),
                    (self.rect.x + door_width//2, self.rect.y + door_height//2)
                ])
            else:
                # Door frame
                pygame.draw.rect(screen, BROWN, (self.rect.x, self.rect.y, door_width, door_height))
                # Door panel
                pygame.draw.rect(screen, (139, 69, 19), (self.rect.x + 5, self.rect.y + 5, door_width - 10, door_height - 10))
                # Door knob
                pygame.draw.circle(screen, YELLOW, (self.rect.x + door_width - 15, self.rect.y + door_height // 2), 5)
        else:
            # Draw flag pole
            pygame.draw.rect(screen, BROWN, (self.rect.x + 25, self.rect.y, 10, self.rect.height))
            # Draw flag
            pygame.draw.polygon(screen, self.color, [
                (self.rect.x + 35, self.rect.y),
                (self.rect.x + 60, self.rect.y + 20),
                (self.rect.x + 35, self.rect.y + 40)
            ])

class Spike:
    def __init__(self, x, y, width=30, height=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (200, 200, 200)  # Silver/gray color for spikes
    
    def draw(self, screen):
        # Draw the base of the spike
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y + self.rect.height - 5, self.rect.width, 5))
        
        # Draw the triangular spikes
        num_spikes = self.rect.width // 10
        for i in range(num_spikes):
            spike_x = self.rect.x + i * 10 + 5
            pygame.draw.polygon(screen, self.color, [
                (spike_x - 5, self.rect.y + self.rect.height - 5),  # Bottom left
                (spike_x, self.rect.y),                            # Top middle
                (spike_x + 5, self.rect.y + self.rect.height - 5)   # Bottom right
            ])

class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(3, 8)
        self.color = random.choice(EXPLOSION_COLORS)
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(-8, -2)
        self.gravity = 0.2
        self.life = random.randint(20, 40)  # Frames the particle will live
    
    def update(self):
        self.vel_y += self.gravity
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1
        # Fade out by reducing size
        if self.life < 10:
            self.size = max(1, self.size - 0.2)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class LevelManager:
    def __init__(self):
        self.current_world = 1
        self.current_level = 1
        self.max_worlds = 3  # Increase to 3 worlds
        self.max_levels = 3
    
    def get_level(self):
        if self.current_world == 1:
            if self.current_level == 1:
                return create_world1_level_1()
            elif self.current_level == 2:
                return create_world1_level_2()
            elif self.current_level == 3:
                return create_world1_level_3()
        elif self.current_world == 2:
            if self.current_level == 1:
                return create_world2_level_1()
            elif self.current_level == 2:
                return create_world2_level_2()
            elif self.current_level == 3:
                return create_world2_level_3()
        elif self.current_world == 3:  # Add World 3
            if self.current_level == 1:
                return create_world3_level_1()
            elif self.current_level == 2:
                return create_world3_level_2()
            elif self.current_level == 3:
                return create_world3_level_3()
        
        # Default fallback
        return create_world1_level_1()
    
    def next_level(self):
        self.current_level += 1
        if self.current_level > self.max_levels:
            self.current_level = 1
            self.current_world += 1
            if self.current_world > self.max_worlds:
                # All levels complete
                self.current_world = self.max_worlds
                self.current_level = self.max_levels
                return False
        return True
    
    def reset(self):
        self.current_world = 1
        self.current_level = 1

def create_world1_level_1():
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
    
    # Add spikes to level 1 - position them ABOVE the platforms
    spikes = [
        Spike(400, SCREEN_HEIGHT - 55, 100, 15),  # Spikes on the floor
        Spike(700, SCREEN_HEIGHT - 55, 100, 15),  # More spikes on the floor
        Spike(300, SCREEN_HEIGHT - 165, 50, 15),  # Spikes on a platform
        Spike(600, SCREEN_HEIGHT - 265, 50, 15),  # Spikes on another platform
    ]
    
    total_coins = len(coins)  # Count the total coins
    
    return platforms, coins, total_coins, spikes  # Now returning spikes

def create_world1_level_2():
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
    
    return platforms, coins, total_coins, []  # Empty spikes list

def create_world1_level_3():
    platforms = [
        # Floor
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
        
        # Platforms - challenging spiral arrangement
        Platform(100, SCREEN_HEIGHT - 150, 200, 20),
        Platform(400, SCREEN_HEIGHT - 250, 200, 20),
        Platform(100, SCREEN_HEIGHT - 350, 200, 20),
        Platform(400, SCREEN_HEIGHT - 450, 200, 20),
        Platform(100, SCREEN_HEIGHT - 550, 200, 20),
        Platform(400, SCREEN_HEIGHT - 650, 200, 20),
        Platform(100, SCREEN_HEIGHT - 750, 800, 20),  # Top platform with goal
        
        # Add connecting platforms to make level completable
        Platform(300, SCREEN_HEIGHT - 200, 50, 20),  # Bridge
        Platform(300, SCREEN_HEIGHT - 400, 50, 20),  # Bridge
        Platform(300, SCREEN_HEIGHT - 600, 50, 20),  # Bridge
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        Coin(150, SCREEN_HEIGHT - 200),
        Coin(450, SCREEN_HEIGHT - 300),
        Coin(150, SCREEN_HEIGHT - 400),
        Coin(450, SCREEN_HEIGHT - 500),
        Coin(150, SCREEN_HEIGHT - 600),
        Coin(450, SCREEN_HEIGHT - 700),
        Coin(250, SCREEN_HEIGHT - 800),
        Coin(550, SCREEN_HEIGHT - 800),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, []  # Empty spikes list

def create_world2_level_1():
    platforms = [
        # Floor with gaps
        Platform(0, SCREEN_HEIGHT - 40, 300, 40),
        Platform(500, SCREEN_HEIGHT - 40, 300, 40),
        Platform(900, SCREEN_HEIGHT - 40, 200, 40),
        
        # Moving platforms pattern
        Platform(100, SCREEN_HEIGHT - 150, 150, 20),
        Platform(350, SCREEN_HEIGHT - 200, 150, 20),
        Platform(600, SCREEN_HEIGHT - 250, 150, 20),
        Platform(850, SCREEN_HEIGHT - 300, 150, 20),
        
        # Upper level
        Platform(600, SCREEN_HEIGHT - 400, 400, 20),
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        Coin(150, SCREEN_HEIGHT - 200),
        Coin(400, SCREEN_HEIGHT - 250),
        Coin(650, SCREEN_HEIGHT - 300),
        Coin(900, SCREEN_HEIGHT - 350),
        Coin(700, SCREEN_HEIGHT - 450),
        Coin(900, SCREEN_HEIGHT - 450),
    ]
    
    # Add spikes in the gaps
    spikes = [
        Spike(300, SCREEN_HEIGHT - 40, 200),  # Spike in first gap
        Spike(800, SCREEN_HEIGHT - 40, 100),  # Spike in second gap
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def create_world2_level_2():
    platforms = [
        # Floor with gaps
        Platform(0, SCREEN_HEIGHT - 40, 200, 40),
        Platform(400, SCREEN_HEIGHT - 40, 200, 40),
        Platform(800, SCREEN_HEIGHT - 40, 200, 40),
        
        # Lower section - more accessible platforms
        Platform(150, SCREEN_HEIGHT - 150, 150, 20),  # Wider platform
        Platform(350, SCREEN_HEIGHT - 200, 150, 20),  # Wider platform
        Platform(550, SCREEN_HEIGHT - 250, 150, 20),  # Wider platform
        Platform(750, SCREEN_HEIGHT - 300, 150, 20),  # Wider platform
        
        # Middle section - wall jump challenge with more forgiving spacing
        Platform(200, SCREEN_HEIGHT - 350, 20, 150),  # Taller vertical wall
        Platform(400, SCREEN_HEIGHT - 400, 20, 150),  # Taller vertical wall
        Platform(600, SCREEN_HEIGHT - 450, 20, 150),  # Taller vertical wall
        Platform(800, SCREEN_HEIGHT - 500, 20, 150),  # Taller vertical wall
        
        # Additional platforms to help with wall jumps
        Platform(250, SCREEN_HEIGHT - 350, 100, 20),  # Helper platform
        Platform(450, SCREEN_HEIGHT - 400, 100, 20),  # Helper platform
        Platform(650, SCREEN_HEIGHT - 450, 100, 20),  # Helper platform
        
        # Upper platforms
        Platform(100, SCREEN_HEIGHT - 450, 150, 20),
        Platform(300, SCREEN_HEIGHT - 500, 150, 20),
        Platform(500, SCREEN_HEIGHT - 550, 150, 20),
        Platform(700, SCREEN_HEIGHT - 600, 300, 20),  # Final platform with goal
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        # Lower section coins
        Coin(175, SCREEN_HEIGHT - 200),
        Coin(375, SCREEN_HEIGHT - 250),
        Coin(575, SCREEN_HEIGHT - 300),
        Coin(775, SCREEN_HEIGHT - 350),
        
        # Middle section coins - more accessible
        Coin(300, SCREEN_HEIGHT - 400),
        Coin(500, SCREEN_HEIGHT - 450),
        Coin(700, SCREEN_HEIGHT - 500),
        
        # Upper section coins
        Coin(150, SCREEN_HEIGHT - 500),
        Coin(350, SCREEN_HEIGHT - 550),
        Coin(550, SCREEN_HEIGHT - 600),
        Coin(800, SCREEN_HEIGHT - 650),  # Coin on the final platform
    ]
    
    # Fewer spikes to make it more beatable
    spikes = [
        # Spikes on the floor between gaps - narrower to allow more room for error
        Spike(250, SCREEN_HEIGHT - 40, 100),  # Between first and second floor platforms
        Spike(650, SCREEN_HEIGHT - 40, 100),  # Between second and third floor platforms
        
        # Only a few strategic spikes on platforms
        Spike(200, SCREEN_HEIGHT - 150 - 15, 30),  # On first platform, smaller
        Spike(600, SCREEN_HEIGHT - 250 - 15, 30),  # On third platform, smaller
        
        # Just one spike on upper platforms
        Spike(350, SCREEN_HEIGHT - 500 - 15, 30),  # On second upper platform, smaller
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def create_world2_level_3():
    platforms = [
        # Floor with very large gaps
        Platform(0, SCREEN_HEIGHT - 40, 150, 40),
        Platform(350, SCREEN_HEIGHT - 40, 150, 40),
        Platform(700, SCREEN_HEIGHT - 40, 150, 40),
        
        # Wall jump maze
        Platform(150, SCREEN_HEIGHT - 200, 20, 160),  # Vertical wall
        Platform(170, SCREEN_HEIGHT - 200, 150, 20),
        Platform(500, SCREEN_HEIGHT - 200, 20, 160),  # Vertical wall
        Platform(350, SCREEN_HEIGHT - 200, 150, 20),
        Platform(850, SCREEN_HEIGHT - 200, 20, 160),  # Vertical wall
        Platform(700, SCREEN_HEIGHT - 200, 150, 20),
        
        # Middle section
        Platform(250, SCREEN_HEIGHT - 350, 150, 20),
        Platform(600, SCREEN_HEIGHT - 350, 150, 20),
        Platform(400, SCREEN_HEIGHT - 450, 200, 20),
        
        # Upper section
        Platform(200, SCREEN_HEIGHT - 550, 150, 20),
        Platform(650, SCREEN_HEIGHT - 550, 150, 20),
        Platform(350, SCREEN_HEIGHT - 650, 300, 20),  # Top platform with goal
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        Coin(250, SCREEN_HEIGHT - 250),
        Coin(450, SCREEN_HEIGHT - 250),
        Coin(750, SCREEN_HEIGHT - 250),
        Coin(300, SCREEN_HEIGHT - 400),
        Coin(700, SCREEN_HEIGHT - 400),
        Coin(500, SCREEN_HEIGHT - 500),
        Coin(250, SCREEN_HEIGHT - 600),
        Coin(700, SCREEN_HEIGHT - 600),
        Coin(500, SCREEN_HEIGHT - 700),
    ]
    
    # Add spikes in strategic locations
    spikes = [
        Spike(150, SCREEN_HEIGHT - 40, 200),  # Between floor platforms
        Spike(500, SCREEN_HEIGHT - 40, 200),  # Between floor platforms
        Spike(400, SCREEN_HEIGHT - 450 - 15, 50),  # On middle platform
        Spike(400, SCREEN_HEIGHT - 650 - 15, 50),  # On top platform
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def create_world3_level_1():
    platforms = [
        # Floor
        Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
        
        # Floating platforms
        Platform(200, SCREEN_HEIGHT - 150, 200, 20),
        Platform(500, SCREEN_HEIGHT - 250, 200, 20),
        Platform(800, SCREEN_HEIGHT - 350, 200, 20),
        
        # Upper platforms
        Platform(300, SCREEN_HEIGHT - 450, 200, 20),
        Platform(600, SCREEN_HEIGHT - 550, 400, 20),
    ]
    
    coins = [
        Coin(300, SCREEN_HEIGHT - 200),
        Coin(600, SCREEN_HEIGHT - 300),
        Coin(900, SCREEN_HEIGHT - 400),
        Coin(400, SCREEN_HEIGHT - 500),
        Coin(700, SCREEN_HEIGHT - 600),
        Coin(900, SCREEN_HEIGHT - 600),
    ]
    
    spikes = [
        Spike(400, SCREEN_HEIGHT - 150 - 15, 50),
        Spike(700, SCREEN_HEIGHT - 250 - 15, 50),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def create_world3_level_2():
    platforms = [
        # Floor with gaps
        Platform(0, SCREEN_HEIGHT - 40, 300, 40),
        Platform(500, SCREEN_HEIGHT - 40, 300, 40),
        Platform(900, SCREEN_HEIGHT - 40, 300, 40),
        
        # Middle platforms
        Platform(200, SCREEN_HEIGHT - 200, 150, 20),
        Platform(450, SCREEN_HEIGHT - 300, 150, 20),
        Platform(700, SCREEN_HEIGHT - 400, 150, 20),
        
        # Upper platforms
        Platform(300, SCREEN_HEIGHT - 500, 200, 20),
        Platform(600, SCREEN_HEIGHT - 600, 400, 20),
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT - 40),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
    ]
    
    coins = [
        Coin(250, SCREEN_HEIGHT - 250),
        Coin(500, SCREEN_HEIGHT - 350),
        Coin(750, SCREEN_HEIGHT - 450),
        Coin(400, SCREEN_HEIGHT - 550),
        Coin(700, SCREEN_HEIGHT - 650),
        Coin(900, SCREEN_HEIGHT - 650),
    ]
    
    spikes = [
        Spike(300, SCREEN_HEIGHT - 40, 200),
        Spike(800, SCREEN_HEIGHT - 40, 100),
        Spike(350, SCREEN_HEIGHT - 200 - 15, 50),
        Spike(600, SCREEN_HEIGHT - 300 - 15, 50),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def create_world3_level_3():
    # Create a maze-like final challenge level
    platforms = [
        # Starting area - small isolated platform
        Platform(50, SCREEN_HEIGHT - 40, 100, 40),
        
        # First challenge - floating islands with large gaps
        Platform(250, SCREEN_HEIGHT - 120, 80, 20),
        Platform(450, SCREEN_HEIGHT - 180, 80, 20),
        Platform(650, SCREEN_HEIGHT - 240, 80, 20),
        Platform(850, SCREEN_HEIGHT - 300, 80, 20),
        
        # Second challenge - moving upward with wall jumps
        Platform(100, SCREEN_HEIGHT - 350, 20, 200),  # Left wall
        Platform(300, SCREEN_HEIGHT - 350, 20, 200),  # Right wall
        Platform(100, SCREEN_HEIGHT - 350, 220, 20),  # Top connector
        
        # Third challenge - narrow platforms with spikes
        Platform(400, SCREEN_HEIGHT - 400, 40, 20),
        Platform(500, SCREEN_HEIGHT - 450, 40, 20),
        Platform(600, SCREEN_HEIGHT - 500, 40, 20),
        Platform(700, SCREEN_HEIGHT - 550, 40, 20),
        Platform(800, SCREEN_HEIGHT - 600, 40, 20),
        
        # Fourth challenge - zigzag pattern
        Platform(700, SCREEN_HEIGHT - 650, 150, 20),
        Platform(450, SCREEN_HEIGHT - 700, 150, 20),
        Platform(700, SCREEN_HEIGHT - 750, 150, 20),
        Platform(450, SCREEN_HEIGHT - 800, 150, 20),
        
        # Final platform - small and hard to reach
        Platform(300, SCREEN_HEIGHT - 850, 100, 20),
        
        # Walls
        Platform(0, 0, 20, SCREEN_HEIGHT),
        Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT),
        
        # Trap platforms - look normal but have spikes
        Platform(200, SCREEN_HEIGHT - 200, 100, 20),
        Platform(500, SCREEN_HEIGHT - 300, 100, 20),
        Platform(300, SCREEN_HEIGHT - 500, 100, 20),
        Platform(900, SCREEN_HEIGHT - 450, 100, 20),
    ]
    
    coins = [
        # Starting area coin
        Coin(100, SCREEN_HEIGHT - 100),
        
        # Floating islands coins - require precise jumps
        Coin(280, SCREEN_HEIGHT - 170),
        Coin(480, SCREEN_HEIGHT - 230),
        Coin(680, SCREEN_HEIGHT - 290),
        
        # Wall jump area coins
        Coin(200, SCREEN_HEIGHT - 400),
        Coin(150, SCREEN_HEIGHT - 450),
        
        # Narrow platforms coins - high risk, high reward
        Coin(420, SCREEN_HEIGHT - 450),
        Coin(520, SCREEN_HEIGHT - 500),
        Coin(620, SCREEN_HEIGHT - 550),
        Coin(720, SCREEN_HEIGHT - 600),
        
        # Zigzag pattern coins
        Coin(750, SCREEN_HEIGHT - 700),
        Coin(500, SCREEN_HEIGHT - 750),
        Coin(750, SCREEN_HEIGHT - 800),
        
        # Final coin - right before the goal
        Coin(350, SCREEN_HEIGHT - 900),
    ]
    
    # Many strategic spike placements for extreme challenge
    spikes = [
        # Gap between starting platform and first floating island
        Spike(150, SCREEN_HEIGHT - 40, 100),
        
        # Spikes on trap platforms
        Spike(220, SCREEN_HEIGHT - 200 - 15, 60),
        Spike(520, SCREEN_HEIGHT - 300 - 15, 60),
        Spike(320, SCREEN_HEIGHT - 500 - 15, 60),
        Spike(920, SCREEN_HEIGHT - 450 - 15, 60),
        
        # Spikes between narrow platforms
        Spike(440, SCREEN_HEIGHT - 400, 60),
        Spike(540, SCREEN_HEIGHT - 450, 60),
        Spike(640, SCREEN_HEIGHT - 500, 60),
        Spike(740, SCREEN_HEIGHT - 550, 60),
        
        # Spikes on zigzag pattern
        Spike(600, SCREEN_HEIGHT - 650 - 15, 50),
        Spike(550, SCREEN_HEIGHT - 700 - 15, 50),
        Spike(600, SCREEN_HEIGHT - 750 - 15, 50),
        
        # Spike before final platform
        Spike(400, SCREEN_HEIGHT - 850, 50),
    ]
    
    total_coins = len(coins)
    
    return platforms, coins, total_coins, spikes

def update_goal_position(world, level):
    is_door = (level == 3 and world < 3)  # It's a door if it's level 3 and not the last world
    
    if world == 1:
        if level == 1:
            return Goal(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120, is_door=False)
        elif level == 2:
            return Goal(700, SCREEN_HEIGHT - 730, is_door=False)
        elif level == 3:
            return Goal(700, SCREEN_HEIGHT - 830, is_door=is_door)
    elif world == 2:
        if level == 1:
            return Goal(900, SCREEN_HEIGHT - 450, is_door=False)
        elif level == 2:
            return Goal(850, SCREEN_HEIGHT - 680, is_door=False)
        elif level == 3:
            return Goal(500, SCREEN_HEIGHT - 700, is_door=is_door)
    elif world == 3:
        if level == 1:
            return Goal(900, SCREEN_HEIGHT - 600, is_door=False)
        elif level == 2:
            return Goal(900, SCREEN_HEIGHT - 650, is_door=False)
        elif level == 3:
            return Goal(350, SCREEN_HEIGHT - 900, is_door=False)  # Updated position for the final goal

# Create a Star class for the night sky background
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT - 100)  # Keep stars above ground level
        self.size = random.randint(1, 3)
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.brightness = random.uniform(0.5, 1.0)
        self.twinkle_offset = random.uniform(0, 2 * math.pi)
    
    def update(self, time):
        # Make stars twinkle by varying brightness
        self.brightness = 0.5 + 0.5 * math.sin(time * self.twinkle_speed + self.twinkle_offset)
    
    def draw(self, screen):
        # Calculate color based on brightness
        color = (int(STAR_COLOR[0] * self.brightness), 
                 int(STAR_COLOR[1] * self.brightness), 
                 int(STAR_COLOR[2] * self.brightness))
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

def main():
    # Create game objects
    player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, 1)
    player2 = Player(150, SCREEN_HEIGHT - 100, RED, 2)
    
    level_manager = LevelManager()
    platforms, coins, total_coins, spikes = level_manager.get_level()
    
    # Set goal position based on level
    goal = update_goal_position(level_manager.current_world, level_manager.current_level)
    
    # Create stars for night sky (World 2)
    stars = [Star() for _ in range(100)]
    
    running = True
    game_complete = False
    all_levels_complete = False
    time_elapsed = 0  # For star twinkling
    show_spike_message = False
    spike_message_timer = 0
    
    while running:
        time_elapsed += 0.1  # Increment time for animations
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
                    
                    platforms, coins, total_coins, spikes = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_world, level_manager.current_level)  # Update goal position
                    game_complete = False
                elif event.key == pygame.K_n and game_complete and not all_levels_complete:
                    # Next level
                    if level_manager.next_level():
                        player1.respawn()
                        player2.respawn()
                        player1.collected_coins = 0
                        player2.collected_coins = 0
                        platforms, coins, total_coins, spikes = level_manager.get_level()
                        goal = update_goal_position(level_manager.current_world, level_manager.current_level)  # Update goal position
                        game_complete = False
                        
                        # Show world transition message if we just moved to a new world
                        if level_manager.current_level == 1 and level_manager.current_world > 1:
                            # Display world transition message
                            transition_text = font_large.render(f"ENTERING WORLD {level_manager.current_world}!", True, GREEN)
                            transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                            pygame.draw.rect(screen, WHITE, transition_rect.inflate(40, 20))
                            pygame.draw.rect(screen, BLACK, transition_rect.inflate(40, 20), 3)
                            screen.blit(transition_text, transition_rect)
                            
                            # Update display and pause briefly
                            pygame.display.flip()
                            pygame.time.delay(2000)  # 2 second pause
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
                    platforms, coins, total_coins, spikes = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_world, level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
                elif event.key == pygame.K_2:
                    # Switch to level 2
                    level_manager.current_level = 2
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins, total_coins, spikes = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_world, level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
                elif event.key == pygame.K_3:
                    # Switch to level 3
                    level_manager.current_level = 3
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    platforms, coins, total_coins, spikes = level_manager.get_level()
                    goal = update_goal_position(level_manager.current_world, level_manager.current_level)
                    game_complete = False
                    all_levels_complete = False
        
        if not game_complete:
            # Update game objects
            player1.update(platforms, coins, keys_pressed, [player2])
            player2.update(platforms, coins, keys_pressed, [player1])
            
            # Check for spike collisions
            if not player1.is_dying and not player2.is_dying:  # Only check if not already dying
                spike_collision = False
                for spike in spikes:
                    if player1.rect.colliderect(spike.rect) and not player1.is_dying:
                        player1.start_death_animation()
                        spike_collision = True
                        break  # Stop checking after first collision
                
                for spike in spikes:
                    if player2.rect.colliderect(spike.rect) and not player2.is_dying:
                        player2.start_death_animation()
                        spike_collision = True
                        break  # Stop checking after first collision
                
                # Show message if spike collision occurred
                if spike_collision:
                    show_spike_message = True
                    spike_message_timer = 60
            
            for coin in coins:
                coin.update()
            
            # Check win condition
            if (player1.rect.colliderect(goal.rect) and 
                player2.rect.colliderect(goal.rect) and 
                len(coins) == 0):
                game_complete = True
            
            # Update player faces and door based on coin collection
            if len(coins) == 0:
                player1.happy_face = True
                player2.happy_face = True
                if goal.is_door:
                    goal.door_open = True
            else:
                player1.happy_face = False
                player2.happy_face = False
                if goal.is_door:
                    goal.door_open = False
        
        # Draw everything
        if level_manager.current_world == 1:
            screen.fill((135, 206, 235))  # Sky blue for day time (World 1)
        else:
            screen.fill(NIGHT_SKY)  # Dark blue for night time (World 2)
            # Update and draw stars
            for star in stars:
                star.update(time_elapsed)
                star.draw(screen)
        
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
        
        # Draw spikes
        for spike in spikes:
            spike.draw(screen)
        
        # Draw spike message if needed
        if show_spike_message:
            spike_message_timer -= 1
            if spike_message_timer <= 0:
                show_spike_message = False
            
            message_text = font_large.render("DANGER! SPIKES!", True, RED)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            pygame.draw.rect(screen, WHITE, message_rect.inflate(40, 20))
            pygame.draw.rect(screen, BLACK, message_rect.inflate(40, 20), 3)
            screen.blit(message_text, message_rect)
            
            sub_message = font_medium.render("Returning to beginning of world...", True, BLACK)
            sub_rect = sub_message.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(sub_message, sub_rect)
        
        # Draw UI
        collected_coins = player1.collected_coins + player2.collected_coins
        score_text = font_medium.render(f"Coins: {collected_coins}/{total_coins}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Display current world and level
        level_text = font_medium.render(f"World: {level_manager.current_world} Level: {level_manager.current_level}", True, BLACK)
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
                victory_text = font_large.render("ALL WORLDS COMPLETE!", True, GREEN)
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
                pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
                screen.blit(victory_text, victory_rect)
                
                continue_text = font_medium.render("Press R to play again from World 1", True, BLACK)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
                screen.blit(continue_text, continue_rect)
            else:
                # Level complete message
                if level_manager.current_level == 3 and level_manager.current_world < level_manager.max_worlds:
                    # End of world message
                    victory_text = font_large.render(f"WORLD {level_manager.current_world} COMPLETE!", True, GREEN)
                else:
                    # Regular level complete message
                    victory_text = font_large.render(f"WORLD {level_manager.current_world} LEVEL {level_manager.current_level} COMPLETE!", True, GREEN)
                    
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
                pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
                screen.blit(victory_text, victory_rect)
                
                if level_manager.current_level < level_manager.max_levels or level_manager.current_world < level_manager.max_worlds:
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
