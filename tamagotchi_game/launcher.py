#!/usr/bin/env python3
"""
Tamagotchi Game Launcher
Checks dependencies and launches the game
"""

import sys
import subprocess

def check_pygame():
    try:
        import pygame
        print("✓ Pygame is installed")
        return True
    except ImportError:
        print("✗ Pygame not found")
        return False

def install_pygame():
    print("Installing pygame...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("✓ Pygame installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install pygame")
        return False

def main():
    print("🎮 Pixelated Tamagotchi Game Launcher")
    print("=" * 40)
    
    if not check_pygame():
        response = input("Would you like to install pygame? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_pygame():
                print("Please install pygame manually: pip install pygame")
                return
        else:
            print("Pygame is required to run the game.")
            return
    
    print("\n🚀 Starting Tamagotchi Game...")
    print("=" * 40)
    
    # Import and run the game
    try:
        from tamagotchi import TamagotchiGame
        game = TamagotchiGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        print("Make sure tamagotchi.py is in the same directory")

if __name__ == "__main__":
    main()
