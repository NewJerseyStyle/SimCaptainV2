import time
from world import World
from ship import Ship

from geopy.point import Point
from geopy.distance import distance
import math
import time
import json
import os
from dotenv import load_dotenv
from world import World
from ship import Ship
from agents import WeaponsOfficerAgent, HelmOfficerAgent, EngineeringOfficerAgent, CommanderAgent, OfficerAgent

load_dotenv() # Load environment variables from .env file

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Point):
            return {"latitude": obj.latitude, "longitude": obj.longitude, "altitude": obj.altitude}
        return super().default(obj)

def serialize_game_state(world: World, player_ship: Ship, enemy_ship: Ship) -> str:
    """
    Serializes the current state of the world and ships into a string for agents.
    """
    state = {
        "game_time": world.game_time,
        "player_ship": {
            "name": player_ship.name,
            "hp": player_ship.hp,
            "location": player_ship.location,
            "direction": player_ship.direction,
            "speed": player_ship.speed,
            "guns_status": [gun.get_status() for gun in player_ship.guns],
            "torpedo_launchers_status": [tl.get_status() for tl in player_ship.torpedo_launchers],
            "engine_status": player_ship.engine_room.get_status(),
            "command_queue": player_ship.command_queue
        },
        "enemy_ship": {
            "name": enemy_ship.name,
            "hp": enemy_ship.hp,
            "location": enemy_ship.location,
            "direction": enemy_ship.direction,
            "speed": enemy_ship.speed,
            "guns_status": [gun.get_status() for gun in enemy_ship.guns],
            "torpedo_launchers_status": [tl.get_status() for tl in enemy_ship.torpedo_launchers],
            "engine_status": enemy_ship.engine_room.get_status(),
            "command_queue": enemy_ship.command_queue
        },
        "projectiles": [
            {"id": p.id, "type": p.type, "location": p.location, "target_ship_id": p.target_ship_id}
            for p in world.projectiles
        ]
    }
    return json.dumps(state, indent=2, cls=CustomEncoder)

def calculate_bearing(point_a: Point, point_b: Point) -> float:
    """Calculate the bearing from point A to point B."""
    lat1 = math.radians(point_a.latitude)
    lat2 = math.radians(point_b.latitude)
    diff_lon = math.radians(point_b.longitude - point_a.longitude)

    x = math.sin(diff_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_lon))
    
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def main():
    world = World()

    # Initialize ships
    fubuki = Ship("Fubuki", initial_location=(35.6895, 139.6917), length=100, displacement=5000, engine_power=60000)
    enemy_ship = Ship("Enemy Destroyer", initial_location=(35.7895, 139.7917), length=120, displacement=6000, engine_power=70000)

    world.add_object(fubuki)
    world.add_object(enemy_ship)

    # Instantiate player's officer agents
    weapons_officer = WeaponsOfficerAgent()
    helm_officer = HelmOfficerAgent()
    engineering_officer = EngineeringOfficerAgent()

    # Instantiate AI Commander for the enemy ship
    ai_commander = OfficerAgent(bot_name="AICommander", prompt_path="prompts/ai_commander_prompt.txt")

    running = True
    last_frame_time = time.time()
    game_duration = 0
    max_game_duration = 600  # seconds, increased for longer gameplay

    print("--- Welcome to the Naval Simulation ---")
    print("You are the Commander of the Fubuki destroyer.")
    print("Issue commands to your officers to control the ship.")
    print("Type 'help' for a list of commands, or 'exit' to quit.")
    
    # Initial report from Helm Officer
    bearing = calculate_bearing(fubuki.location, enemy_ship.location)
    dist = distance(fubuki.location, enemy_ship.location).kilometers
    print(f"\nHelm Officer: 'Commander, we have an enemy vessel on bearing {bearing:.0f}, distance {dist:.2f} kilometers.'")

    while running:
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        world.update(delta_time)
        game_duration += delta_time

        # Serialize game state for agents
        game_state_str = serialize_game_state(world, fubuki, enemy_ship)

        # Display status
        print("\n--- World Status ---")
        for ship in world.ships:
            print(f"Ship: {ship.name} (ID: {ship.id}) - HP: {ship.hp}, Location: {ship.location}, Speed: {ship.speed}, Direction: {ship.direction}")
            if ship.command_queue:
                print(f"  Command Queue: {ship.command_queue}")
            else:
                print("  Command Queue: Empty")

        # Player Input (Natural Language Command)
        player_command_input = input("\nCommander, what are your orders? ").strip()

        if player_command_input.lower() == 'exit':
            running = False
        elif player_command_input.lower() == 'help':
            print("\n--- Command Help ---")
            print("Format: 'officer, your command'")
            print("Available officers: 'weapons', 'helm', 'engineering'")
            print("\nExample Commands:")
            print("  'helm, turn to starboard'")
            print("  'helm, set course to 180 degrees'")
            print("  'engineering, increase speed to 20 knots'")
            print("  'weapons, fire guns at enemy destroyer'")
            print("  'weapons, launch torpedoes at target 1234'")

        elif player_command_input:
            parts = player_command_input.split(',', 1)
            if len(parts) == 2:
                recipient = parts[0].strip().lower()
                command_text = parts[1].strip()

                officer_agent = None
                if "weapons" in recipient:
                    officer_agent = weapons_officer
                elif "helm" in recipient:
                    officer_agent = helm_officer
                elif "engineering" in recipient:
                    officer_agent = engineering_officer
                else:
                    print("Unknown officer. Please specify 'weapons', 'helm', or 'engineering'.")

                if officer_agent:
                    print(f"Sending command to {officer_agent.bot_name}...")
                    action, params = officer_agent.process_command(command_text, game_state_str)
                    if action:
                        if "report" in action:
                            # Handle reporting actions immediately
                            if action == "report_status":
                                if "enemy" in command_text.lower():
                                    bearing = calculate_bearing(fubuki.location, enemy_ship.location)
                                    dist = distance(fubuki.location, enemy_ship.location).kilometers
                                    print(f"\nHelm Officer: 'Commander, the enemy is bearing {bearing:.0f} degrees, distance {dist:.2f} kilometers.'")
                                else:
                                    if officer_agent == helm_officer:
                                        print(f"\nHelm Officer: 'Our current heading is {fubuki.direction} degrees at {fubuki.speed} knots, Commander.'")
                                    elif officer_agent == weapons_officer:
                                        gun_status = [gun.get_status() for gun in fubuki.guns]
                                        torpedo_status = [tl.get_status() for tl in fubuki.torpedo_launchers]
                                        print(f"\nWeapons Officer: 'Guns are {gun_status[0]['state']}, {gun_status[0]['rounds_left']} rounds left. Torpedoes are {torpedo_status[0]['state']}, {torpedo_status[0]['torpedoes_in_reserve']} in reserve.'")
                                    elif officer_agent == engineering_officer:
                                        engine_status = fubuki.engine_room.get_status()
                                        print(f"\nEngineering Officer: 'Engine is {engine_status['state']} at {engine_status['power_percentage']:.0f}% power, speed is {engine_status['speed']} knots.'")
                                    else:
                                        print(f"\n{officer_agent.bot_name}: '{fubuki.get_status()}'")
                            else:
                                 print(f"\n{officer_agent.bot_name}: 'I have no report on that, Commander.'")
                        else:
                            # Add action-oriented commands to the queue
                            fubuki.command_queue.append({"action": action, "parameters": params if params is not None else {}})
                            print(f"Command '{action}' with params {params} added to Fubuki's queue.")
                    else:
                        print(f"Officer {officer_agent.bot_name} did not return a valid command.")
            else:
                # Handle general commands without a specific officer
                if "battle station" in player_command_input.lower():
                    print("\nCommander: 'Battle station!'")
                    fubuki.command_queue.append({"action": "set_speed", "parameters": {"knots": 20}})
                    print("Helm Officer: 'Aye, Commander. Increasing speed to 20 knots.'")
                    fubuki.command_queue.append({"action": "fire_guns", "parameters": {"target_id": enemy_ship.id}})
                    print("Weapons Officer: 'Aye, Commander. Guns are ready to fire.'")
                else:
                    print("Invalid command format. Expected: 'officer, natural language command'. Type 'help' for more info.")

        # AI Commander's turn
        print(f"\nAI Commander ({enemy_ship.name}) is processing its turn...")
        ai_order_json = ai_commander.process_command("Formulate a strategic plan based on the current situation.", game_state_str)
        
        if ai_order_json and isinstance(ai_order_json, dict):
            ai_recipient = ai_order_json.get("recipient")
            ai_order_text = ai_order_json.get("order")

            if ai_recipient and ai_order_text:
                ai_officer_agent = None
                if "WeaponsOfficer" in ai_recipient:
                    ai_officer_agent = WeaponsOfficerAgent() # Re-instantiate for simplicity, in a real game these would be persistent
                elif "HelmOfficer" in ai_recipient:
                    ai_officer_agent = HelmOfficerAgent()
                elif "EngineeringOfficer" in ai_recipient:
                    ai_officer_agent = EngineeringOfficerAgent()
                
                if ai_officer_agent:
                    print(f"AI Commander sending order to {ai_officer_agent.bot_name}: '{ai_order_text}'")
                    ai_action, ai_params = ai_officer_agent.process_command(ai_order_text, game_state_str)
                    if ai_action:
                        enemy_ship.command_queue.append({"action": ai_action, "parameters": ai_params if ai_params is not None else {}})
                        print(f"AI Command '{ai_action}' with params {ai_params} added to {enemy_ship.name}'s queue.")
                    else:
                        print(f"AI Officer {ai_officer_agent.bot_name} did not return a valid command.")
                else:
                    print(f"AI Commander specified unknown officer: {ai_recipient}")
            else:
                print("AI Commander did not return a valid recipient or order.")
        else:
            print("AI Commander did not return a valid JSON order.")


        # Break condition: game duration or a ship is destroyed
        if game_duration > max_game_duration or not fubuki.is_alive() or not enemy_ship.is_alive():
            running = False

        # Small delay to prevent busy-waiting and make the simulation observable
        time.sleep(0.1) # Increased delay for better readability of output

    print("Game Over!")
    print(f"{fubuki.name} alive: {fubuki.is_alive()}")
    print(f"{enemy_ship.name} alive: {enemy_ship.is_alive()}")

if __name__ == "__main__":
    main()