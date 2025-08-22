import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EngineRoom:
    """
    EngineRoom class to simulate the operations of an engine room on a ship.

    Parameters:
        staff_on_duty: Number of staff currently on duty.
        staff_off_duty: Number of staff currently off duty.
        boilers: Description of the boilers in the engine room.
        engines: Description of the engines in the engine room.
        power: Power output of the engines.
        max_speed: Maximum speed of the ship.
        range_distance: Range of the ship in nautical miles.
        speed: Current Speed of the ship.
        direction: Current direction of the ship ('forward', 'backward', 'stopped').

    States:
        IDLE: The engine room is idle and ready for operations.
        OPERATING: The engine room is operating normally.
        MAINTENANCE: The engine room is undergoing maintenance.
        FAULT: The engine room has encountered a fault that requires attention.
        DAMAGED: The engine room has sustained damage.

    Fault Levels:
        IMMEDIATE_REPAIR: The fault can be repaired immediately.
        FIELD_REPAIR: The fault requires the engine room to be taken out of the battlefield for repair.
        UNREPAIRABLE: The fault is unrepairable and the engine room is unusable.

    Damage Levels:
        MINOR: The damage is minor and may not affect functionality significantly.
        MODERATE: The damage is moderate and may affect functionality.
        SEVERE: The damage is severe and the engine room is likely unusable.

    Directions:
        FORWARD: The ship is moving forward.
        BACKWARD: The ship is moving backward.
        STOPPED: The ship is stopped.

    Example Usage:
        >>> engine_room = EngineRoom(
        ...     staff_on_duty=20,
        ...     staff_off_duty=70,
        ...     boilers="艦本式呂號専烧鍋爐4座",
        ...     engines="艦本式渦輪引擎（2座2軸）",
        ...     power=50000,  # horse power
        ...     max_speed=38,  # knot
        ...     range_distance=5000,  # nautical miles
        ...     speed=0,
        ...     direction=EngineRoom.STOPPED
        ... )
        >>> engine_room.start_operations()
        2023-10-05 12:34:56,789 - INFO - Engine room operations started.
        >>> engine_room.add_casualties(3)
        2023-10-05 12:34:56,790 - INFO - 3 casualties occurred. Staff on duty: 17.
        >>> engine_room.recall_staff(5)
        2023-10-05 12:34:56,791 - INFO - 5 staff recalled. Staff on duty: 22.
        >>> engine_room.set_speed(20)
        2023-10-05 12:34:56,792 - INFO - Speed set to 20 knots.
        >>> engine_room.set_direction(EngineRoom.FORWARD)
        2023-10-05 12:34:56,793 - INFO - Direction set to forward.
        >>> engine_room.fault(EngineRoom.FAULT_LEVELS['IMMEDIATE_REPAIR'])
        2023-10-05 12:34:56,794 - INFO - Engine room fault occurred: Immediate Repair
        >>> engine_room.damage(EngineRoom.DAMAGE_LEVELS['MINOR'])
        2023-10-05 12:34:56,795 - INFO - Engine room has been damaged: Minor Damage
    """

    IDLE = 'idle'
    OPERATING = 'operating'
    MAINTENANCE = 'maintenance'
    FAULT = 'fault'
    DAMAGED = 'damaged'

    FAULT_LEVELS = {
        'IMMEDIATE_REPAIR': 'Immediate Repair',
        'FIELD_REPAIR': 'Field Repair',
        'UNREPAIRABLE': 'Unrepairable'
    }

    DAMAGE_LEVELS = {
        'MINOR': 'Minor Damage',
        'MODERATE': 'Moderate Damage',
        'SEVERE': 'Severe Damage'
    }

    FORWARD = 'forward'
    BACKWARD = 'backward'
    STOPPED = 'stopped'

    DIRECTIONS = [FORWARD, BACKWARD, STOPPED]

    def __init__(self, staff_on_duty, staff_off_duty,
                    boilers, engines, power, max_speed, range_distance,
                    speed, direction, cruise_speed):
        self.state = self.IDLE
        self.staff_on_duty = staff_on_duty
        self.staff_off_duty = staff_off_duty
        self.boilers = boilers
        self.engines = engines
        self.power = power
        self.max_speed = max_speed
        self.range_distance = range_distance
        self.speed = speed
        self.direction = direction
        self.cruise_speed = cruise_speed
        self.fault_level = None
        self.damage_level = None
        self.current_power_percentage = 0.0

    def start_operations(self):
        if self.state == self.IDLE and self.staff_on_duty > 1:
            self.state = self.OPERATING
            logging.info("Engine room operations started.")
        else:
            logging.info(f"Cannot start operations while in state: {self.state}")

    def stop_operations(self):
        if self.state == self.OPERATING and self.staff_on_duty > 1:
            self.state = self.IDLE
            logging.info("Engine room operations stopped.")
        else:
            logging.info(f"Cannot stop operations while in state: {self.state}")

    def add_casualties(self, casualties):
        self.staff_on_duty -= casualties
        if self.staff_on_duty < 0:
            self.staff_on_duty = 0
        logging.info(f"{casualties} casualties occurred. Staff on duty: {self.staff_on_duty}.")

    def recall_staff(self, staff):
        if staff <= self.staff_off_duty:
            self.staff_on_duty += staff
            self.staff_off_duty -= staff
            logging.info(f"{staff} staff recalled. Staff on duty: {self.staff_on_duty}.")
        elif self.staff_off_duty > 0:
            self.staff_on_duty += self.staff_off_duty
            self.staff_off_duty = 0
            logging.info(f"{self.staff_off_duty} staff recalled. Staff on duty: {self.staff_on_duty}.")
        else:
            logging.info(f"Not enough staff off duty to recall {staff} staff. Staff off duty: {self.staff_off_duty}.")

    def set_speed(self, speed):
        if self.state == self.OPERATING:
            max_speed = self.max_speed
            if self.direction == self.BACKWARD:
                max_speed = 12
            if 0 <= speed <= max_speed:
                self.speed = speed
                logging.info(f"Speed set to {self.speed} knots.")
            else:
                logging.info(f"Invalid speed. Must be between 0 and {max_speed} knots to drive {self.direction}.")
        else:
            logging.info(f"Cannot set Speed while in state: {self.state}")

    def set_direction(self, direction):
        if self.state == self.OPERATING:
            if direction in self.DIRECTIONS:
                self.direction = direction
                if self.direction == self.BACKWARD:
                    if self.speed > 12:
                        self.speed = 12
                logging.info(f"Direction set to {self.direction}, speed set to {self.speed}.")
            else:
                logging.info(f"Invalid direction. Must be one of {self.DIRECTIONS}.")
        else:
            logging.info(f"Cannot set direction while in state: {self.state}")

    def fault(self, level):
        if self.state in [self.OPERATING, self.IDLE]:
            self.state = self.FAULT
            self.fault_level = level
            logging.info(f"Engine room fault occurred: {self.FAULT_LEVELS[level]}")
        else:
            logging.info(f"Fault cannot occur in state: {self.state}")

    def damage(self, level):
        self.state = self.DAMAGED
        self.damage_level = level
        logging.info(f"Engine room has been damaged: {self.DAMAGE_LEVELS[level]}")

    def maintenance(self):
        if self.state == self.IDLE:
            self.state = self.MAINTENANCE
            logging.info("Maintenance started.")
            # Simulate maintenance process
            self.state = self.IDLE
            logging.info("Maintenance completed.")
        else:
            logging.info(f"Cannot perform maintenance while in state: {self.state}")

    def set_target_speed(self, target_speed):
        """Sets the target speed and adjusts power percentage accordingly."""
        if self.state == self.OPERATING:
            if 0 <= target_speed <= self.max_speed:
                self.speed = target_speed
                self.current_power_percentage = (self.speed / self.max_speed) * 100
                if self.current_power_percentage > 100:
                    self.current_power_percentage = 100
                logging.info(f"Target speed set to {self.speed} knots, power at {self.current_power_percentage:.2f}%.")
            else:
                logging.warning(f"Target speed {target_speed} is out of range (0-{self.max_speed}).")
        else:
            logging.info(f"Cannot set target speed while in state: {self.state}")

    def get_status(self):
        """Returns a dictionary representing the engine room's status."""
        return {
            "state": self.state,
            "speed": self.speed,
            "direction": self.direction,
            "power_percentage": self.current_power_percentage,
            "fault_level": self.fault_level,
            "damage_level": self.damage_level
        }
    def __str__(self):
        fault_level = self.fault_level if self.fault_level else "None"
        damage_level = self.damage_level if self.damage_level else "None"
        return (f"Engine Room Status:\n"
                f"State: {self.state}\n"
                f"Staff On Duty: {self.staff_on_duty}\n"
                f"Staff Off Duty: {self.staff_off_duty}\n"
                f"Boilers: {self.boilers}\n"
                f"Engines: {self.engines}\n"
                f"Power: {self.power} 匹\n"
                f"Max Speed: {self.max_speed} 節\n"
                f"Range Distance: {self.range_distance} 海里\n"
                f"Speed: {self.speed} 節\n"
                f"Cruise Speed: {self.cruise_speed} 節\n"
                f"Direction: {self.direction}\n"
                f"Fault Level: {fault_level}\n"
                f"Damage Level: {damage_level}")

# Example usage
if __name__ == "__main__":
    engine_room = EngineRoom(
        staff_on_duty=20,
        staff_off_duty=70,
        boilers="艦本式呂號専烧鍋爐4座",
        engines="艦本式渦輪引擎（2座2軸）",
        power=50000,  # horse power
        max_speed=38,  # knot
        range_distance=5000,  # nautical miles
        cruise_speed=12,
        speed=0,
        direction=EngineRoom.STOPPED
    )
    engine_room.start_operations()
    engine_room.add_casualties(3)
    engine_room.recall_staff(5)
    engine_room.set_speed(20)
    engine_room.set_direction(EngineRoom.FORWARD)
    engine_room.fault(EngineRoom.FAULT_LEVELS['IMMEDIATE_REPAIR'])
    engine_room.damage(EngineRoom.DAMAGE_LEVELS['MINOR'])
    engine_room.maintenance()