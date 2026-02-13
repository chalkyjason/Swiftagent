import pygame
import json
import time
import random
import os
import sys
from datetime import datetime, timedelta
from enum import Enum
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
FPS = 60
PIXEL_SIZE = 4  # For pixelated effect

# Colors (Retro palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)

class PetState(Enum):
    HAPPY = "happy"
    SAD = "sad"
    SLEEPING = "sleeping"
    EATING = "eating"
    PLAYING = "playing"
    SICK = "sick"
    DEAD = "dead"

class TamagotchiGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixelated Tamagotchi")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Pet stats (0-100)
        self.hunger = 80
        self.happiness = 80
        self.health = 90
        self.energy = 70
        self.age = 0
        self.level = 1
        
        # Pet properties
        self.pet_name = "Pixel"
        self.pet_state = PetState.HAPPY
        self.last_update = time.time()
        self.birth_time = time.time()
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.pet_x = WINDOW_WIDTH // 2
        self.pet_y = WINDOW_HEIGHT // 2 - 50
        self.bob_offset = 0
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Load or create save file
        self.save_file = "tamagotchi_save.json"
        self.load_game()
        
        # Menu system
        self.menu_items = ["Feed", "Play", "Medicine", "Sleep", "Stats", "Save"]
        self.selected_menu = 0
        
    def save_game(self):
        """Save game state to file"""
        save_data = {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "health": self.health,
            "energy": self.energy,
            "age": self.age,
            "level": self.level,
            "pet_name": self.pet_name,
            "last_update": time.time(),
            "birth_time": self.birth_time
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            print("Game saved!")
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def load_game(self):
        """Load game state from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)
                
                self.hunger = save_data.get("hunger", 50)
                self.happiness = save_data.get("happiness", 50)
                self.health = save_data.get("health", 80)
                self.energy = save_data.get("energy", 60)
                self.age = save_data.get("age", 0)
                self.level = save_data.get("level", 1)
                self.pet_name = save_data.get("pet_name", "Pixel")
                self.birth_time = save_data.get("birth_time", time.time())
                
                # Calculate time passed while away
                last_update = save_data.get("last_update", time.time())
                time_passed = time.time() - last_update
                self.update_stats_for_time(time_passed)
                
                print("Game loaded!")
            except Exception as e:
                print(f"Error loading game: {e}")
                self.create_new_pet()
        else:
            self.create_new_pet()
    
    def create_new_pet(self):
        """Create a new pet with default stats"""
        self.hunger = 80
        self.happiness = 80
        self.health = 90
        self.energy = 70
        self.age = 0
        self.level = 1
        self.birth_time = time.time()
        print("New pet created!")
    
    def update_stats_for_time(self, time_passed):
        """Update stats based on time passed (for when game was closed)"""
        hours_passed = time_passed / 3600
        
        # Decrease stats over time
        self.hunger = max(0, self.hunger - hours_passed * 5)
        self.happiness = max(0, self.happiness - hours_passed * 3)
        self.energy = max(0, self.energy - hours_passed * 2)
        
        # Health decreases if other stats are low
        if self.hunger < 20 or self.happiness < 20:
            self.health = max(0, self.health - hours_passed * 2)
    
    def update_pet_state(self):
        """Update pet state based on stats"""
        if self.health <= 0:
            self.pet_state = PetState.DEAD
        elif self.health < 30 or self.hunger < 20:
            self.pet_state = PetState.SICK
        elif self.energy < 20:
            self.pet_state = PetState.SLEEPING
        elif self.happiness < 30:
            self.pet_state = PetState.SAD
        else:
            self.pet_state = PetState.HAPPY
    
    def update_stats(self):
        """Update pet stats over time"""
        current_time = time.time()
        time_delta = current_time - self.last_update
        
        if time_delta >= 60:  # Update every minute
            self.hunger = max(0, self.hunger - 1)
            self.happiness = max(0, self.happiness - 0.5)
            self.energy = max(0, self.energy - 0.3)
            
            # Health decreases if other stats are low
            if self.hunger < 20 or self.happiness < 20:
                self.health = max(0, self.health - 1)
            elif self.health < 100:
                self.health = min(100, self.health + 0.1)
            
            # Age increases
            self.age = int((current_time - self.birth_time) / 3600)  # Age in hours
            self.level = min(10, self.age // 24 + 1)  # Level up every day
            
            self.last_update = current_time
    
    def feed_pet(self):
        """Feed the pet"""
        if self.hunger < 100:
            self.hunger = min(100, self.hunger + 25)
            self.happiness = min(100, self.happiness + 5)
            self.pet_state = PetState.EATING
            print("Fed the pet!")
    
    def play_with_pet(self):
        """Play with the pet"""
        if self.energy > 10:
            self.happiness = min(100, self.happiness + 20)
            self.energy = max(0, self.energy - 15)
            self.pet_state = PetState.PLAYING
            print("Played with pet!")
        else:
            print("Pet is too tired to play!")
    
    def give_medicine(self):
        """Give medicine to pet"""
        if self.health < 100:
            self.health = min(100, self.health + 30)
            self.happiness = max(0, self.happiness - 5)  # Pet doesn't like medicine
            print("Gave medicine to pet!")
    
    def pet_sleep(self):
        """Make pet sleep"""
        self.energy = min(100, self.energy + 40)
        self.pet_state = PetState.SLEEPING
        print("Pet is sleeping...")
    
    def draw_pixel_pet(self):
        """Draw the pixelated pet"""
        # Simple pixel art pet (16x16 scaled up)
        pixel_size = 8
        pet_size = 16
        
        # Calculate position with bobbing animation
        self.bob_offset = math.sin(self.animation_timer * 0.05) * 3
        draw_x = self.pet_x - (pet_size * pixel_size) // 2
        draw_y = int(self.pet_y + self.bob_offset) - (pet_size * pixel_size) // 2
        
        # Pet color based on state
        pet_color = GREEN
        if self.pet_state == PetState.SAD:
            pet_color = BLUE
        elif self.pet_state == PetState.SICK:
            pet_color = PURPLE
        elif self.pet_state == PetState.SLEEPING:
            pet_color = GRAY
        elif self.pet_state == PetState.DEAD:
            pet_color = RED
        elif self.pet_state == PetState.EATING:
            pet_color = ORANGE
        elif self.pet_state == PetState.PLAYING:
            pet_color = YELLOW
        
        # Draw simple pet sprite (basic oval shape)
        for y in range(pet_size):
            for x in range(pet_size):
                # Create oval shape
                center_x, center_y = pet_size // 2, pet_size // 2
                if ((x - center_x) ** 2 / (pet_size // 2) ** 2 + 
                    (y - center_y) ** 2 / (pet_size // 2.5) ** 2) <= 1:
                    
                    rect = pygame.Rect(
                        draw_x + x * pixel_size,
                        draw_y + y * pixel_size,
                        pixel_size,
                        pixel_size
                    )
                    pygame.draw.rect(self.screen, pet_color, rect)
        
        # Draw eyes
        eye_color = BLACK
        if self.pet_state == PetState.SLEEPING:
            eye_color = GRAY
        elif self.pet_state == PetState.DEAD:
            eye_color = RED
        
        # Left eye
        eye_rect = pygame.Rect(
            draw_x + 4 * pixel_size,
            draw_y + 5 * pixel_size,
            pixel_size * 2,
            pixel_size * 2
        )
        pygame.draw.rect(self.screen, eye_color, eye_rect)
        
        # Right eye
        eye_rect = pygame.Rect(
            draw_x + 10 * pixel_size,
            draw_y + 5 * pixel_size,
            pixel_size * 2,
            pixel_size * 2
        )
        pygame.draw.rect(self.screen, eye_color, eye_rect)
        
        # Draw mouth based on happiness
        mouth_color = BLACK
        mouth_y = draw_y + 10 * pixel_size
        if self.happiness > 60:
            # Happy mouth (smile)
            for i in range(6):
                mouth_rect = pygame.Rect(
                    draw_x + (5 + i) * pixel_size,
                    mouth_y,
                    pixel_size,
                    pixel_size
                )
                pygame.draw.rect(self.screen, mouth_color, mouth_rect)
        elif self.happiness < 30:
            # Sad mouth (frown)
            for i in range(4):
                mouth_rect = pygame.Rect(
                    draw_x + (6 + i) * pixel_size,
                    mouth_y + pixel_size,
                    pixel_size,
                    pixel_size
                )
                pygame.draw.rect(self.screen, mouth_color, mouth_rect)
    
    def draw_stats(self):
        """Draw pet stats"""
        y_offset = 20
        
        # Pet name and level
        name_text = self.font.render(f"{self.pet_name} (Lv.{self.level})", True, WHITE)
        self.screen.blit(name_text, (10, y_offset))
        
        # Age
        age_text = self.small_font.render(f"Age: {self.age}h", True, WHITE)
        self.screen.blit(age_text, (10, y_offset + 25))
        
        # Status
        status_text = self.small_font.render(f"Status: {self.pet_state.value.title()}", True, WHITE)
        self.screen.blit(status_text, (10, y_offset + 45))
        
        # Stats bars
        stats = [
            ("Hunger", self.hunger, RED),
            ("Happiness", self.happiness, YELLOW),
            ("Health", self.health, GREEN),
            ("Energy", self.energy, BLUE)
        ]
        
        for i, (stat_name, value, color) in enumerate(stats):
            y = y_offset + 70 + i * 30
            
            # Stat name
            stat_text = self.small_font.render(f"{stat_name}:", True, WHITE)
            self.screen.blit(stat_text, (10, y))
            
            # Stat bar background
            bar_rect = pygame.Rect(80, y, 100, 15)
            pygame.draw.rect(self.screen, GRAY, bar_rect)
            
            # Stat bar fill
            fill_width = int(value)
            fill_rect = pygame.Rect(80, y, fill_width, 15)
            pygame.draw.rect(self.screen, color, fill_rect)
            
            # Stat value text
            value_text = self.small_font.render(f"{int(value)}", True, WHITE)
            self.screen.blit(value_text, (190, y))
    
    def draw_menu(self):
        """Draw the action menu"""
        menu_y = WINDOW_HEIGHT - 120
        menu_width = WINDOW_WIDTH - 20
        menu_height = 100
        
        # Menu background
        menu_rect = pygame.Rect(10, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, GRAY, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 2)
        
        # Menu items
        cols = 3
        rows = 2
        item_width = menu_width // cols
        item_height = menu_height // rows
        
        for i, item in enumerate(self.menu_items):
            col = i % cols
            row = i // cols
            
            item_x = 10 + col * item_width
            item_y = menu_y + row * item_height
            
            # Highlight selected item
            if i == self.selected_menu:
                highlight_rect = pygame.Rect(item_x, item_y, item_width, item_height)
                pygame.draw.rect(self.screen, BLUE, highlight_rect)
            
            # Item text
            item_text = self.small_font.render(item, True, WHITE)
            text_rect = item_text.get_rect()
            text_rect.center = (item_x + item_width // 2, item_y + item_height // 2)
            self.screen.blit(item_text, text_rect)
    
    def handle_menu_action(self):
        """Handle selected menu action"""
        action = self.menu_items[self.selected_menu]
        
        if action == "Feed":
            self.feed_pet()
        elif action == "Play":
            self.play_with_pet()
        elif action == "Medicine":
            self.give_medicine()
        elif action == "Sleep":
            self.pet_sleep()
        elif action == "Stats":
            print(f"Stats - Hunger: {self.hunger}, Happiness: {self.happiness}, Health: {self.health}, Energy: {self.energy}")
        elif action == "Save":
            self.save_game()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_menu = (self.selected_menu - 1) % len(self.menu_items)
                elif event.key == pygame.K_RIGHT:
                    self.selected_menu = (self.selected_menu + 1) % len(self.menu_items)
                elif event.key == pygame.K_UP:
                    self.selected_menu = (self.selected_menu - 3) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_menu = (self.selected_menu + 3) % len(self.menu_items)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.handle_menu_action()
                elif event.key == pygame.K_ESCAPE:
                    self.save_game()
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks on menu
                mouse_x, mouse_y = pygame.mouse.get_pos()
                menu_y = WINDOW_HEIGHT - 120
                
                if menu_y <= mouse_y <= WINDOW_HEIGHT - 20:
                    # Click is in menu area
                    cols = 3
                    item_width = (WINDOW_WIDTH - 20) // cols
                    item_height = 100 // 2
                    
                    col = (mouse_x - 10) // item_width
                    row = (mouse_y - menu_y) // item_height
                    
                    if 0 <= col < cols and 0 <= row < 2:
                        menu_index = row * cols + col
                        if menu_index < len(self.menu_items):
                            self.selected_menu = menu_index
                            self.handle_menu_action()
    
    def update(self):
        """Update game state"""
        self.animation_timer += 1
        
        # Update pet stats
        self.update_stats()
        self.update_pet_state()
        
        # Auto-save periodically
        if self.animation_timer % (FPS * 300) == 0:  # Every 5 minutes
            self.save_game()
    
    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw pet
        self.draw_pixel_pet()
        
        # Draw UI
        self.draw_stats()
        self.draw_menu()
        
        # Instructions
        instruction_text = self.small_font.render("Use Arrow Keys + Space/Enter, or Click to interact", True, WHITE)
        self.screen.blit(instruction_text, (10, WINDOW_HEIGHT - 15))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Welcome to Pixelated Tamagotchi!")
        print("Controls:")
        print("- Arrow Keys: Navigate menu")
        print("- Space/Enter: Select action")
        print("- Mouse: Click on menu items")
        print("- ESC: Quit and save")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TamagotchiGame()
    game.run()
