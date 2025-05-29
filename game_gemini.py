import pygame
import sys
import math
import random
import json
import os
import re # For parsing level filenames

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound playback

# Set up the display
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# You can switch between fullscreen and windowed mode
FULLSCREEN = False

if FULLSCREEN:
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    except pygame.error as e:
        print(f"Fullscreen failed: {e}, falling back to windowed.")
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
EXPLOSION_COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (255, 255, 255)]
NIGHT_SKY = (25, 25, 50)
STAR_COLOR = (255, 255, 200)

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

# Game states
GAME_STATE_LEVEL_SELECT = "LEVEL_SELECT"
GAME_STATE_VERSION_SELECT = "VERSION_SELECT"
GAME_STATE_PLAYING = "PLAYING"

# --- Synthesized sound generation functions ---
def generate_tone(frequency, duration, sample_rate=22050, volume=0.5):
    """Generate a sine wave tone"""
    try:
        import numpy
        frames = int(duration * sample_rate)
        arr = numpy.array([4096 * volume * math.sin(2 * math.pi * frequency * i / sample_rate) for i in range(frames)])
        arr = numpy.column_stack((arr, arr)).astype(numpy.int16) # Stereo
        return pygame.sndarray.make_sound(arr)
    except ImportError:
        print("NumPy not found for generate_tone. Sound will be silent.")
        return DummySound() # Fallback if numpy isn't there for this simple tone too

def generate_coin_sound():
    try:
        import numpy
        sample_rate = 22050; duration = 0.5; frames = int(duration * sample_rate); arr = []
        notes = [523, 659, 784, 1047]; note_duration = duration / len(notes)
        for i in range(frames):
            t = i / sample_rate; note_index = min(int(t / note_duration), len(notes) - 1)
            note_t = (t % note_duration) / note_duration; freq = notes[note_index]
            fundamental = math.sin(2 * math.pi * freq * t)
            harmonic2 = 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            harmonic3 = 0.1 * math.sin(2 * math.pi * freq * 3 * t)
            envelope = math.exp(-note_t * 3) * math.sin(math.pi * note_t)
            wave = 2048 * 0.4 * (fundamental + harmonic2 + harmonic3) * envelope
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))
    except ImportError: return generate_tone(523, 0.2, volume=0.3)

def generate_jump_sound():
    try:
        import numpy
        sample_rate = 22050; duration = 0.25; frames = int(duration * sample_rate); arr = []
        start_freq, end_freq = 262, 392
        for i in range(frames):
            t = i / sample_rate; progress = t / duration
            freq_progress = 0.5 * (1 - math.cos(math.pi * progress))
            freq = start_freq + (end_freq - start_freq) * freq_progress
            fundamental = math.sin(2 * math.pi * freq * t)
            harmonic2 = 0.2 * math.sin(2 * math.pi * freq * 2 * t)
            if progress < 0.1: envelope = progress / 0.1
            elif progress < 0.7: envelope = 1.0
            else: envelope = (1.0 - progress) / 0.3
            wave = 2048 * 0.6 * (fundamental + harmonic2) * envelope
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))
    except ImportError: return generate_tone(300, 0.1, volume=0.2)

def generate_level_complete_sound():
    try:
        import numpy
        sample_rate = 22050; duration = 1.5; frames = int(duration * sample_rate); arr = []
        melody = [(523, 0.1), (523, 0.1), (523, 0.1), (523, 0.1), (784, 0.1), (784, 0.1), (784, 0.1), (784, 0.1), (880, 0.15), (880, 0.15), (880, 0.15), (1047, 0.4)]
        for i in range(frames):
            t = i / sample_rate; wave = 0; note_time = 0; current_note = None
            for note_freq, note_dur in melody:
                if note_time <= t < note_time + note_dur: current_note = (note_freq, t - note_time, note_dur); break
                note_time += note_dur
            if current_note:
                freq, note_t, note_dur = current_note
                fundamental = math.sin(2 * math.pi * freq * t)
                harmonic2 = 0.3 * math.sin(2 * math.pi * freq * 2 * t)
                harmonic3 = 0.1 * math.sin(2 * math.pi * freq * 3 * t)
                note_progress = note_t / note_dur
                if note_progress < 0.1: envelope = note_progress / 0.1
                elif note_progress < 0.8: envelope = 1.0
                else: envelope = (1.0 - note_progress) / 0.2
                wave = 2048 * 0.4 * (fundamental + harmonic2 + harmonic3) * envelope
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))
    except ImportError: return generate_tone(659, 0.5, volume=0.5)

def generate_explosion_sound():
    try:
        import numpy
        sample_rate = 22050; duration = 1.2; frames = int(duration * sample_rate); arr = []
        melody = [(784, 0.2), (698, 0.2), (622, 0.2), (587, 0.3), (523, 0.3)]
        for i in range(frames):
            t = i / sample_rate; wave = 0; note_time = 0; current_note = None
            for note_freq, note_dur in melody:
                if note_time <= t < note_time + note_dur: current_note = (note_freq, t - note_time, note_dur); break
                note_time += note_dur
            if current_note:
                freq, note_t, note_dur = current_note; note_progress = note_t / note_dur
                vibrato_freq = 5; vibrato_depth = 0.02
                freq_with_vibrato = freq * (1 + vibrato_depth * math.sin(2 * math.pi * vibrato_freq * t))
                fundamental = math.sin(2 * math.pi * freq_with_vibrato * t)
                harmonic2 = 0.3 * math.sin(2 * math.pi * freq_with_vibrato * 2 * t)
                harmonic3 = 0.1 * math.sin(2 * math.pi * freq_with_vibrato * 3 * t)
                if note_progress < 0.1: envelope = note_progress / 0.1
                else: envelope = math.exp(-(note_progress - 0.1) * 2) * (1 - note_progress * 0.3)
                phrase_progress = t / duration; overall_volume = (1 - phrase_progress * 0.7)
                wave = 2048 * 0.5 * (fundamental + harmonic2 + harmonic3) * envelope * overall_volume
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16))
    except ImportError: return generate_tone(100, 0.3, volume=0.8)

# DummySound class for fallback
class DummySound:
    def play(self): pass
    def set_volume(self, vol): pass

# Generate sounds
try:
    coin_sound = generate_coin_sound()
    level_complete_sound = generate_level_complete_sound()
    jump_sound = generate_jump_sound()
    explosion_sound = generate_explosion_sound()
    print("Successfully generated synthesized sounds (or using fallbacks).")
except Exception as e:
    print(f"Warning: Sound synthesis failed: {e}. Using DummySounds.")
    coin_sound = DummySound()
    level_complete_sound = DummySound()
    jump_sound = DummySound()
    explosion_sound = DummySound()

# --- Helper functions ---
def setup_display():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN
    infoObject = pygame.display.Info()
    if FULLSCREEN:
        try:
            SCREEN_WIDTH = infoObject.current_w
            SCREEN_HEIGHT = infoObject.current_h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        except pygame.error:
            FULLSCREEN = False # Fallback
    if not FULLSCREEN: # If initially false or fallback
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    print(f"Display updated: {'Fullscreen' if FULLSCREEN else 'Windowed'} - {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

def get_text_color(background_color):
    if isinstance(background_color, tuple) and len(background_color) >= 3:
        r, g, b = background_color[:3]
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        return BLACK if luminance > 0.5 else WHITE
    return BLACK

def get_current_background_color(level_data):
    return NIGHT_SKY if level_data.get('background_type', 'day') == 'night' else (135, 206, 235)

# --- Game Object Classes ---
class Player:
    def __init__(self, x, y, color, player_num):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0; self.vel_y = 0; self.color = color
        self.is_jumping = False; self.on_ground = False; self.player_num = player_num
        self.spawn_x = x; self.spawn_y = y; self.collected_coins = 0
        self.standing_on_player = False; self.touching_wall = False
        self.can_wall_jump = False; self.wall_slide_speed = 2
        self.wall_jump_direction = 0; self.last_wall_id = None
        self.bounce_timer = 0; self.ignore_wall_contact = False
        self.happy_face = False; self.is_dying = False; self.death_timer = 0
        self.death_particles = []; self.death_sound_played = False
        self.death_phase = 0; self.death_center_x = 0; self.death_center_y = 0
        self.surprised_face = False; self.eye_direction = 0

    def update(self, platforms, coins_list, keys_pressed, other_players=None):
        if self.is_dying: self.update_death_animation(); return

        if self.bounce_timer > 0:
            self.bounce_timer -= 1
            self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5
            self.ignore_wall_contact = True
        else:
            self.ignore_wall_contact = False

        # Input handling
        move_left_key, move_right_key, jump_key = (pygame.K_a, pygame.K_d, pygame.K_w) if self.player_num == 1 else (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
        
        if keys_pressed[move_left_key]: self.vel_x = -MOVE_SPEED; self.eye_direction = -1
        elif keys_pressed[move_right_key]: self.vel_x = MOVE_SPEED; self.eye_direction = 1
        else: self.vel_x *= FRICTION; self.eye_direction = 0
            
        can_normal_jump = self.on_ground or self.standing_on_player
        if keys_pressed[jump_key] and self.bounce_timer <= 0 and (can_normal_jump or self.can_wall_jump):
            self.vel_y = JUMP_STRENGTH; self.is_jumping = True
            if self.can_wall_jump:
                self.vel_x = self.wall_jump_direction * MOVE_SPEED * 1.5
                self.can_wall_jump = False; self.bounce_timer = 10
            jump_sound.play()

        self.vel_y += GRAVITY
        self.rect.x += int(self.vel_x)

        # Horizontal collisions
        self.touching_wall = False; current_wall_id = None
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0: self.rect.right = platform.rect.left
                elif self.vel_x < 0: self.rect.left = platform.rect.right
                if not (self.ignore_wall_contact and id(platform) == self.last_wall_id):
                    self.touching_wall = True
                    self.wall_jump_direction = -1 if self.vel_x > 0 else 1
                    current_wall_id = id(platform)
                self.vel_x = 0
        
        if other_players:
            for other in other_players:
                if self.rect.colliderect(other.rect):
                    if self.vel_x > 0: self.rect.right = other.rect.left
                    elif self.vel_x < 0: self.rect.left = other.rect.right
                    self.vel_x = 0
        
        if self.touching_wall and not self.on_ground and current_wall_id != self.last_wall_id:
            self.can_wall_jump = True; self.last_wall_id = current_wall_id
        
        self.rect.y += int(self.vel_y)

        # Vertical collisions
        self.on_ground = False; self.standing_on_player = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0: self.rect.bottom = platform.rect.top; self.on_ground = True
                elif self.vel_y < 0: self.rect.top = platform.rect.bottom
                self.vel_y = 0
        
        if other_players:
            for other in other_players:
                if self.rect.colliderect(other.rect):
                    if self.vel_y > 0: self.rect.bottom = other.rect.top; self.standing_on_player = True
                    elif self.vel_y < 0: self.rect.top = other.rect.bottom
                    self.vel_y = 0
        
        if other_players: # Re-check standing on player if already on top
            for other in other_players:
                if (self.rect.bottom == other.rect.top and # Allow for 1px float error
                    self.rect.right > other.rect.left and 
                    self.rect.left < other.rect.right):
                    self.standing_on_player = True; self.on_ground = True # Treat as on_ground for jumping logic

        # Collect coins
        for coin_item in coins_list[:]:
            if self.rect.colliderect(coin_item.rect):
                coins_list.remove(coin_item)
                self.collected_coins += 1
                coin_sound.play()
        
        if self.on_ground: self.is_jumping = False; self.last_wall_id = None
        if self.rect.top > SCREEN_HEIGHT: self.start_death_animation()

    def start_death_animation(self):
        self.is_dying = True; self.death_timer = 90; self.death_particles = []
        self.death_sound_played = False; self.death_phase = 0; self.surprised_face = True
        self.death_center_x = self.rect.centerx; self.death_center_y = SCREEN_HEIGHT // 3
        explosion_sound.set_volume(1.0); explosion_sound.play()

    def update_death_animation(self):
        if self.death_phase == 0 and self.death_timer <= 75: self.death_phase = 1
        elif self.death_phase == 1:
            dy = self.death_center_y - self.rect.centery; move_speed = abs(dy) * 0.15
            if move_speed < 3 and dy < 0: move_speed = 3
            if abs(dy) > 5: self.rect.y += int(dy * move_speed / abs(dy if dy else 1))
            if abs(dy) < 20: self.death_phase = 2
        elif self.death_phase == 2:
            remaining_growth_time = max(0, self.death_timer - 15)
            if remaining_growth_time > 0:
                growth_progress = (30 - remaining_growth_time) / 30; growth_factor = 1 + 2 * growth_progress
                center_x, center_y = self.rect.centerx, self.rect.centery
                self.rect.width, self.rect.height = int(40 * growth_factor), int(40 * growth_factor)
                self.rect.centerx, self.rect.centery = center_x, center_y
                if growth_factor >= 2.8:
                    for _ in range(80):
                        p = ExplosionParticle(self.rect.centerx, self.rect.centery)
                        p.size = random.randint(3, 8); p.vel_x = random.uniform(-10, 10); p.vel_y = random.uniform(-10, 10)
                        self.death_particles.append(p)
                    explosion_sound.play(); self.death_phase = 3; self.white_flash_timer = 10
        elif self.death_phase == 3 and hasattr(self, 'white_flash_timer'): self.white_flash_timer -= 1
        
        for p in self.death_particles[:]: p.update();
        if p.life <= 0: self.death_particles.remove(p)
        self.death_timer -= 1
        if self.death_timer <= 0:
            self.is_dying = False; self.surprised_face = False
            self.rect.width, self.rect.height = 40, 40; self.respawn()

    def respawn(self):
        self.rect.x, self.rect.y = self.spawn_x, self.spawn_y
        self.vel_x, self.vel_y = 0, 0
        self.last_wall_id = None; self.can_wall_jump = False
        self.collected_coins = 0 # Reset coins on respawn
        self.is_dying = False # Ensure not stuck in death anim
        self.death_phase = 0

    def draw(self, screen):
        if self.is_dying and self.death_phase == 3 and hasattr(self, 'white_flash_timer') and self.white_flash_timer > 0:
            flash_alpha = min(200, self.white_flash_timer * 25)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, flash_alpha)); screen.blit(flash_surface, (0, 0))
        
        if self.is_dying:
            if self.death_phase < 3 and self.death_timer > 15:
                pygame.draw.rect(screen, self.color, self.rect); pygame.draw.rect(screen, BLACK, self.rect, 2)
                scale_factor = self.rect.width / 40
                eye_size, pupil_size = int(10 * scale_factor), int(3 * scale_factor)
                left_eye_x, right_eye_x = self.rect.left + int(12 * scale_factor), self.rect.right - int(12 * scale_factor)
                eye_y = self.rect.top + int(15 * scale_factor)
                pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_size); pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_size)
                pygame.draw.circle(screen, BLACK, (left_eye_x, eye_y), pupil_size); pygame.draw.circle(screen, BLACK, (right_eye_x, eye_y), pupil_size)
                mouth_size, mouth_y = int(8 * scale_factor), self.rect.top + int(28 * scale_factor)
                pygame.draw.circle(screen, BLACK, (self.rect.centerx, mouth_y), mouth_size)
            for particle in self.death_particles: particle.draw(screen)
        else:
            pygame.draw.rect(screen, self.color, self.rect); pygame.draw.rect(screen, BLACK, self.rect, 2)
            eye_size, pupil_size, pupil_offset = 8, 4, 2
            left_eye_center, right_eye_center = (self.rect.left + 12, self.rect.top + 15), (self.rect.right - 12, self.rect.top + 15)
            pygame.draw.circle(screen, WHITE, left_eye_center, eye_size); pygame.draw.circle(screen, WHITE, right_eye_center, eye_size)
            
            pupil_x_offset = self.eye_direction * pupil_offset
            left_pupil_pos = (left_eye_center[0] + pupil_x_offset, left_eye_center[1])
            right_pupil_pos = (right_eye_center[0] + pupil_x_offset, right_eye_center[1])
            pygame.draw.circle(screen, BLACK, left_pupil_pos, pupil_size); pygame.draw.circle(screen, BLACK, right_pupil_pos, pupil_size)
            
            mouth_y = self.rect.top + 28
            if self.happy_face: pygame.draw.arc(screen, BLACK, (self.rect.left + 10, mouth_y - 5, 20, 15), math.pi, 2*math.pi, 2)
            else: pygame.draw.arc(screen, BLACK, (self.rect.left + 10, mouth_y, 20, 10), 0, math.pi, 2)
            
            if self.touching_wall and not self.on_ground:
                side_x = self.rect.right - 3 if self.wall_jump_direction == -1 else self.rect.left
                pygame.draw.rect(screen, WHITE, (side_x, self.rect.y + 5, 3, self.rect.height - 10))

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.rect = pygame.Rect(x, y, width, height); self.color = color
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect); pygame.draw.rect(screen, BLACK, self.rect, 2)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30); self.color = YELLOW; self.angle = 0
    def update(self): self.angle = (self.angle + 5) % 360 # Faster rotation
    def draw(self, screen):
        center = self.rect.center; points = []
        # Draw a simpler filled circle with an inner highlight for coin
        pygame.draw.circle(screen, self.color, center, 15)
        pygame.draw.circle(screen, BLACK, center, 15, 2)
        pygame.draw.circle(screen, (255,255,150), center, 10) # Highlight
        # Optional: Add a subtle spin effect if desired (e.g., slight width change)
        # scale_x = 15 * (0.8 + 0.2 * abs(math.cos(math.radians(self.angle))))
        # pygame.draw.ellipse(screen, self.color, (center[0]-scale_x, center[1]-15, scale_x*2, 30))
        # pygame.draw.ellipse(screen, BLACK, (center[0]-scale_x, center[1]-15, scale_x*2, 30),2)

class Goal:
    def __init__(self, x, y, is_door=False):
        self.rect = pygame.Rect(x, y, 60, 80); self.color = GREEN
        self.is_door = is_door; self.door_open = False
    def draw(self, screen):
        if self.is_door:
            door_width, door_height = 60, 80
            if self.door_open:
                pygame.draw.rect(screen, BROWN, (self.rect.x, self.rect.y, door_width, door_height), 5)
                pygame.draw.rect(screen, BLACK, (self.rect.x + 5, self.rect.y + 5, door_width - 10, door_height - 10))
                pygame.draw.polygon(screen, (255, 255, 200), [(self.rect.x + 10, self.rect.y + 10), (self.rect.x + door_width - 10, self.rect.y + 10), (self.rect.x + door_width//2, self.rect.y + door_height//2)])
            else:
                pygame.draw.rect(screen, BROWN, (self.rect.x, self.rect.y, door_width, door_height))
                pygame.draw.rect(screen, (139, 69, 19), (self.rect.x + 5, self.rect.y + 5, door_width - 10, door_height - 10))
                pygame.draw.circle(screen, YELLOW, (self.rect.x + door_width - 15, self.rect.y + door_height // 2), 5)
        else: # Flag
            pygame.draw.rect(screen, BROWN, (self.rect.x + 25, self.rect.y, 10, self.rect.height))
            pygame.draw.polygon(screen, self.color, [(self.rect.x + 35, self.rect.y), (self.rect.x + 60, self.rect.y + 20), (self.rect.x + 35, self.rect.y + 40)])

class Spike:
    def __init__(self, x, y, width=30, height=15):
        self.rect = pygame.Rect(x, y, width, height); self.color = (200, 200, 200)
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y + self.rect.height - 5, self.rect.width, 5))
        num_spikes = self.rect.width // 10
        for i in range(num_spikes):
            spike_x = self.rect.x + i * 10 + 5
            pygame.draw.polygon(screen, self.color, [(spike_x - 5, self.rect.y + self.rect.height - 5), (spike_x, self.rect.y), (spike_x + 5, self.rect.y + self.rect.height - 5)])

class ExplosionParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.size = random.randint(3, 8)
        self.color = random.choice(EXPLOSION_COLORS)
        self.vel_x, self.vel_y = random.uniform(-5, 5), random.uniform(-8, -2)
        self.gravity = 0.2; self.life = random.randint(20, 40)
    def update(self):
        self.vel_y += self.gravity; self.x += self.vel_x; self.y += self.vel_y
        self.life -= 1;
        if self.life < 10: self.size = max(1, self.size - 0.2)
    def draw(self, screen): pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Star:
    def __init__(self):
        self.x, self.y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT - 100)
        self.size = random.randint(1, 3); self.twinkle_speed = random.uniform(0.01, 0.05)
        self.brightness = random.uniform(0.5, 1.0); self.twinkle_offset = random.uniform(0, 2 * math.pi)
    def update(self, time): self.brightness = 0.5 + 0.5 * math.sin(time * self.twinkle_speed + self.twinkle_offset)
    def draw(self, screen):
        color = (int(STAR_COLOR[0] * self.brightness), int(STAR_COLOR[1] * self.brightness), int(STAR_COLOR[2] * self.brightness))
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

class LevelPortal:
    def __init__(self, x, y, world, level_num, portal_type="door", base_level_name="Level"):
        self.rect = pygame.Rect(x, y, 80, 100)
        self.world, self.level_num = world, level_num
        self.base_level_name = base_level_name
        self.portal_type = portal_type
        self.is_available = True # Could be used for unlocking later
        self.glow_time = random.uniform(0, math.pi * 2) # Random start for glow
        self.both_players_touching = False
        
        colors = {1: ((139, 69, 19), GREEN), 2: ((75, 75, 75), PURPLE), 3: ((50, 50, 100), (255, 215, 0))}
        self.color, self.accent_color = colors.get(world, (GRAY, WHITE))

    def update(self, player1, player2):
        self.both_players_touching = self.rect.colliderect(player1.rect) and self.rect.colliderect(player2.rect)
        self.glow_time += 0.05 # Slower glow

    def draw(self, screen):
        glow_alpha = int(64 + 63 * math.sin(self.glow_time * 2)) # More subtle glow

        if self.portal_type == "door":
            pygame.draw.rect(screen, self.color, self.rect); pygame.draw.rect(screen, BLACK, self.rect, 3)
            inner_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, self.rect.height - 20)
            pygame.draw.rect(screen, self.accent_color, inner_rect)
            pygame.draw.circle(screen, YELLOW, (self.rect.right - 20, self.rect.centery), 5) # Knob
            
            display_text_str = f"{self.level_num}"
            # if len(self.base_level_name) < 12 and not self.base_level_name.startswith("Level "):
            #     display_text_str = self.base_level_name # Keep it simple with just number for now
            level_text_surf = font_medium.render(display_text_str, True, WHITE)
            text_rect = level_text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
            screen.blit(level_text_surf, text_rect)
            world_id_text = font_small.render(f"W{self.world}", True, WHITE)
            screen.blit(world_id_text, world_id_text.get_rect(center=(self.rect.centerx, self.rect.centery + 20)))

        elif self.portal_type == "pipe":
            pygame.draw.rect(screen, GREEN, self.rect); pygame.draw.rect(screen, BLACK, self.rect, 3)
            opening_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 10, self.rect.width + 10, 20)
            pygame.draw.rect(screen, (0, 150, 0), opening_rect); pygame.draw.rect(screen, BLACK, opening_rect, 3)
            level_text_surf = font_medium.render(f"{self.level_num}", True, WHITE)
            screen.blit(level_text_surf, level_text_surf.get_rect(center=(self.rect.centerx, self.rect.top + 30)))
            
        elif self.portal_type == "portal":
            pygame.draw.circle(screen, self.accent_color, self.rect.center, 50, 5)
            for i in range(3):
                angle = self.glow_time * 2 + i * (2 * math.pi / 3)
                inner_x, inner_y = self.rect.centerx + 30 * math.cos(angle), self.rect.centery + 30 * math.sin(angle)
                pygame.draw.circle(screen, self.color, (int(inner_x), int(inner_y)), 8)
            pygame.draw.circle(screen, (0,0,0, glow_alpha + 100), self.rect.center, 25) # Inner portal with alpha
            level_text_surf = font_medium.render(f"{self.level_num}", True, self.accent_color)
            screen.blit(level_text_surf, level_text_surf.get_rect(center=self.rect.center))
        
        if self.both_players_touching:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.accent_color, glow_alpha), (0, 0, self.rect.width + 20, self.rect.height + 20), 5, border_radius=5)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        
        # Base level name above portal
        base_name_text = font_small.render(self.base_level_name, True, WHITE)
        base_name_rect = base_name_text.get_rect(center=(self.rect.centerx, self.rect.y - 15))
        pygame.draw.rect(screen, (50,50,50,150), base_name_rect.inflate(10,4), border_radius=3) # semi-transparent bg
        screen.blit(base_name_text, base_name_rect)


class LevelManager:
    def __init__(self):
        self.levels_dir = "levels"
        self.available_levels_by_base = {} # {(world, level_num): [{'id': 'a', 'display_name': 'Name', 'filename': '...'}, ...]}
        self.base_levels_meta = [] # Stores unique {'world': w, 'level': l, 'name': base_name}
        self.current_world = 1
        self.current_level = 1 # Base level number
        self.current_selected_version_id = None
        self.current_level_data = {} # Data of the currently loaded level version
        self.scan_available_levels()

        self.max_worlds = max([meta['world'] for meta in self.base_levels_meta]) if self.base_levels_meta else 1
        # max_levels per world can be found by checking len(self.available_levels_by_base.get((w_num, l_num), []))

    def scan_available_levels(self):
        self.available_levels_by_base = {}
        self.base_levels_meta = []
        temp_base_levels_meta = {} 

        if not os.path.exists(self.levels_dir):
            os.makedirs(self.levels_dir); print(f"Created missing '{self.levels_dir}' directory.")
            return

        # Pattern for new versioned files: world1_level1_a.json
        versioned_pattern = re.compile(r"world(\d+)_level(\d+)_([a-zA-Z0-9_]+)\.json", re.IGNORECASE)
        # Pattern for legacy files: world1_level1.json
        legacy_pattern = re.compile(r"world(\d+)_level(\d+)\.json", re.IGNORECASE)

        for filename in os.listdir(self.levels_dir):
            # Try versioned pattern first
            match = versioned_pattern.match(filename)
            version_id = None
            if match:
                world = int(match.group(1))
                level_num = int(match.group(2))
                version_id = match.group(3)
            else:
                # Try legacy pattern
                match = legacy_pattern.match(filename)
                if match:
                    world = int(match.group(1))
                    level_num = int(match.group(2))
                    version_id = "default"  # Default version ID for legacy files
            
            if match:
                try:
                    filepath = os.path.join(self.levels_dir, filename)
                    with open(filepath, 'r') as f: level_data = json.load(f)
                    
                    display_name = level_data.get('name', f"Version {version_id.replace('_', ' ').title()}")
                    base_level_name = level_data.get('base_level_name', f"Level {level_num}")

                    base_key = (world, level_num)
                    if base_key not in self.available_levels_by_base: self.available_levels_by_base[base_key] = []
                    
                    self.available_levels_by_base[base_key].append({
                        'id': version_id, 'display_name': display_name, 'filename': filename
                    })

                    if base_key not in temp_base_levels_meta:
                        temp_base_levels_meta[base_key] = {'world': world, 'level': level_num, 'name': base_level_name}
                except Exception as e: print(f"Error processing {filename}: {e}")
            # else: print(f"Skipping non-matching file: {filename}") # Optional: for debugging
        
        for base_key in self.available_levels_by_base:
            self.available_levels_by_base[base_key].sort(key=lambda v: v['id'])
        self.base_levels_meta = sorted(list(temp_base_levels_meta.values()), key=lambda x: (x['world'], x['level']))

    def get_versions_for_level(self, world, level_num):
        return self.available_levels_by_base.get((world, level_num), [])

    def load_level_from_json(self, world, level_num, version_id):
        versions = self.get_versions_for_level(world, level_num)
        level_file_info = next((v for v in versions if v['id'] == version_id), None)

        if not level_file_info:
            self.current_level_data = {"name": "Fallback: Version Missing", "world": world, "level": level_num, "version_id": version_id}
            return self.create_fallback_level()
        
        try:
            filepath = os.path.join(self.levels_dir, level_file_info['filename'])
            with open(filepath, 'r') as f: level_data_json = json.load(f)
            
            # Ensure critical data is present in self.current_level_data
            self.current_level_data = {
                'world': level_data_json.get('world', world),
                'level': level_data_json.get('level', level_num), # Base level num
                'version_id': level_data_json.get('version_id', version_id),
                'name': level_data_json.get('name', level_file_info['display_name']),
                'base_level_name': level_data_json.get('base_level_name', f"Level {level_num}"),
                'background_type': level_data_json.get('background_type', 'day'),
                'player_spawns': level_data_json.get('player_spawns', [{'x':100, 'y':SCREEN_HEIGHT-100}, {'x':150, 'y':SCREEN_HEIGHT-100}]),
                'goal': level_data_json.get('goal', {'x': SCREEN_WIDTH - 100, 'y': SCREEN_HEIGHT - 120, 'is_door': False}),
                'platforms': level_data_json.get('platforms', []),
                'coins': level_data_json.get('coins', []),
                'spikes': level_data_json.get('spikes', [])
            }
            return self.parse_level_data(self.current_level_data) # Pass the processed data
        except Exception as e:
            print(f"Error loading {level_file_info['filename']}: {e}")
            self.current_level_data = {"name": "Fallback: Load Error", "world": world, "level": level_num, "version_id": version_id}
            return self.create_fallback_level()

    def parse_level_data(self, level_data_to_parse): # Takes the full data dict
        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], tuple(p.get('color', BROWN))) for p in level_data_to_parse.get('platforms', [])]
        coins = [Coin(c['x'], c['y']) for c in level_data_to_parse.get('coins', [])]
        spikes = [Spike(s['x'], s['y'], s.get('width', 30), s.get('height', 15)) for s in level_data_to_parse.get('spikes', [])]
        total_coins = len(coins)
        # self.current_level_data is already set by load_level_from_json before calling this
        return platforms, coins, total_coins, spikes

    def create_fallback_level(self):
        print("Loading fallback level.")
        platforms = [Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)]
        coins = [Coin(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        # self.current_level_data should be set by the caller to reflect fallback state
        self.current_level_data.setdefault('goal', {'x': SCREEN_WIDTH - 100, 'y': SCREEN_HEIGHT - 120, 'is_door': False})
        self.current_level_data.setdefault('player_spawns', [{'x':100, 'y':SCREEN_HEIGHT-100}, {'x':150, 'y':SCREEN_HEIGHT-100}])
        return platforms, coins, 1, []

    def get_level(self, version_id_to_load): # Must provide version_id
        # self.current_world and self.current_level (base) should be set by caller
        self.current_selected_version_id = version_id_to_load
        return self.load_level_from_json(self.current_world, self.current_level, version_id_to_load)

    def get_current_level_data(self): return self.current_level_data

    def reset_level_tracking(self): # Call when returning to level select map
        if self.base_levels_meta:
            first_meta = self.base_levels_meta[0]
            self.current_world = first_meta['world']
            self.current_level = first_meta['level']
        else: self.current_world, self.current_level = 1, 1
        self.current_selected_version_id = None
        self.current_level_data = {}

class LevelSelectMap:
    def __init__(self, level_manager):
        self.level_manager = level_manager
        self.platforms = []; self.portals = []
        self.create_level_select_map()

    def create_level_select_map(self):
        # Ground platforms
        self.platforms.extend([
            Platform(50, SCREEN_HEIGHT - 40, 350, 40, (139, 69, 19)),   # W1 ground
            Platform(100, SCREEN_HEIGHT - 120, 250, 20, (139, 69, 19)), # W1 platform
            Platform(450, SCREEN_HEIGHT - 40, 350, 40, (75, 75, 75)),    # W2 ground (elevated relative to W1)
            Platform(500, SCREEN_HEIGHT - 200, 250, 20, (75, 75, 75)),   # W2 platform
            Platform(850, SCREEN_HEIGHT - 40, 380, 40, (50, 50, 100)),   # W3 ground
            Platform(900, SCREEN_HEIGHT - 280, 280, 20, (50, 50, 100)),  # W3 platform
        ])
        # Connecting platforms (example, adjust as needed for accessibility)
        self.platforms.extend([
            Platform(380, SCREEN_HEIGHT - 100, 100, 20, GRAY), # W1 to W2 jump point
            Platform(780, SCREEN_HEIGHT - 180, 100, 20, GRAY), # W2 to W3 jump point
        ])

        base_portals_meta = self.level_manager.base_levels_meta
        portal_spacing_x = 110; portal_spacing_y = 120 # For multiple rows if needed

        world_configs = { # Base X, Y, type, num_per_row
            1: {'x': 120, 'y': SCREEN_HEIGHT - 220, 'type': "door", 'row_y': SCREEN_HEIGHT - 120 - 100},
            2: {'x': 520, 'y': SCREEN_HEIGHT - 300, 'type': "pipe", 'row_y': SCREEN_HEIGHT - 200 - 100},
            3: {'x': 920, 'y': SCREEN_HEIGHT - 380, 'type': "portal",'row_y': SCREEN_HEIGHT - 280 - 100}
        }
        
        portals_in_world_count = {w: 0 for w in world_configs}

        for meta in base_portals_meta:
            world, level_num, base_name = meta['world'], meta['level'], meta['name']
            config = world_configs.get(world)
            if not config: continue

            x = config['x'] + (portals_in_world_count[world] % 3) * portal_spacing_x # Max 3 per row
            y = config['row_y'] - (portals_in_world_count[world] // 3) * portal_spacing_y 
            
            self.portals.append(LevelPortal(x, y, world, level_num, config['type'], base_name))
            portals_in_world_count[world] +=1

    def update(self, player1, player2): [p.update(player1, player2) for p in self.portals]
    def check_portal_activation(self, player1, player2):
        for portal in self.portals:
            if portal.both_players_touching: return portal.world, portal.level_num
        return None, None
    def draw(self, screen):
        for y_grad in range(SCREEN_HEIGHT): # Gradient sky
            ratio = y_grad / SCREEN_HEIGHT
            r,g,b = int(135*(1-ratio)+25*ratio), int(206*(1-ratio)+25*ratio), int(235*(1-ratio)+50*ratio)
            pygame.draw.line(screen, (r,g,b), (0, y_grad), (SCREEN_WIDTH, y_grad))
        
        [p.draw(screen) for p in self.platforms]; [p.draw(screen) for p in self.portals]
        
        title_text = font_large.render("LEVEL SELECT", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        pygame.draw.rect(screen, WHITE, title_rect.inflate(40, 20), border_radius=5)
        pygame.draw.rect(screen, BLACK, title_rect.inflate(40, 20), 3, border_radius=5)
        screen.blit(title_text, title_rect)
        
        instr_text = font_medium.render("Move both players to a portal and press SPACE/ENTER", True, BLACK)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH//2, 110))
        pygame.draw.rect(screen, (*WHITE, 200), instr_rect.inflate(20,10), border_radius=3) # semi-transparent
        screen.blit(instr_text, instr_rect)

# --- Utility functions for game ---
def create_goal_from_level_data(level_manager):
    goal_data = level_manager.get_current_level_data().get('goal', {})
    return Goal(goal_data.get('x', SCREEN_WIDTH - 100), goal_data.get('y', SCREEN_HEIGHT - 120), goal_data.get('is_door', False))

def update_player_spawn_points(level_manager, player1, player2):
    spawns = level_manager.get_current_level_data().get('player_spawns', [{},{}])
    p1_spawn = spawns[0] if len(spawns) > 0 else {}
    p2_spawn = spawns[1] if len(spawns) > 1 else {}
    player1.spawn_x, player1.spawn_y = p1_spawn.get('x', 100), p1_spawn.get('y', SCREEN_HEIGHT - 100)
    player2.spawn_x, player2.spawn_y = p2_spawn.get('x', 150), p2_spawn.get('y', SCREEN_HEIGHT - 100)

# --- Main Game Loop ---
def main():
    level_manager = LevelManager()
    game_state = GAME_STATE_LEVEL_SELECT
    level_select_map = LevelSelectMap(level_manager) # Create once

    player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, 1) # Initial spawn for level select
    player2 = Player(150, SCREEN_HEIGHT - 100, RED, 2)  # Initial spawn for level select

    platforms, coins_list, total_coins, spikes, goal = [], [], 0, [], None
    stars = [Star() for _ in range(100)]; time_elapsed = 0
    
    # For VERSION_SELECT state
    selected_base_world, selected_base_level_num = None, None
    available_versions_for_selection, current_version_selection_idx = [], 0
    game_complete_flag = False # For current level play

    running = True
    while running:
        time_elapsed += 0.1; keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GAME_STATE_PLAYING: game_state = GAME_STATE_LEVEL_SELECT; level_manager.reset_level_tracking()
                    elif game_state == GAME_STATE_VERSION_SELECT: game_state = GAME_STATE_LEVEL_SELECT
                    else: running = False # Exit from Level Select

                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if game_state == GAME_STATE_LEVEL_SELECT:
                        activated_world, activated_level_num = level_select_map.check_portal_activation(player1, player2)
                        if activated_world:
                            selected_base_world, selected_base_level_num = activated_world, activated_level_num
                            available_versions_for_selection = level_manager.get_versions_for_level(selected_base_world, selected_base_level_num)
                            if available_versions_for_selection:
                                current_version_selection_idx = 0; game_state = GAME_STATE_VERSION_SELECT; jump_sound.play()
                            else: print(f"No versions for W{selected_base_world}L{selected_base_level_num}")
                    
                    elif game_state == GAME_STATE_VERSION_SELECT and available_versions_for_selection:
                        selected_version_info = available_versions_for_selection[current_version_selection_idx]
                        level_manager.current_world, level_manager.current_level = selected_base_world, selected_base_level_num
                        platforms, coins_list, total_coins, spikes = level_manager.get_level(selected_version_info['id'])
                        goal = create_goal_from_level_data(level_manager)
                        update_player_spawn_points(level_manager, player1, player2)
                        player1.respawn(); player2.respawn()
                        game_state = GAME_STATE_PLAYING; game_complete_flag = False
                
                elif game_state == GAME_STATE_VERSION_SELECT and available_versions_for_selection:
                    if event.key == pygame.K_UP: current_version_selection_idx = (current_version_selection_idx - 1) % len(available_versions_for_selection)
                    elif event.key == pygame.K_DOWN: current_version_selection_idx = (current_version_selection_idx + 1) % len(available_versions_for_selection)

                elif event.key == pygame.K_r and game_state == GAME_STATE_PLAYING:
                    platforms, coins_list, total_coins, spikes = level_manager.get_level(level_manager.current_selected_version_id)
                    goal = create_goal_from_level_data(level_manager) # Recreate goal
                    update_player_spawn_points(level_manager, player1, player2) # Ensure spawns are for this level
                    player1.respawn(); player2.respawn(); game_complete_flag = False

                elif event.key == pygame.K_n and game_state == GAME_STATE_PLAYING and game_complete_flag:
                    game_state = GAME_STATE_LEVEL_SELECT; level_manager.reset_level_tracking() # Return to map

                elif event.key == pygame.K_F11: FULLSCREEN = not FULLSCREEN; setup_display()
        
        # Updates
        if game_state == GAME_STATE_LEVEL_SELECT:
            level_select_map.update(player1, player2)
            player1.update(level_select_map.platforms, [], keys_pressed, [player2])
            player2.update(level_select_map.platforms, [], keys_pressed, [player1])
        elif game_state == GAME_STATE_PLAYING and not game_complete_flag:
            player1.update(platforms, coins_list, keys_pressed, [player2])
            player2.update(platforms, coins_list, keys_pressed, [player1])
            [c.update() for c in coins_list]
            
            for spike_obj in spikes: # Renamed to avoid conflict
                if not player1.is_dying and player1.rect.colliderect(spike_obj.rect): player1.start_death_animation()
                if not player2.is_dying and player2.rect.colliderect(spike_obj.rect): player2.start_death_animation()

            if (goal and player1.rect.colliderect(goal.rect) and player2.rect.colliderect(goal.rect) and not coins_list):
                if not game_complete_flag: level_complete_sound.play()
                game_complete_flag = True
            
            player1.happy_face = player2.happy_face = not coins_list
            if goal and goal.is_door: goal.door_open = not coins_list

        # Drawing
        if game_state == GAME_STATE_LEVEL_SELECT:
            level_select_map.draw(screen)
            player1.draw(screen); player2.draw(screen)
            aw, aln = level_select_map.check_portal_activation(player1, player2)
            if aw:
                portal_obj = next((p for p in level_select_map.portals if p.world == aw and p.level_num == aln), None)
                p_name = portal_obj.base_level_name if portal_obj else f"L{aln}"
                prompt = font_medium.render(f"SPACE for {p_name} (W{aw})", True, GREEN)
                pr_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
                pygame.draw.rect(screen, (*WHITE,200), pr_rect.inflate(10,5), border_radius=3)
                screen.blit(prompt, pr_rect)

        elif game_state == GAME_STATE_VERSION_SELECT:
            screen.fill(NIGHT_SKY) # Darker bg for selection
            for s in stars:
                s.update(time_elapsed)
                s.draw(screen)
            title_str = f"World {selected_base_world} - Level {selected_base_level_num}: Select Version"
            title_surf = font_large.render(title_str, True, WHITE)
            screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))

            if not available_versions_for_selection:
                screen.blit(font_medium.render("No versions found!", True, RED), (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
            else:
                for i, ver_info in enumerate(available_versions_for_selection):
                    text = f"{ver_info['display_name']} (ID: {ver_info['id']})"
                    color = YELLOW if i == current_version_selection_idx else WHITE
                    surf = font_medium.render(text, True, color)
                    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                    bg_rect_color = (*GRAY, 100) if i == current_version_selection_idx else (*GRAY, 50)
                    pygame.draw.rect(screen, bg_rect_color, rect.inflate(20,10), border_radius=5)
                    screen.blit(surf, rect)
            instr = font_small.render("UP/DOWN, SPACE/ENTER to Select, ESC for Map", True, WHITE)
            screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

        elif game_state == GAME_STATE_PLAYING:
            level_data = level_manager.get_current_level_data()
            bg_color = get_current_background_color(level_data)
            txt_color = get_text_color(bg_color)
            screen.fill(bg_color)
            if level_data.get('background_type') == 'night':
                for s in stars:
                    s.update(time_elapsed)
                    s.draw(screen)

            [p.draw(screen) for p in platforms]; [c.draw(screen) for c in coins_list]
            if goal: goal.draw(screen)
            [s.draw(screen) for s in spikes] # Renamed for clarity
            player1.draw(screen); player2.draw(screen)
            
            # UI Text
            lvl_name = level_data.get('name', "Unnamed Level")
            ver_id = level_data.get('version_id', "N/A")
            screen.blit(font_medium.render(f"{lvl_name} (v: {ver_id})", True, txt_color), (20, 20))
            collected = player1.collected_coins + player2.collected_coins
            screen.blit(font_medium.render(f"Coins: {collected}/{total_coins}", True, txt_color), (20, 60))

            if game_complete_flag:
                comp_text = font_large.render("LEVEL COMPLETE!", True, GREEN)
                comp_rect = comp_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
                pygame.draw.rect(screen,WHITE,comp_rect.inflate(20,10), border_radius=5); screen.blit(comp_text,comp_rect)
                next_text = font_medium.render("N for Level Select, R to Replay", True, BLACK)
                screen.blit(next_text, next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
            
            # Basic instructions on playing screen
            instr_y_start = SCREEN_HEIGHT - 100
            instructions_playing = ["P1: WASD, P2: Arrows", "R: Restart, ESC: Map"]
            for i, txt in enumerate(instructions_playing):
                screen.blit(font_small.render(txt, True, txt_color), (20, instr_y_start + i * 20))


        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()