import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TorpedoLauncher:
    """
    TorpedoLauncher class to simulate a torpedo launching system on a ship.

    Parameters:
        staff_on_duty: Number of staff currently on duty.
        staff_off_duty: Number of staff currently off duty.
        num_tubes: Number of torpedo tubes.
        reload_time: Time required to reload a torpedo tube in combat (in minutes).
        full_reload_time: Time required to fully reload all torpedo tubes during battle preparation (in minutes).
        torpedoes: List of torpedoes available for loading.
        tube_rotation: Whether the torpedo tubes can rotate 360 degrees.

    States:
        IDLE: The launcher is idle and ready to load or launch torpedoes.
        LOADING: The launcher is in the process of loading torpedoes.
        READY: The launcher is ready to launch torpedoes.
        LAUNCHING: The launcher is in the process of launching a torpedo.
        POST_LAUNCH: The launcher is in the post-launch state, considering reloading.
        MAINTENANCE: The launcher is undergoing maintenance after combat.
        FAULT: The launcher has encountered a fault that requires attention.
        DAMAGED: The launcher has sustained damage.

    Fault Levels:
        IMMEDIATE_REPAIR: The fault can be repaired immediately.
        FIELD_REPAIR: The fault requires the launcher to be taken out of the battlefield for repair.
        UNREPAIRABLE: The fault is unrepairable and the launcher is unusable.

    Damage Levels:
        MINOR: The damage is minor and may not affect functionality significantly.
        MODERATE: The damage is moderate and may affect functionality.
        SEVERE: The damage is severe and the launcher is likely unusable.

    Example Usage:
        >>> launcher = TorpedoLauncher(
        ...     staff_on_duty=5,
        ...     staff_off_duty=10,
        ...     num_tubes=3,
        ...     reload_time=1,
        ...     full_reload_time=90,
        ...     torpedoes=6,
        ...     tube_rotation=True
        ... )
        >>> launcher.load_torpedoes()
        2023-10-05 12:34:56,789 - INFO - Loading torpedoes started.
        >>> launcher.prepare_launch()
        2023-10-05 12:34:56,790 - INFO - Launch preparation completed.
        >>> launcher.launch_torpedo()
        2023-10-05 12:34:56,791 - INFO - Torpedo launch initiated.
        >>> launcher.post_launch()
        2023-10-05 12:34:56,792 - INFO - Post-launch processing started.
        >>> launcher.reload()
        2023-10-05 12:34:56,793 - INFO - Torpedo reload started.
        >>> launcher.maintenance()
        2023-10-05 12:34:56,794 - INFO - Maintenance started.
        >>> launcher.fault(TorpedoLauncher.FAULT_LEVELS['IMMEDIATE_REPAIR'])
        2023-10-05 12:34:56,795 - INFO - Torpedo launcher fault occurred: Immediate Repair
        >>> launcher.damage(TorpedoLauncher.DAMAGE_LEVELS['MINOR'])
        2023-10-05 12:34:56,796 - INFO - Torpedo launcher has been damaged: Minor Damage
        >>> print(launcher)
        Torpedo Launcher Status:
        State: idle
        Staff On Duty: 20
        Staff Off Duty: 70
        Fault Level: None
        Damage Level: Minor Damage
        Number of Tubes: 3
        Reload Time: 1 minute(s)
        Full Reload Time: 90 minute(s)
        Torpedoes Available: 3
        Tube Rotation: True
        Tube Status:
        Tube 1: Torpedo_6_0
        Tube 2: Torpedo_5_1
        Tube 3: Torpedo_4_2
    """

    IDLE = 'idle'
    LOADING = 'loading'
    READY = 'ready'
    LAUNCHING = 'launching'
    POST_LAUNCH = 'post_launch'
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

    def __init__(self, staff_on_duty, staff_off_duty, num_tubes, reload_time, full_reload_time, torpedoes, tube_rotation):
        self.state = self.IDLE
        self.staff_on_duty = staff_on_duty
        self.staff_off_duty = staff_off_duty
        self.num_tubes = num_tubes
        self.reload_time = reload_time # in minutes
        self.full_reload_time = full_reload_time # in minutes
        self.torpedoes = torpedoes
        self.tube_rotation = tube_rotation
        self.tubes = [None] * num_tubes
        self.fault_level = None
        self.damage_level = None
        self.current_reload_timer = 0.0
        self.current_full_reload_timer = 0.0

    def load_torpedoes(self):
        """Initiates the loading process for torpedoes."""
        if self.state == self.IDLE and any(tube is None for tube in self.tubes):
            self.state = self.LOADING
            logging.info("Loading torpedoes started.")
            self.current_reload_timer = self.reload_time # Start individual tube reload timer
        else:
            logging.info(f"Cannot load torpedoes while in state: {self.state} or if all tubes are full.")

    def prepare_launch(self):
        if self.state == self.READY:
            self.state = self.IDLE
            logging.info("Launch preparation completed.")
        else:
            logging.info(f"Cannot prepare launch while in state: {self.state}")

    def launch_torpedo(self):
        """Initiates the launch of a single torpedo."""
        if self.state == self.READY and any(tube is not None for tube in self.tubes):
            self.state = self.LAUNCHING
            logging.info("Torpedo launch initiated.")
            launched = False
            for i in range(self.num_tubes):
                if self.tubes[i] is not None:
                    logging.info(f"Launching {self.tubes[i]} from tube {i+1}.")
                    self.tubes[i] = None
                    launched = True
                    break # Launch only one torpedo per command
            if not launched:
                logging.info("No torpedoes available to launch.")
            self.state = self.POST_LAUNCH # Transition to post-launch state
        else:
            logging.info(f"Cannot launch torpedo while in state: {self.state} or if no torpedoes are loaded.")

    def post_launch(self):
        """Handles post-launch procedures, typically transitioning to IDLE or LOADING."""
        if self.state == self.POST_LAUNCH:
            logging.info("Post-launch processing completed. Ready for next action.")
            self.state = self.IDLE # Ready for next command, which might be reload
        else:
            logging.info(f"Cannot perform post-launch processing while in state: {self.state}")

    def reload(self):
        """Initiates a full reload of all empty tubes."""
        if self.state == self.IDLE and any(tube is None for tube in self.tubes):
            self.state = self.LOADING
            logging.info("Full torpedo reload started.")
            self.current_full_reload_timer = self.full_reload_time # Start full reload timer
        else:
            logging.info(f"Cannot reload while in state: {self.state} or if all tubes are full.")

    def maintenance(self):
        if self.state == self.IDLE:
            self.state = self.MAINTENANCE
            logging.info("Maintenance started.")
            # Simulate maintenance process
            self.tubes = [None] * self.num_tubes
            logging.info("Maintenance completed.")
            self.state = self.IDLE
        else:
            logging.info(f"Cannot perform maintenance while in state: {self.state}")

    def fault(self, level):
        if self.state in [self.IDLE, self.READY, self.LAUNCHING, self.POST_LAUNCH]:
            self.state = self.FAULT
            self.fault_level = level
            logging.info(f"Torpedo launcher fault occurred: {self.FAULT_LEVELS[level]}")
        else:
            logging.info(f"Fault cannot occur in state: {self.state}")

    def damage(self, level):
        self.state = self.DAMAGED
        self.damage_level = level
        logging.info(f"Torpedo launcher has been damaged: {self.DAMAGE_LEVELS[level]}")

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

    def update(self, delta_time):
        """Updates the torpedo launcher's state based on elapsed time."""
        if self.state == self.LOADING:
            if self.current_reload_timer > 0:
                self.current_reload_timer -= delta_time * 60 # Convert hours to minutes
                if self.current_reload_timer <= 0:
                    # Load one torpedo
                    for i in range(self.num_tubes):
                        if self.tubes[i] is None and self.torpedoes > 0:
                            self.tubes[i] = f"Torpedo_{self.torpedoes}"
                            self.torpedoes -= 1
                            logging.info(f"Torpedo loaded into tube {i+1}.")
                            break
                    if any(tube is None for tube in self.tubes) and self.torpedoes > 0:
                        self.current_reload_timer = self.reload_time # Reset timer for next torpedo
                    else:
                        logging.info("All available tubes loaded or no more torpedoes.")
                        self.state = self.READY
            elif self.current_full_reload_timer > 0:
                self.current_full_reload_timer -= delta_time * 60 # Convert hours to minutes
                if self.current_full_reload_timer <= 0:
                    # Full reload completed
                    for i in range(self.num_tubes):
                        if self.tubes[i] is None and self.torpedoes > 0:
                            self.tubes[i] = f"Torpedo_{self.torpedoes}"
                            self.torpedoes -= 1
                    logging.info("Full torpedo reload completed.")
                    self.state = self.READY
        elif self.state == self.LAUNCHING:
            self.state = self.POST_LAUNCH # Transition immediately after launch
        # Add logic for FAULT and DAMAGED states if they have time-based effects

    def get_status(self):
        """Returns a dictionary representing the torpedo launcher's status."""
        return {
            "state": self.state,
            "tubes": [tube if tube else 'Empty' for tube in self.tubes],
            "torpedoes_in_reserve": self.torpedoes,
            "fault_level": self.fault_level,
            "damage_level": self.damage_level
        }
    def __str__(self):
        fault_level = self.fault_level if self.fault_level else "None"
        damage_level = self.damage_level if self.damage_level else "None"
        tube_status = "\n".join([f"Tube {i+1}: {self.tubes[i] if self.tubes[i] else 'Empty'}" for i in range(self.num_tubes)])
        return (f"Torpedo Launcher Status:\n"
                f"State: {self.state}\n"
                f"Staff On Duty: {self.staff_on_duty}\n"
                f"Staff Off Duty: {self.staff_off_duty}\n"
                f"Number of Tubes: {self.num_tubes}\n"
                f"Reload Time (per tube): {self.reload_time} minute(s)\n"
                f"Full Reload Time: {self.full_reload_time} minute(s)\n"
                f"Current Reload Timer: {self.current_reload_timer:.2f} minutes\n"
                f"Current Full Reload Timer: {self.current_full_reload_timer:.2f} minutes\n"
                f"Torpedoes Available (in reserve): {self.torpedoes}\n"
                f"Tube 360 Degree Rotation: {self.tube_rotation}\n"
                f"Tube Status:\n"
                f"{tube_status}\n"
                f"Fault Level: {fault_level}\n"
                f"Damage Level: {damage_level}")

# Example usage
if __name__ == "__main__":
    launcher = TorpedoLauncher(
        staff_on_duty=5,
        staff_off_duty=10,
        num_tubes=3,
        reload_time=0.1, # 6 seconds per tube
        full_reload_time=0.5, # 30 seconds for full reload
        torpedoes=6,
        tube_rotation=True
    )
    print("--- Initial Torpedo Launcher Status ---")
    print(launcher)

    print("\n--- Loading Torpedoes (one by one) ---")
    launcher.load_torpedoes()
    launcher.update(delta_time=0.1/60) # Load first torpedo
    print(launcher)
    launcher.update(delta_time=0.1/60) # Load second torpedo
    print(launcher)
    launcher.update(delta_time=0.1/60) # Load third torpedo
    print(launcher)

    print("\n--- Launching Torpedo ---")
    launcher.launch_torpedo()
    launcher.update(delta_time=0.01) # Small update to transition state
    print(launcher)

    print("\n--- Reloading (full reload) ---")
    launcher.reload()
    launcher.update(delta_time=0.5/60) # Simulate full reload time
    print(launcher)

    print("\n--- Simulating Fault and Damage ---")
    launcher.fault(TorpedoLauncher.FAULT_LEVELS['IMMEDIATE_REPAIR'])
    launcher.damage(TorpedoLauncher.DAMAGE_LEVELS['MINOR'])
    print(launcher)

    print("\n--- Simulating Casualties and Staff Recall ---")
    launcher.add_casualties(1)
    launcher.recall_staff(2)
    print(launcher)