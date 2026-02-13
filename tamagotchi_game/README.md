# Pixelated Tamagotchi Game

A retro-styled virtual pet game that lives on your computer!

## Features

- **Virtual Pet Simulation**: Take care of your pixelated pet with hunger, happiness, health, and energy stats
- **Real-time Progression**: Your pet continues to age and change even when the game is closed
- **Pixel Art Style**: Classic 8-bit aesthetic with chunky pixel graphics
- **Persistent Save System**: Your pet's progress is automatically saved
- **Interactive Care**: Feed, play, heal, and help your pet sleep
- **Evolution System**: Watch your pet grow and level up over time

## Installation

1. Make sure you have Python 3.6+ installed
2. Install pygame:
   ```bash
   pip install pygame
   ```
   or
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python tamagotchi.py
   ```

2. **Controls**:
   - Arrow Keys: Navigate the action menu
   - Space/Enter: Select an action
   - Mouse: Click on menu items directly
   - ESC: Save and quit

3. **Actions**:
   - **Feed**: Increases hunger and slightly boosts happiness
   - **Play**: Greatly increases happiness but uses energy
   - **Medicine**: Restores health (pet won't like it much)
   - **Sleep**: Restores energy
   - **Stats**: View detailed pet statistics
   - **Save**: Manually save your progress

## Pet Care Tips

- Keep all stats above 20 to maintain pet health
- A happy pet is a healthy pet - play regularly!
- Don't let your pet get too tired before playing
- Your pet ages in real-time, even when the game is closed
- The game auto-saves every 5 minutes and when you quit

## Pet States

Your pet will show different emotions and colors based on its condition:
- **Happy** (Green): All stats are good
- **Sad** (Blue): Happiness is low
- **Sick** (Purple): Health is low or other stats are critically low
- **Sleeping** (Gray): Energy is very low
- **Eating** (Orange): Just been fed
- **Playing** (Yellow): Just played with
- **Dead** (Red): Health reached zero (game over)

## File Structure

- `tamagotchi.py`: Main game file
- `tamagotchi_save.json`: Save file (created automatically)
- `requirements.txt`: Python dependencies

## Development

The game is built with:
- **Python 3.6+**
- **Pygame**: For graphics and input handling
- **JSON**: For save file management
- **Time-based mechanics**: Real-world time affects pet stats

Enjoy taking care of your pixelated companion! 🎮
