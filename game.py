import pygame
import sys
import math
import random
import json
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound playback

# Set up the display
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# You can switch between fullscreen and windowed mode
FULLSCREEN = False  # Changed to False to use windowed mode

if FULLSCREEN:
    try:
        # Try fullscreen first
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print(f"Fullscreen mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    except pygame.error as e:
        print(f"Fullscreen failed: {e}")
        print("Falling back to windowed mode...")
        FULLSCREEN = False
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

print(f"Display mode: {'Fullscreen' if FULLSCREEN else 'Windowed'} - {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
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
    """Generate a pleasant coin collection sound - melodic arpeggio"""
    sample_rate = 22050
    duration = 0.5
    frames = int(duration * sample_rate)
    arr = []
    
    # C major arpeggio: C5 -> E5 -> G5 -> C6
    notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
    note_duration = duration / len(notes)
    
    for i in range(frames):
        t = i / sample_rate
        note_index = min(int(t / note_duration), len(notes) - 1)
        note_t = (t % note_duration) / note_duration
        
        freq = notes[note_index]
        
        # Add harmonics for richer sound
        fundamental = math.sin(2 * math.pi * freq * t)
        harmonic2 = 0.3 * math.sin(2 * math.pi * freq * 2 * t)
        harmonic3 = 0.1 * math.sin(2 * math.pi * freq * 3 * t)
        
        # Bell-like envelope
        envelope = math.exp(-note_t * 3) * math.sin(math.pi * note_t)
        
        wave = 2048 * 0.4 * (fundamental + harmonic2 + harmonic3) * envelope
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_jump_sound():
    """Generate a melodic jump sound - perfect fifth interval"""
    sample_rate = 22050
    duration = 0.25
    frames = int(duration * sample_rate)
    arr = []
    
    # Perfect fifth: C4 to G4 (musical interval)
    start_freq, end_freq = 262, 392  # C4 to G4
    
    for i in range(frames):
        t = i / sample_rate
        progress = t / duration
        
        # Smooth frequency transition using sine curve
        freq_progress = 0.5 * (1 - math.cos(math.pi * progress))
        freq = start_freq + (end_freq - start_freq) * freq_progress
        
        # Add harmonics for richer sound
        fundamental = math.sin(2 * math.pi * freq * t)
        harmonic2 = 0.2 * math.sin(2 * math.pi * freq * 2 * t)
        
        # Musical envelope - attack, sustain, decay
        if progress < 0.1:  # Attack
            envelope = progress / 0.1
        elif progress < 0.7:  # Sustain
            envelope = 1.0
        else:  # Decay
            envelope = (1.0 - progress) / 0.3
        
        wave = 2048 * 0.6 * (fundamental + harmonic2) * envelope
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_level_complete_sound():
    """Generate a melodic victory fanfare - classic video game melody"""
    sample_rate = 22050
    duration = 1.5
    frames = int(duration * sample_rate)
    arr = []
    
    # Classic victory melody: C-C-C-C-G-G-G-G-A-A-A-A-C6
    melody = [
        (523, 0.1), (523, 0.1), (523, 0.1), (523, 0.1),  # C5 x4
        (784, 0.1), (784, 0.1), (784, 0.1), (784, 0.1),  # G5 x4
        (880, 0.15), (880, 0.15), (880, 0.15),           # A5 x3
        (1047, 0.4)                                       # C6 (long)
    ]
    
    current_time = 0
    
    for i in range(frames):
        t = i / sample_rate
        wave = 0
        
        # Find current note
        note_time = 0
        current_note = None
        for note_freq, note_dur in melody:
            if note_time <= t < note_time + note_dur:
                current_note = (note_freq, t - note_time, note_dur)
                break
            note_time += note_dur
        
        if current_note:
            freq, note_t, note_dur = current_note
            
            # Add harmonics for richer sound
            fundamental = math.sin(2 * math.pi * freq * t)
            harmonic2 = 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            harmonic3 = 0.1 * math.sin(2 * math.pi * freq * 3 * t)
            
            # Note envelope
            note_progress = note_t / note_dur
            if note_progress < 0.1:  # Attack
                envelope = note_progress / 0.1
            elif note_progress < 0.8:  # Sustain
                envelope = 1.0
            else:  # Release
                envelope = (1.0 - note_progress) / 0.2
            
            wave = 2048 * 0.4 * (fundamental + harmonic2 + harmonic3) * envelope
        
        arr.append([int(wave), int(wave)])
    
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))

def generate_explosion_sound():
    """Generate a melodic death sound - sad descending melody"""
    sample_rate = 22050
    duration = 1.2
    frames = int(duration * sample_rate)
    arr = []
    
    # Sad, melodic descending phrase - like a "wah wah wah" cartoon death
    # Using a minor scale descent: G5 -> F5 -> Eb5 -> D5 -> C5
    melody = [
        (784, 0.2),   # G5
        (698, 0.2),   # F5  
        (622, 0.2),   # Eb5
        (587, 0.3),   # D5
        (523, 0.3)    # C5 (longer, final note)
    ]
    
    for i in range(frames):
        t = i / sample_rate
        wave = 0
        
        # Find current note
        note_time = 0
        current_note = None
        for note_freq, note_dur in melody:
            if note_time <= t < note_time + note_dur:
                current_note = (note_freq, t - note_time, note_dur)
                break
            note_time += note_dur
        
        if current_note:
            freq, note_t, note_dur = current_note
            note_progress = note_t / note_dur
            
            # Add vibrato for expressive effect
            vibrato_freq = 5  # 5 Hz vibrato
            vibrato_depth = 0.02  # 2% frequency modulation
            freq_with_vibrato = freq * (1 + vibrato_depth * math.sin(2 * math.pi * vibrato_freq * t))
            
            # Generate rich harmonic content
            fundamental = math.sin(2 * math.pi * freq_with_vibrato * t)
            harmonic2 = 0.3 * math.sin(2 * math.pi * freq_with_vibrato * 2 * t)
            harmonic3 = 0.1 * math.sin(2 * math.pi * freq_with_vibrato * 3 * t)
            
            # Sad, droopy envelope - starts strong, fades with a droop
            if note_progress < 0.1:  # Quick attack
                envelope = note_progress / 0.1
            else:  # Sad, drooping decay
                envelope = math.exp(-(note_progress - 0.1) * 2) * (1 - note_progress * 0.3)
            
            # Overall volume that decreases through the phrase
            phrase_progress = t / duration
            overall_volume = (1 - phrase_progress * 0.7)  # Fade to 30% by end
            
            wave = 2048 * 0.5 * (fundamental + harmonic2 + harmonic3) * envelope * overall_volume
        
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

# Game states
GAME_STATE_LEVEL_SELECT = "LEVEL_SELECT"
GAME_STATE_PLAYING = "PLAYING"

def setup_display():
    """Setup display mode (fullscreen or windowed)"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN
    
    if FULLSCREEN:
        try:
            # Get the current display info for fullscreen
            infoObject = pygame.display.Info()
            SCREEN_WIDTH = infoObject.current_w
            SCREEN_HEIGHT = infoObject.current_h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            print(f"Switched to fullscreen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        except pygame.error as e:
            print(f"Fullscreen failed: {e}")
            print("Falling back to windowed mode...")
            FULLSCREEN = False
            SCREEN_WIDTH = 1280
            SCREEN_HEIGHT = 720
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            print(f"Windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Switched to windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

def get_text_color(background_color):
    """
    Determine the best text color (black or white) based on background brightness.
    Uses the luminance formula to calculate brightness.
    """
    if isinstance(background_color, tuple) and len(background_color) >= 3:
        r, g, b = background_color[:3]
    else:
        # Default to black text if we can't determine background
        return BLACK
    
    # Calculate luminance using the standard formula
    # Luminance = 0.299*R + 0.587*G + 0.114*B
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    
    # If background is bright (luminance > 0.5), use black text
    # If background is dark (luminance <= 0.5), use white text
    return BLACK if luminance > 0.5 else WHITE

def get_current_background_color(level_data):
    """Get the current background color based on level data"""
    background_type = level_data.get('background_type', 'day')
    
    if background_type == 'night':
        return NIGHT_SKY  # Dark blue for night time
    else:
        return (135, 206, 235)  # Sky blue for day time

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
        self.levels_dir = "levels"
        self.available_levels = self.scan_available_levels()
        self.max_worlds = max([level['world'] for level in self.available_levels]) if self.available_levels else 1
        self.max_levels = max([level['level'] for level in self.available_levels if level['world'] == self.current_world]) if self.available_levels else 1
    
    def scan_available_levels(self):
        """Scan the levels directory for available JSON level files"""
        levels = []
        if not os.path.exists(self.levels_dir):
            print(f"Warning: {self.levels_dir} directory not found. Creating it...")
            os.makedirs(self.levels_dir)
            return levels
        
        for filename in os.listdir(self.levels_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.levels_dir, filename), 'r') as f:
                        level_data = json.load(f)
                        levels.append({
                            'world': level_data.get('world', 1),
                            'level': level_data.get('level', 1),
                            'filename': filename,
                            'name': level_data.get('name', 'Unnamed Level')
                        })
                except Exception as e:
                    print(f"Error loading level {filename}: {e}")
        
        # Sort levels by world, then by level
        levels.sort(key=lambda x: (x['world'], x['level']))
        return levels
    
    def load_level_from_json(self, world, level):
        """Load a level from JSON file"""
        # Find the level file
        level_file = None
        for level_info in self.available_levels:
            if level_info['world'] == world and level_info['level'] == level:
                level_file = level_info['filename']
                break
        
        if not level_file:
            print(f"Warning: Level {world}-{level} not found. Using fallback.")
            return self.create_fallback_level()
        
        try:
            with open(os.path.join(self.levels_dir, level_file), 'r') as f:
                level_data = json.load(f)
                return self.parse_level_data(level_data)
        except Exception as e:
            print(f"Error loading level {level_file}: {e}")
            return self.create_fallback_level()
    
    def parse_level_data(self, level_data):
        """Parse JSON level data into game objects"""
        platforms = []
        coins = []
        spikes = []
        
        # Create platforms
        for platform_data in level_data.get('platforms', []):
            color = tuple(platform_data.get('color', [139, 69, 19]))
            platform = Platform(
                platform_data['x'],
                platform_data['y'],
                platform_data['width'],
                platform_data['height'],
                color
            )
            platforms.append(platform)
        
        # Create coins
        for coin_data in level_data.get('coins', []):
            coin = Coin(coin_data['x'], coin_data['y'])
            coins.append(coin)
        
        # Create spikes
        for spike_data in level_data.get('spikes', []):
            spike = Spike(
                spike_data['x'],
                spike_data['y'],
                spike_data.get('width', 30),
                spike_data.get('height', 15)
            )
            spikes.append(spike)
        
        total_coins = len(coins)
        
        # Store additional level info
        self.current_level_data = level_data
        
        return platforms, coins, total_coins, spikes
    
    def create_fallback_level(self):
        """Create a simple fallback level if JSON loading fails"""
        platforms = [
            Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
            Platform(200, SCREEN_HEIGHT - 150, 200, 20),
            Platform(0, 0, 20, SCREEN_HEIGHT - 40),
            Platform(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT - 40),
        ]
        coins = [Coin(250, SCREEN_HEIGHT - 200)]
        spikes = []
        return platforms, coins, 1, spikes
    
    def get_level(self):
        return self.load_level_from_json(self.current_world, self.current_level)
    
    def get_current_level_data(self):
        """Get the current level's metadata"""
        return getattr(self, 'current_level_data', {})
    
    def next_level(self):
        # Find next available level
        current_levels_in_world = [l for l in self.available_levels if l['world'] == self.current_world]
        max_level_in_world = max([l['level'] for l in current_levels_in_world]) if current_levels_in_world else 1
        
        self.current_level += 1
        if self.current_level > max_level_in_world:
            self.current_level = 1
            self.current_world += 1
            if self.current_world > self.max_worlds:
                # All levels complete
                self.current_world = self.max_worlds
                self.current_level = max_level_in_world
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

def create_goal_from_level_data(level_manager):
    """Create goal from current level data"""
    level_data = level_manager.get_current_level_data()
    goal_data = level_data.get('goal', {})
    
    x = goal_data.get('x', SCREEN_WIDTH - 100)
    y = goal_data.get('y', SCREEN_HEIGHT - 120)
    is_door = goal_data.get('is_door', False)
    
    return Goal(x, y, is_door)

def update_player_spawn_points(level_manager, player1, player2):
    """Update player spawn coordinates based on current level data"""
    level_data = level_manager.get_current_level_data()
    player_spawns = level_data.get('player_spawns', [
        {'x': 100, 'y': SCREEN_HEIGHT - 100},
        {'x': 150, 'y': SCREEN_HEIGHT - 100}
    ])
    
    player1.spawn_x = player_spawns[0]['x']
    player1.spawn_y = player_spawns[0]['y']
    player2.spawn_x = player_spawns[1]['x']
    player2.spawn_y = player_spawns[1]['y']

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

class LevelPortal:
    def __init__(self, x, y, world, level, portal_type="door"):
        self.rect = pygame.Rect(x, y, 80, 100)
        self.world = world
        self.level = level
        self.portal_type = portal_type  # "door", "pipe", "portal"
        self.is_available = True
        self.glow_time = 0
        self.both_players_touching = False
        
        # Portal-specific colors
        if world == 1:
            self.color = (139, 69, 19)  # Brown for world 1
            self.accent_color = GREEN
        elif world == 2:
            self.color = (75, 75, 75)  # Dark gray for world 2
            self.accent_color = PURPLE
        elif world == 3:
            self.color = (50, 50, 100)  # Dark blue for world 3
            self.accent_color = (255, 215, 0)  # Gold
        else:
            self.color = GRAY
            self.accent_color = WHITE
    
    def update(self, player1, player2):
        # Check if both players are touching this portal
        p1_touching = self.rect.colliderect(player1.rect)
        p2_touching = self.rect.colliderect(player2.rect)
        self.both_players_touching = p1_touching and p2_touching
        
        # Update glow animation
        self.glow_time += 0.1
    
    def draw(self, screen):
        # Calculate glow effect
        glow_alpha = int(128 + 127 * math.sin(self.glow_time))
        
        if self.portal_type == "door":
            # Draw door frame
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 3)
            
            # Draw door panel
            inner_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, 
                                   self.rect.width - 20, self.rect.height - 20)
            pygame.draw.rect(screen, self.accent_color, inner_rect)
            
            # Draw door knob
            knob_x = self.rect.right - 20
            knob_y = self.rect.centery
            pygame.draw.circle(screen, YELLOW, (knob_x, knob_y), 5)
            
            # Draw level number on door
            level_text = font_medium.render(f"{self.level}", True, WHITE)
            text_rect = level_text.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(level_text, text_rect)
            
        elif self.portal_type == "pipe":
            # Draw Mario-style pipe
            # Main pipe body
            pygame.draw.rect(screen, GREEN, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 3)
            
            # Pipe opening at top
            opening_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 10, 
                                     self.rect.width + 10, 20)
            pygame.draw.rect(screen, (0, 150, 0), opening_rect)
            pygame.draw.rect(screen, BLACK, opening_rect, 3)
            
            # Level number
            level_text = font_medium.render(f"{self.level}", True, WHITE)
            text_rect = level_text.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(level_text, text_rect)
            
        elif self.portal_type == "portal":
            # Draw magical portal
            # Outer ring
            pygame.draw.circle(screen, self.accent_color, self.rect.center, 50, 5)
            # Inner swirling effect
            for i in range(3):
                angle = self.glow_time * 2 + i * (2 * math.pi / 3)
                inner_x = self.rect.centerx + 30 * math.cos(angle)
                inner_y = self.rect.centery + 30 * math.sin(angle)
                pygame.draw.circle(screen, self.color, (int(inner_x), int(inner_y)), 8)
            
            # Center portal
            pygame.draw.circle(screen, (0, 0, 0), self.rect.center, 25)
            
            # Level number
            level_text = font_medium.render(f"{self.level}", True, self.accent_color)
            text_rect = level_text.get_rect(center=self.rect.center)
            screen.blit(level_text, text_rect)
        
        # Draw glow effect if both players are touching
        if self.both_players_touching:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*WHITE, glow_alpha//2), 
                           (0, 0, self.rect.width + 20, self.rect.height + 20), 5)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        
        # Draw world label above portal
        world_text = font_small.render(f"World {self.world}", True, WHITE)
        world_rect = world_text.get_rect(center=(self.rect.centerx, self.rect.y - 15))
        screen.blit(world_text, world_rect)

class LevelSelectMap:
    def __init__(self, level_manager):
        self.level_manager = level_manager
        self.platforms = []
        self.portals = []
        self.create_level_select_map()
    
    def create_level_select_map(self):
        # Create the level select map layout
        
        # Ground platforms for each world
        # World 1 area (left side)
        self.platforms.append(Platform(50, SCREEN_HEIGHT - 40, 300, 40, (139, 69, 19)))
        self.platforms.append(Platform(100, SCREEN_HEIGHT - 120, 200, 20, (139, 69, 19)))
        
        # World 2 area (middle, elevated)
        self.platforms.append(Platform(450, SCREEN_HEIGHT - 200, 300, 40, (75, 75, 75)))
        self.platforms.append(Platform(500, SCREEN_HEIGHT - 280, 200, 20, (75, 75, 75)))
        
        # World 3 area (right side, highest)
        self.platforms.append(Platform(850, SCREEN_HEIGHT - 360, 350, 40, (50, 50, 100)))
        self.platforms.append(Platform(900, SCREEN_HEIGHT - 440, 250, 20, (50, 50, 100)))
        
        # Connecting platforms between worlds
        self.platforms.append(Platform(350, SCREEN_HEIGHT - 120, 100, 20, GRAY))  # World 1 to 2
        self.platforms.append(Platform(750, SCREEN_HEIGHT - 280, 100, 20, GRAY))  # World 2 to 3
        
        # Create portals for each available level
        available_levels = self.level_manager.available_levels
        
        for level_info in available_levels:
            world = level_info['world']
            level = level_info['level']
            
            if world == 1:
                # World 1 portals on lower platform
                x = 120 + (level - 1) * 90
                y = SCREEN_HEIGHT - 220
                portal_type = "door"
            elif world == 2:
                # World 2 portals on middle platform  
                x = 520 + (level - 1) * 90
                y = SCREEN_HEIGHT - 380
                portal_type = "pipe"
            elif world == 3:
                # World 3 portals on upper platform
                x = 920 + (level - 1) * 90
                y = SCREEN_HEIGHT - 540
                portal_type = "portal"
            else:
                continue
                
            portal = LevelPortal(x, y, world, level, portal_type)
            self.portals.append(portal)
        
        # Add some decorative elements
        # World 1: Normal grass and trees
        self.platforms.append(Platform(80, SCREEN_HEIGHT - 60, 20, 20, GREEN))  # Grass block
        self.platforms.append(Platform(280, SCREEN_HEIGHT - 60, 20, 20, GREEN))  # Grass block
        
        # World 2: Dark/spiky decorations
        self.platforms.append(Platform(480, SCREEN_HEIGHT - 220, 20, 20, (50, 50, 50)))  # Dark block
        self.platforms.append(Platform(680, SCREEN_HEIGHT - 220, 20, 20, (50, 50, 50)))  # Dark block
        
        # World 3: Floating magical platforms
        self.platforms.append(Platform(880, SCREEN_HEIGHT - 380, 20, 20, (100, 50, 150)))  # Magic block
        self.platforms.append(Platform(1180, SCREEN_HEIGHT - 380, 20, 20, (100, 50, 150)))  # Magic block
    
    def update(self, player1, player2):
        # Update all portals
        for portal in self.portals:
            portal.update(player1, player2)
    
    def check_portal_activation(self, player1, player2):
        # Check if players want to enter a portal
        for portal in self.portals:
            if portal.both_players_touching:
                return portal.world, portal.level
        return None, None
    
    def draw(self, screen):
        # Draw gradient sky background for level select
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(135 * (1 - ratio) + 100 * ratio)
            g = int(206 * (1 - ratio) + 150 * ratio)
            b = int(235 * (1 - ratio) + 200 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(screen)
        
        # Draw portals
        for portal in self.portals:
            portal.draw(screen)
        
        # Draw world area labels
        world1_text = font_large.render("WORLD 1", True, (139, 69, 19))
        world1_rect = world1_text.get_rect(center=(200, SCREEN_HEIGHT - 300))
        screen.blit(world1_text, world1_rect)
        
        world2_text = font_large.render("WORLD 2", True, (75, 75, 75))
        world2_rect = world2_text.get_rect(center=(600, SCREEN_HEIGHT - 460))
        screen.blit(world2_text, world2_rect)
        
        world3_text = font_large.render("WORLD 3", True, (50, 50, 100))
        world3_rect = world3_text.get_rect(center=(1025, SCREEN_HEIGHT - 620))
        screen.blit(world3_text, world3_rect)
        
        # Draw title
        title_text = font_large.render("LEVEL SELECT", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        # Add background for title
        pygame.draw.rect(screen, WHITE, title_rect.inflate(40, 20))
        pygame.draw.rect(screen, BLACK, title_rect.inflate(40, 20), 3)
        screen.blit(title_text, title_rect)
        
        # Draw instructions
        instruction_text = font_medium.render("Walk both players to a level entrance and press SPACE to enter!", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        pygame.draw.rect(screen, WHITE, instruction_rect.inflate(20, 10))
        screen.blit(instruction_text, instruction_rect)

def main():
    level_manager = LevelManager()
    
    # Initialize game state
    game_state = GAME_STATE_LEVEL_SELECT
    
    # Create level select map
    level_select_map = LevelSelectMap(level_manager)
    
    # Create players for level select (start in World 1 area)
    player1 = Player(150, SCREEN_HEIGHT - 100, BLUE, 1)
    player2 = Player(200, SCREEN_HEIGHT - 100, RED, 2)
    
    # Game state variables
    platforms = []
    coins = []
    total_coins = 0
    spikes = []
    goal = None
    
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
                    if game_state == GAME_STATE_PLAYING:
                        # Return to level select
                        game_state = GAME_STATE_LEVEL_SELECT
                        player1.rect.x = 150
                        player1.rect.y = SCREEN_HEIGHT - 100
                        player2.rect.x = 200 
                        player2.rect.y = SCREEN_HEIGHT - 100
                        player1.vel_x = 0
                        player1.vel_y = 0
                        player2.vel_x = 0
                        player2.vel_y = 0
                        player1.collected_coins = 0
                        player2.collected_coins = 0
                    else:
                        running = False
                elif event.key == pygame.K_SPACE:
                    if game_state == GAME_STATE_LEVEL_SELECT:
                        # Check if players want to enter a portal
                        target_world, target_level = level_select_map.check_portal_activation(player1, player2)
                        if target_world and target_level:
                            # Enter the selected level
                            level_manager.current_world = target_world
                            level_manager.current_level = target_level
                            platforms, coins, total_coins, spikes = level_manager.get_level()
                            goal = create_goal_from_level_data(level_manager)
                            
                            # Get player spawn positions from level data
                            level_data = level_manager.get_current_level_data()
                            player_spawns = level_data.get('player_spawns', [
                                {'x': 100, 'y': SCREEN_HEIGHT - 100},
                                {'x': 150, 'y': SCREEN_HEIGHT - 100}
                            ])
                            
                            # Reset players to level spawn positions
                            player1.rect.x = player_spawns[0]['x']
                            player1.rect.y = player_spawns[0]['y']
                            player2.rect.x = player_spawns[1]['x']
                            player2.rect.y = player_spawns[1]['y']
                            # Update spawn coordinates so respawn works correctly
                            player1.spawn_x = player_spawns[0]['x']
                            player1.spawn_y = player_spawns[0]['y']
                            player2.spawn_x = player_spawns[1]['x']
                            player2.spawn_y = player_spawns[1]['y']
                            player1.vel_x = 0
                            player1.vel_y = 0
                            player2.vel_x = 0
                            player2.vel_y = 0
                            player1.collected_coins = 0
                            player2.collected_coins = 0
                            player1.is_dying = False
                            player2.is_dying = False
                            
                            game_state = GAME_STATE_PLAYING
                            game_complete = False
                            
                            # Play jump sound for level entry
                            jump_sound.play()
                elif event.key == pygame.K_r and game_state == GAME_STATE_PLAYING:
                    # Reset current level
                    if all_levels_complete:
                        level_manager.reset()
                        all_levels_complete = False
                    
                    platforms, coins, total_coins, spikes = level_manager.get_level()
                    goal = create_goal_from_level_data(level_manager)
                    
                    # Update spawn points before respawning
                    update_player_spawn_points(level_manager, player1, player2)
                    player1.respawn()
                    player2.respawn()
                    player1.collected_coins = 0
                    player2.collected_coins = 0
                    game_complete = False
                elif event.key == pygame.K_n and game_complete and not all_levels_complete and game_state == GAME_STATE_PLAYING:
                    # Next level
                    if level_manager.next_level():
                        platforms, coins, total_coins, spikes = level_manager.get_level()
                        goal = create_goal_from_level_data(level_manager)
                        
                        # Update spawn points before respawning
                        update_player_spawn_points(level_manager, player1, player2)
                        player1.respawn()
                        player2.respawn()
                        player1.collected_coins = 0
                        player2.collected_coins = 0
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
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    global FULLSCREEN
                    FULLSCREEN = not FULLSCREEN
                    setup_display()
        
        # Update game logic based on current state
        if game_state == GAME_STATE_LEVEL_SELECT:
            # Update level select map
            level_select_map.update(player1, player2)
            
            # Update players in level select (they use level select platforms)
            player1.update(level_select_map.platforms, [], keys_pressed, [player2])
            player2.update(level_select_map.platforms, [], keys_pressed, [player1])
            
        elif game_state == GAME_STATE_PLAYING and not game_complete:
            # Update game objects in playing state
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
            if (goal and player1.rect.colliderect(goal.rect) and 
                player2.rect.colliderect(goal.rect) and 
                len(coins) == 0):
                game_complete = True
            
            # Update player faces and door based on coin collection
            if len(coins) == 0:
                player1.happy_face = True
                player2.happy_face = True
                if goal and goal.is_door:
                    goal.door_open = True
            else:
                player1.happy_face = False
                player2.happy_face = False
                if goal and goal.is_door:
                    goal.door_open = False
        
        # Draw everything to screen based on current state
        if game_state == GAME_STATE_LEVEL_SELECT:
            # Draw level select screen
            level_select_map.draw(screen)
            
            # Draw players
            player1.draw(screen)
            player2.draw(screen)
            
            # Draw additional UI for level select
            controls_text = font_small.render("Player 1: WASD | Player 2: Arrow Keys | Both players on portal + SPACE to enter", True, BLACK)
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
            pygame.draw.rect(screen, WHITE, controls_rect.inflate(20, 10))
            screen.blit(controls_text, controls_rect)
            
            # Show portal entry prompt if both players are on a portal
            target_world, target_level = level_select_map.check_portal_activation(player1, player2)
            if target_world and target_level:
                prompt_text = font_large.render(f"Press SPACE to enter World {target_world} Level {target_level}!", True, GREEN)
                prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.draw.rect(screen, WHITE, prompt_rect.inflate(40, 20))
                pygame.draw.rect(screen, BLACK, prompt_rect.inflate(40, 20), 3)
                screen.blit(prompt_text, prompt_rect)
            
        elif game_state == GAME_STATE_PLAYING:
            # Draw playing state
            level_data = level_manager.get_current_level_data()
            background_type = level_data.get('background_type', 'day')
            background_color = get_current_background_color(level_data)
            text_color = get_text_color(background_color)
            
            if background_type == 'night':
                screen.fill(NIGHT_SKY)  # Dark blue for night time
                # Update and draw stars
                for star in stars:
                    star.update(time_elapsed)
                    star.draw(screen)
            else:
                screen.fill((135, 206, 235))  # Sky blue for day time
            
            # Draw platforms
            for platform in platforms:
                platform.draw(screen)
            
            # Draw coins
            for coin in coins:
                coin.draw(screen)
            
            # Draw goal
            if goal:
                goal.draw(screen)
            
            # Draw players
            player1.draw(screen)
            player2.draw(screen)
            
            # Draw spikes
            for spike in spikes:
                spike.draw(screen)
        
            # Draw spike message if needed (only in playing state)
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
            
            # Draw UI with dynamic text color
            collected_coins = player1.collected_coins + player2.collected_coins
            score_text = font_medium.render(f"Coins: {collected_coins}/{total_coins}", True, text_color)
            screen.blit(score_text, (20, 20))
            
            # Display current world and level with dynamic text color
            level_text = font_medium.render(f"World: {level_manager.current_world} Level: {level_manager.current_level}", True, text_color)
            screen.blit(level_text, (20, 60))
            
            # Draw instructions with dynamic text color
            instructions = [
                "Player 1: WASD to move",
                "Player 2: Arrow keys to move",
                "Players can stand on each other to reach higher platforms!",
                "Jump off walls to reach higher areas!",
                "Collect all coins and reach the flag together!",
                "Press R to restart, ESC to return to level select, F11 for fullscreen"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_text = font_small.render(instruction, True, text_color)
                screen.blit(inst_text, (20, SCREEN_HEIGHT - 120 + i * 18))
            
            # Draw completion messages
            if game_complete:
                if all_levels_complete:
                    # Final victory message
                    victory_text = font_large.render("ALL WORLDS COMPLETE!", True, GREEN)
                    victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    pygame.draw.rect(screen, WHITE, victory_rect.inflate(40, 20))
                    pygame.draw.rect(screen, BLACK, victory_rect.inflate(40, 20), 3)
                    screen.blit(victory_text, victory_rect)
                    
                    continue_text = font_medium.render("Press ESC to return to level select", True, BLACK)
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
                        continue_text = font_medium.render("Press N for next level, R to replay, or ESC for level select", True, BLACK)
                    else:
                        continue_text = font_medium.render("Press N to finish, R to replay, or ESC for level select", True, BLACK)
                        
                    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
                    screen.blit(continue_text, continue_rect)
            
            # Play level complete sound when game is won
            if (goal and player1.rect.colliderect(goal.rect) and 
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
