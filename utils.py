import json
from geopy.point import Point
from world import World
from ship import Ship

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