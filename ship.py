import uuid
import logging
from geopy.point import Point
from geopy.distance import distance

from module.Engine import EngineRoom
from module.Gun import Gun
from module.TorpedoLauncher import TorpedoLauncher
from module.ShipSpeedResist import Ship as ShipPhysics # Renamed to avoid conflict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Ship:
    """
    The Ship class serves as a central container for all ship-specific systems and properties.
    It encapsulates the existing Python modules and integrates the physics model.
    """

    def __init__(self, name, initial_location, length, displacement, engine_power,
                 num_guns=1, num_torpedo_launchers=1):
        self.id = str(uuid.uuid4())
        self.name = name
        self.hp = 1000 # Example initial HP
        self.location = Point(initial_location) # geopy.point.Point object
        self.direction = 0 # 0-359 degrees, 0 is North, 90 is East
        self.speed = 0 # Current speed in knots
        self.target_speed = 0 # Desired speed in knots
        self.target_direction = 0 # Desired direction in degrees
        self.acceleration_rate = 100 # knots per hour
        self.deceleration_rate = 100 # knots per hour
        self.turning_rate = 360 # degrees per hour

        # Ship components with HP
        self.components = {
            "engine_room": {"module": None, "hp": 100},
            "guns": [],
            "torpedo_launchers": []
        }

        # Time management for internal simulation
        self.current_time = 0.0 # in hours

        # Command queue for player commands
        self.command_queue = []

        # Ship components
        self.engine_room = EngineRoom(
            staff_on_duty=20, staff_off_duty=70,
            boilers="艦本式呂號専烧鍋爐4座", engines="艦本式渦輪引擎（2座2軸）",
            power=engine_power, max_speed=38, range_distance=5000,
            speed=0, direction=EngineRoom.STOPPED, cruise_speed=12
        )
        self.components["engine_room"]["module"] = self.engine_room

        # Pass reload_time to Gun and TorpedoLauncher, converting hours to minutes for their internal logic
        self.guns = [Gun(staff_on_duty=5, staff_off_duty=10, reload_time=5.0) for _ in range(num_guns)] # 5 minutes reload
        for gun in self.guns:
            self.components["guns"].append({"module": gun, "hp": 50}) # Example HP for guns

        self.torpedo_launchers = [TorpedoLauncher(
            staff_on_duty=5, staff_off_duty=10, num_tubes=3,
            reload_time=1.0, full_reload_time=90.0, torpedoes=6, tube_rotation=True # 1 minute per tube, 90 min full
        ) for _ in range(num_torpedo_launchers)]
        for launcher in self.torpedo_launchers:
            self.components["torpedo_launchers"].append({"module": launcher, "hp": 75}) # Example HP for launchers

        self.physics_model = ShipPhysics(length=length, displacement=displacement, engine_power=engine_power)

        # Crew and communication (placeholders for now)
        self.crew_agents = []
        self.communication_channels = {}
        self.bridge_personnel = []
        self.last_gun_fire_time = -1000
        self.gun_cooldown = 0.1 # hours
        self.last_torpedo_launch_time = -1000
        self.torpedo_cooldown = 0.2 # hours

    def update(self, delta_time):
        """
        Updates the ship's state, including movement based on engine output and physics,
        and module states.
        delta_time is in hours.
        """
        self.current_time += delta_time

        # Process commands from the queue
        self._process_commands()
        
        # Calculate target speed based on engine power setting
        # Assuming engine_room.current_power_percentage is a value between 0 and 100
        # The physics model calculates speed in m/s, convert to knots
        target_speed_mps = self.physics_model.calculate_speed(self.engine_room.current_power_percentage)
        self.target_speed = target_speed_mps * 1.94384 # Convert m/s to knots

        # Apply acceleration/deceleration
        if self.speed < self.target_speed:
            self.speed += self.acceleration_rate * delta_time
            if self.speed > self.target_speed:
                self.speed = self.target_speed
        elif self.speed > self.target_speed:
            self.speed -= self.deceleration_rate * delta_time
            if self.speed < self.target_speed:
                self.speed = self.target_speed

        # Apply turning mechanics
        if self.direction != self.target_direction:
            diff = (self.target_direction - self.direction + 360) % 360
            turn_amount = self.turning_rate * delta_time

            if diff > 180: # Turn left
                self.direction = (self.direction - min(turn_amount, 360 - diff) + 360) % 360
            else: # Turn right
                self.direction = (self.direction + min(turn_amount, diff)) % 360

            # Ensure direction is exactly target_direction if close enough
            if abs(self.direction - self.target_direction) < turn_amount or \
               abs(self.direction - self.target_direction - 360) < turn_amount or \
               abs(self.direction - self.target_direction + 360) < turn_amount:
                self.direction = self.target_direction

        # Move the ship
        self.move(delta_time)

        # Update module states (e.g., guns reloading, torpedo launchers)
        for gun in self.guns:
            gun.update(delta_time)
            # If gun is out of ammo and idle, initiate reload
            if not gun.ammo_loaded and gun.state == gun.IDLE:
                gun.load_ammo()
        
        for launcher in self.torpedo_launchers:
            launcher.update(delta_time)
            # If launcher has empty tubes and is idle, initiate reload
            if any(tube is None for tube in launcher.tubes) and launcher.torpedoes > 0 and launcher.state == launcher.IDLE:
                launcher.load_torpedoes() # Use load_torpedoes for individual tube loading
            elif all(tube is None for tube in launcher.tubes) and launcher.torpedoes > 0 and launcher.state == launcher.IDLE:
                launcher.reload() # Use reload for full reload if all tubes are empty

    def _process_commands(self):
        """Processes commands from the command queue."""
        while self.command_queue:
            command = self.command_queue.pop(0)
            logging.info(f"Processing command for {self.name}: {command}")
            
            action = command.get("action")
            params = command.get("parameters", {})

            if action == "set_speed":
                speed = params.get("knots")
                if speed is not None:
                    self.set_engine_speed(float(speed))
                else:
                    logging.warning(f"Missing 'knots' parameter for set_speed: {command}")

            elif action == "set_direction":
                direction = params.get("degrees")
                if direction is not None:
                    self.set_direction(int(direction))
                else:
                    logging.warning(f"Missing 'degrees' parameter for set_direction: {command}")

            elif action == "fire_guns":
                target_id = params.get("target_id")
                if target_id is not None:
                    self.fire_guns(target_location=target_id)
                else:
                    logging.warning(f"Missing 'target_id' for fire_guns: {command}")

            elif action == "launch_torpedoes":
                target_id = params.get("target_id")
                if target_id is not None:
                    self.launch_torpedoes(target_location=target_id)
                else:
                    logging.warning(f"Missing 'target_id' for launch_torpedoes: {command}")
            
            else:
                logging.warning(f"Unknown or malformed command: {command}")

    def take_damage(self, damage_amount, hit_location):
        """
        Applies damage to the ship and potentially its modules based on hit_location.
        If a component's HP drops to zero, it becomes inoperable.
        """
        self.hp -= damage_amount
        if self.hp < 0:
            self.hp = 0
        logging.info(f"{self.name} took {damage_amount} damage at {hit_location}. Current HP: {self.hp}")

        # Apply damage to specific modules based on hit_location
        if hit_location == "engine_room":
            self._damage_component("engine_room", damage_amount)
        elif hit_location == "guns":
            # Damage a random gun for simplicity, or iterate through all
            if self.components["guns"]:
                import random
                damaged_gun = random.choice(self.components["guns"])
                self._damage_component(damaged_gun, damage_amount)
        elif hit_location == "torpedo_launchers":
            # Damage a random torpedo launcher
            if self.components["torpedo_launchers"]:
                import random
                damaged_launcher = random.choice(self.components["torpedo_launchers"])
                self._damage_component(damaged_launcher, damage_amount)
        # Add more hit locations and corresponding module damage logic as needed

    def _damage_component(self, component_info, damage_amount):
        """Helper to apply damage to a specific component."""
        if isinstance(component_info, str): # For top-level components like engine_room
            component = self.components[component_info]
        else: # For items in lists like guns or torpedo_launchers
            component = component_info

        component["hp"] -= damage_amount
        if component["hp"] < 0:
            component["hp"] = 0
            logging.warning(f"{component['module'].__class__.__name__} is inoperable due to 0 HP!")
            # Set module state to DAMAGED or similar if it has such a state
            if hasattr(component["module"], 'damage'):
                component["module"].damage(component["module"].DAMAGE_LEVELS['SEVERE'])
        logging.info(f"{component['module'].__class__.__name__} HP: {component['hp']}")

    def get_status(self):
        """Returns a comprehensive status report of the ship and its modules."""
        status_report = f"--- {self.name} Status ---\n"
        status_report += f"ID: {self.id}\n"
        status_report += f"HP: {self.hp}\n"
        status_report += f"Location: {self.location.latitude:.4f}, {self.location.longitude:.4f}\n"
        status_report += f"Direction: {self.direction}°\n"
        status_report += f"Speed: {self.speed} knots\n"
        status_report += f"Current Time: {self.current_time:.2f} hours\n"
        status_report += f"\n--- Engine Room ---\nHP: {self.components['engine_room']['hp']}\n{self.engine_room}\n"
        for i, gun_info in enumerate(self.components["guns"]):
            status_report += f"\n--- Gun {i+1} ---\nHP: {gun_info['hp']}\n{gun_info['module']}\n"
        for i, launcher_info in enumerate(self.components["torpedo_launchers"]):
            status_report += f"\n--- Torpedo Launcher {i+1} ---\nHP: {launcher_info['hp']}\n{launcher_info['module']}\n"
        return status_report

    def set_engine_speed(self, desired_speed_knots):
        """
        Sets the desired speed for the ship. The engine room will adjust its power
        to try and reach this speed, and the ship's physics model will handle
        acceleration/deceleration.
        """
        # Convert desired speed from knots to m/s for the physics model
        desired_speed_mps = desired_speed_knots * 0.514444

        # Find the power percentage required to achieve this speed
        # This is a simplified approach; a more robust solution might involve
        # iterating or using a reverse lookup on the physics model.
        # For now, we'll assume a linear relationship or a direct mapping
        # from desired speed to engine power percentage.
        # A better approach would be to have the engine room manage its power
        # based on a target speed, and the physics model calculates actual speed.
        # Let's set the target speed directly here for now, and the engine room
        # will try to match it.
        self.target_speed = desired_speed_knots
        
        # Update engine room's target speed, which it will use to adjust power
        self.engine_room.set_target_speed(desired_speed_knots)

    def set_direction(self, direction):
        """Sets the target direction for the ship."""
        if 0 <= direction <= 359:
            self.target_direction = direction
            logging.info(f"{self.name} target direction set to {self.target_direction}°.")
        else:
            logging.warning("Direction must be between 0 and 359 degrees.")

    def fire_guns(self, target_location):
        """Delegates to appropriate Gun instances, respecting cooldown."""
        if (self.current_time - self.last_gun_fire_time) >= self.gun_cooldown:
            fired_any = False
            for gun in self.guns:
                if gun.state == gun.IDLE and gun.ammo_loaded:
                    gun.fire()
                    logging.info(f"{self.name}'s gun fired at {target_location}.")
                    fired_any = True
                    self.last_gun_fire_time = self.current_time
                    break # Only fire one gun per command for simplicity
                else:
                    logging.info(f"{self.name}'s gun cannot fire (State: {gun.state}, Ammo Loaded: {gun.ammo_loaded}).")
            if not fired_any:
                logging.warning(f"{self.name}: No guns could be fired.")
        else:
            logging.info(f"{self.name}: Guns are on cooldown. Time remaining: {self.gun_cooldown - (self.current_time - self.last_gun_fire_time):.2f} hours.")

    def launch_torpedoes(self, target_location):
        """Delegates to appropriate TorpedoLauncher instances, respecting cooldown."""
        if (self.current_time - self.last_torpedo_launch_time) >= self.torpedo_cooldown:
            launched_any = False
            for launcher in self.torpedo_launchers:
                if launcher.state == launcher.IDLE:
                    launcher.launch_torpedo()
                    logging.info(f"{self.name}'s torpedo launcher launched at {target_location}.")
                    launched_any = True
                    self.last_torpedo_launch_time = self.current_time
                    break # Only launch from one launcher per command for simplicity
                else:
                    logging.info(f"{self.name}'s torpedo launcher cannot launch (State: {launcher.state}).")
            if not launched_any:
                logging.warning(f"{self.name}: No torpedoes could be launched.")
        else:
            logging.info(f"{self.name}: Torpedo launchers are on cooldown. Time remaining: {self.torpedo_cooldown - (self.current_time - self.last_torpedo_launch_time):.2f} hours.")

    def move(self, hours):
        """Calculates new location based on current speed and direction, using geopy.distance.distance."""
        if self.speed > 0:
            # Calculate distance traveled in nautical miles
            distance_nm = self.speed * hours
            
            # Convert nautical miles to meters for geopy.distance
            distance_m = distance_nm * 1852 # 1 nautical mile = 1852 meters

            # Calculate new location using geopy.distance
            # geopy.distance.distance expects distance in meters
            # The bearing is the direction in degrees
            new_location = distance(meters=distance_m).destination(point=self.location, bearing=self.direction)
            self.location = new_location
            logging.info(f"{self.name} moved to {self.location.latitude:.4f}, {self.location.longitude:.4f} at {self.speed} knots for {hours} hours.")
        else:
            logging.info(f"{self.name} is stopped.")

    def hit_on(self, by):
        """Handles damage based on weapon type. (Placeholder)"""
        logging.info(f"{self.name} was hit by {by}.")
        # TODO: Implement actual damage calculation based on 'by' (e.g., shell, torpedo)

    def process_crew_actions(self):
        """Iterates through crew_agents to allow them to perform actions based on their roles and communication. (Placeholder)"""
        pass

    def process_player_command(self, command):
        """Adds player commands to the command queue for interpretation and action."""
        logging.info(f"Player command received for {self.name}: {command}. Adding to queue.")
        self.command_queue.append(command)

    def handle_casualties(self, casualties_data):
        """Updates crew status and reassigns roles if necessary. (Placeholder)"""
        logging.info(f"{self.name} handling casualties: {casualties_data}")
        # TODO: Implement actual casualty handling and role reassignment
        pass

    def is_alive(self):
        """Checks if the ship is still alive."""
        return self.hp > 0

    def __str__(self):
        return self.get_status()

if __name__ == "__main__":
    # Example Usage
    ship1 = Ship(
        name="Fubuki",
        initial_location=(35.6895, 139.6917), # Tokyo coordinates
        length=118.5, # meters
        displacement=1750, # tons
        engine_power=50000, # kW
        num_guns=2,
        num_torpedo_launchers=1
    )

    logging.info(f"Initial status of {ship1.name}:\n{ship1.get_status()}")

    ship1.engine_room.start_operations()
    
    # Simulate multiple commands
    ship1.process_player_command("set_speed 25")
    ship1.process_player_command("set_direction 90")
    ship1.process_player_command("fire_guns")
    ship1.process_player_command("launch_torpedoes")

    # Simulate 1 hour of movement and command processing
    ship1.update(delta_time=1)
    logging.info(f"Status of {ship1.name} after 1 hour:\n{ship1.get_status()}")

    # Try to fire again immediately (should be reloading)
    ship1.process_player_command("fire_guns target_enemy_ship_A")
    ship1.process_player_command("launch_torpedoes target_enemy_ship_B")
    ship1.update(delta_time=0.01) # Small delta to check state
    logging.info(f"Status of {ship1.name} after small update (reload check):\n{ship1.get_status()}")

    # Simulate enough time passing for reloads
    # Guns reload in 5 minutes (0.0833 hours)
    # Torpedoes reload in 1 minute (0.0167 hours) per tube, full reload 90 minutes (1.5 hours)

    # Simulate time for gun to reload after initial fire
    ship1.update(delta_time=5.0/60.0 + 0.01) # Pass enough time for gun reload
    ship1.process_player_command("fire_guns target_enemy_ship_A") # Should now fire
    logging.info(f"Status of {ship1.name} after gun reload and re-fire:\n{ship1.get_status()}")

    # Simulate time for torpedo launcher to reload after initial launch
    ship1.update(delta_time=1.0/60.0 + 0.01) # Pass enough time for one torpedo tube to reload
    ship1.process_player_command("launch_torpedoes target_enemy_ship_B") # Should now launch
    logging.info(f"Status of {ship1.name} after torpedo reload and re-launch:\n{ship1.get_status()}")

    # Simulate taking damage
    ship1.take_damage(damage_amount=50, hit_location="Amidships")
    logging.info(f"Status of {ship1.name} after taking damage:\n{ship1.get_status()}")