import math
from ship import Ship

class World:
    def __init__(self):
        self.ships = []
        self.projectiles = []
        self.environment = {}
        self.game_time = 0.0
        self.timer = None # Placeholder for timer mechanism
        self.global_channels = {} # Placeholder for global communication channels
        self.game_objects = [] # General list for all game objects

    def add_object(self, obj):
        self.game_objects.append(obj)
        if isinstance(obj, Ship):
            self.ships.append(obj)
        # Add logic for other types of objects if needed (e.g., Projectile)

    def remove_object(self, obj):
        if obj in self.game_objects:
            self.game_objects.remove(obj)
        if isinstance(obj, Ship) and obj in self.ships:
            self.ships.remove(obj)
        # Add logic for other types of objects if needed

    def update(self, delta_time):
        self.game_time += delta_time

        # Update ships
        for ship in self.ships:
            ship.update(delta_time)

        # Update projectiles (placeholder)
        # for projectile in self.projectiles:
        #     projectile.update(delta_time)

        self.check_collisions()

    def check_collisions(self):
        # Basic collision detection: check for collisions between ships and projectiles
        # This is a simplified example and would need more sophisticated logic for a real game
        for ship in self.ships:
            for projectile in self.projectiles:
                # Placeholder for actual collision logic
                # For demonstration, let's assume a simple distance-based collision
                # In a real scenario, you'd compare bounding boxes or more complex shapes
                distance = math.sqrt(
                    (ship.location.latitude - projectile.location.latitude)**2 +
                    (ship.location.longitude - projectile.location.longitude)**2
                )
                # Assuming a collision if distance is less than a certain threshold
                collision_threshold = 0.1 # Example value, adjust as needed
                if distance < collision_threshold:
                    print(f"Collision detected between {ship.name} and a projectile!")
                    # Assuming projectiles have a damage attribute
                    ship.take_damage(projectile.damage, "hull") # Placeholder hit_location
                    # Remove projectile after collision (or mark as inactive)
                    self.remove_object(projectile)
                    break # Only one projectile can hit a ship at a time in this simple model

    def get_ship_by_id(self, ship_id):
        for ship in self.ships:
            if ship.id == ship_id:
                return ship
        return None

    def get_all_ships_status(self):
        statuses = {}
        for ship in self.ships:
            statuses[ship.name] = ship.get_status()
        return statuses

    # run_game_loop is not implemented as per instructions.