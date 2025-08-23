import time
import json
import os
from dotenv import load_dotenv

from world import World
from ship import Ship
from game_manager import Game # Import the new Game class

load_dotenv() # Load environment variables from .env file

def main():
    print("--- Welcome to the Naval Simulation (Zork-style) ---")
    print("You are the Commander of the Fubuki destroyer.")
    print("Issue commands to your officers to control the ship.")
    print("Type 'exit' to quit.")

    # Initialize World and Ships for the game
    world = World()
    fubuki = Ship("Fubuki", initial_location=(35.6895, 139.6917), length=100, displacement=5000, engine_power=60000)
    enemy_ship = Ship("Enemy Destroyer", initial_location=(35.7895, 139.7917), length=120, displacement=6000, engine_power=70000)
    world.add_object(fubuki)
    world.add_object(enemy_ship)
    
    # Use a fixed thread_id for a single-player, direct execution game
    game_instance = Game("single_player_game", world, fubuki, enemy_ship)

    running = True
    while running:
        user_input = input("\nCommander, what are your orders? ").strip()
        if user_input.lower() == 'exit':
            running = False
            break
        
        if not user_input:
            print("Please provide an order.")
            continue

        # Process the turn using the Game instance
        responses = game_instance.turn(user_input)

        # Display responses from agents
        if isinstance(responses, list):
            for msg in responses:
                print(f"{msg['role']}: {msg['content']}")
        else:
            print(f"Game response: {responses}")

    print("Game Over!")
    print(f"{fubuki.name} alive: {fubuki.is_alive()}")
    print(f"{enemy_ship.name} alive: {enemy_ship.is_alive()}")

if __name__ == "__main__":
    main()