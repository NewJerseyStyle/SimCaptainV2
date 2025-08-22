import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Gun:
    """
    Gun class to simulate a firearm with states and conditions.

    States:
        IDLE: The gun is idle and ready to load or fire.
        LOADING: The gun is in the process of loading ammo.
        FIRING: The gun is in the process of firing.
        FAULT: The gun has encountered a fault that requires attention.
        DAMAGED: The gun has sustained damage.

    Fault Levels:
        IMMEDIATE_REPAIR: The fault can be repaired immediately.
        FIELD_REPAIR: The fault requires the gun to be taken out of the battlefield for repair.
        UNREPAIRABLE: The fault is unrepairable and the gun is unusable.

    Damage Levels:
        MINOR: The damage is minor and may not affect functionality significantly.
        MODERATE: The damage is moderate and may affect functionality.
        SEVERE: The damage is severe and the gun is likely unusable.

    Example Usage:
        >>> gun = Gun(staff_on_duty=5)
        >>> gun.load_ammo()
        2023-10-05 12:34:56,789 - INFO - Loading process started.
        >>> gun.fire()
        2023-10-05 12:34:56,790 - INFO - Firing process started.
        >>> gun.fault(Gun.FAULT_LEVELS['IMMEDIATE_REPAIR'])
        2023-10-05 12:34:56,791 - INFO - Gun fault occurred: Immediate Repair
        >>> gun.fault(Gun.FAULT_LEVELS['FIELD_REPAIR'])
        2023-10-05 12:34:56,792 - INFO - Gun fault occurred: Field Repair
        >>> gun.fault(Gun.FAULT_LEVELS['UNREPAIRABLE'])
        2023-10-05 12:34:56,793 - INFO - Gun fault occurred: Unrepairable
        >>> gun.damage(Gun.DAMAGE_LEVELS['MINOR'])
        2023-10-05 12:34:56,794 - INFO - Gun system has been damaged: Minor Damage
        >>> gun.damage(Gun.DAMAGE_LEVELS['MODERATE'])
        2023-10-05 12:34:56,795 - INFO - Gun system has been damaged: Moderate Damage
        >>> gun.damage(Gun.DAMAGE_LEVELS['SEVERE'])
        2023-10-05 12:34:56,796 - INFO - Gun system has been damaged: Severe Damage
        >>> gun.add_casualties(1)
        2023-10-05 12:34:56,797 - INFO - 1 casualties occurred. Staff on duty: 4.
        >>> gun.recall_staff(2)
        2023-10-05 12:34:56,798 - INFO - 2 staff recalled. Staff on duty: 6.
        >>> print(gun)
        Gun Status:
        State: idle
        Staff On Duty: 6
        Breech Locked: True
        Breech Opened: False
        Ammo Loaded: False
        Firing: False
        Shells: 5
        Current Shell: 1
        Fault Level: None
        Damage Level: None
    """

    IDLE = 'idle'
    LOADING = 'loading'
    FIRING = 'firing'
    FAULT = 'fault'
    DAMAGED = 'damaged'
    POST_FIRE = 'post_fire'

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

    def __init__(self, staff_on_duty=0, staff_off_duty=0, reload_time=5.0):
        self.state = self.IDLE
        self.breech_locked = True
        self.breech_opened = False
        self.ammo_loaded = False
        self.firing = False
        self.shells = 5
        self.current_shell = 0
        self.fire_shell_cost = 1
        self.fault_level = None
        self.damage_level = None
        self.staff_on_duty = staff_on_duty
        self.staff_off_duty = staff_off_duty
        self.reload_time = reload_time # in minutes
        self.current_reload_time = 0.0

    def load_ammo(self):
        if self.state == self.IDLE and not self.ammo_loaded:
            self.state = self.LOADING
            logging.info("Loading process started.")
            self.current_reload_time = self.reload_time # Start reload timer
        else:
            logging.info(f"Cannot load ammo while in state: {self.state} or if ammo is already loaded.")

    def fire(self):
        if self.state == self.IDLE and self.ammo_loaded:
            self.state = self.FIRING
            logging.info("Firing process started.")
            self.firing = True
            self.current_shell += self.fire_shell_cost
            if self.current_shell >= self.shells: # Use >= to handle cases where fire_shell_cost might exceed remaining shells
                self.ammo_loaded = False
                logging.info("All shells have been fired. Reload needed.")
            self.state = self.POST_FIRE # Transition to post-fire state to manage cooldown
        else:
            logging.info(f"Cannot fire while in state: {self.state} or if no ammo is loaded.")

    def fault(self, level):
        self.state = self.FAULT
        self.fault_level = level
        logging.info(f"Gun fault occurred: {self.FAULT_LEVELS[level]}")

    def damage(self, level):
        self.state = self.DAMAGED
        self.damage_level = level
        logging.info(f"Gun system has been damaged: {self.DAMAGE_LEVELS[level]}")

    def add_casualties(self, casualties):
        self.staff_on_duty -= casualties
        if self.staff_on_duty < 0:
            self.staff_on_duty = 0
        logging.info(f"{casualties} casualties occurred. Staff on duty: {self.staff_on_duty}.")

    def recall_staff(self, staff):
        if staff > self.staff_off_duty:
            staff = self.staff_off_duty
        self.staff_on_duty += staff
        self.staff_off_duty -= staff
        logging.info(f"{staff} staff recalled. Staff on duty: {self.staff_on_duty}.")

    def update(self, delta_time):
        """Updates the gun's state based on elapsed time."""
        if self.state == self.LOADING:
            self.current_reload_time -= delta_time * 60 # Convert hours to minutes
            if self.current_reload_time <= 0:
                self.breech_locked = False
                self.breech_opened = True
                self.ammo_loaded = True
                logging.info("Ammo loaded successfully.")
                self.state = self.IDLE
        elif self.state == self.FIRING:
            self.firing = False # Firing is instantaneous for now, immediately transition
            self.state = self.IDLE # After firing, it's ready for next command or reload if out of ammo
        elif self.state == self.POST_FIRE:
            # For guns, post-fire means it's ready to be reloaded if out of ammo, or fire again if not.
            # No explicit cooldown timer here, as it's managed by the Ship class for now.
            # The Ship will check if the gun is IDLE and has ammo before firing.
            self.state = self.IDLE
        # Add logic for FAULT and DAMAGED states if they have time-based effects

    def get_status(self):
        """Returns a dictionary representing the gun's status."""
        return {
            "state": self.state,
            "ammo_loaded": self.ammo_loaded,
            "rounds_left": self.shells - self.current_shell,
            "fault_level": self.fault_level,
            "damage_level": self.damage_level
        }
    def __str__(self):
        fault_level = self.fault_level if self.fault_level else "None"
        damage_level = self.damage_level if self.damage_level else "None"
        return (f"Gun Status:\n"
                f"State: {self.state}\n"
                f"Staff On Duty: {self.staff_on_duty}\n"
                f"Staff Off Duty: {self.staff_off_duty}\n"
                f"Breech Locked: {self.breech_locked}\n"
                f"Breech Opened: {self.breech_opened}\n"
                f"Ammo Loaded: {self.ammo_loaded}\n"
                f"Firing: {self.firing}\n"
                f"Shells (Max shell count): {self.shells}\n"
                f"Current Shell (counter): {self.current_shell}\n"
                f"Rounds left: {self.shells - self.current_shell}\n"
                f"Reload Time: {self.reload_time} minutes\n"
                f"Current Reload Time: {self.current_reload_time:.2f} minutes\n"
                f"Fault Level: {fault_level}\n"
                f"Damage Level: {damage_level}")

    # Example usage
if __name__ == "__main__":
    gun = Gun(staff_on_duty=5, staff_off_duty=10, reload_time=0.1) # 6 seconds reload
    print("--- Initial Gun Status ---")
    print(gun)

    print("\n--- Loading Ammo ---")
    gun.load_ammo()
    gun.update(delta_time=0.05/60) # Simulate 0.05 minutes (3 seconds)
    print(gun)
    gun.update(delta_time=0.05/60) # Simulate another 0.05 minutes (3 seconds)
    print(gun)

    print("\n--- Firing Gun ---")
    gun.fire()
    gun.update(delta_time=0.01) # Small update to transition state
    print(gun)

    print("\n--- Firing Gun (no ammo) ---")
    gun.fire() # Should not fire, as ammo_loaded is False

    print("\n--- Loading Ammo Again ---")
    gun.load_ammo()
    gun.update(delta_time=0.1/60) # Simulate 0.1 minutes (6 seconds)
    print(gun)

    print("\n--- Simulating Fault and Damage ---")
    gun.fault(Gun.FAULT_LEVELS['IMMEDIATE_REPAIR'])
    gun.damage(Gun.DAMAGE_LEVELS['MINOR'])
    print(gun)

    print("\n--- Simulating Casualties and Staff Recall ---")
    gun.add_casualties(1)
    gun.recall_staff(2)
    print(gun)