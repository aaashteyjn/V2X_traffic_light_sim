class TrafficLight:
    """
    A class representing a traffic light in the V2X intersection simulation.

    Modes:
        - fixed: switches after a fixed cycle time
        - adaptive: adjusts based on queue lengths
        - rl: controlled by a reinforcement learning agent
    """

    def __init__(self, position=0, mode="fixed"):
        self.position = position
        self.mode = mode
        self.state = "green_x"  # initial state: X-direction green
        self.timer = 0
        self.cycle_time = 15  # fixed cycle length (seconds)

        # Adaptive mode parameters
        self.min_green_time = 5
        self.green_timer = 0
        self.queue_x = 0
        self.queue_y = 0

        # Yellow phase parameters
        self.yellow_timer = 0
        self.yellow_duration = 2

        # RL mode parameters
        self.red_timer = 0
        self.max_red_time = 10  # prevent starving a direction

    def receive_data(self, vehicle_data):
        """
        Receive V2I data from vehicles.
        Counts stopped vehicles in both directions.
        """
        self.queue_x = sum(1 for v in vehicle_data if v["direction"] == "x" and v["stopped"])
        self.queue_y = sum(1 for v in vehicle_data if v["direction"] == "y" and v["stopped"])

    def update(self, dt, rl_action=None):
        """
        Update traffic light state based on the selected mode.
        dt: simulation timestep
        rl_action: optional action from RL agent (0=hold, 1=switch)
        """
        self.timer += dt
        self.green_timer += dt

        # Handle yellow phase transition
        if self.state in ["yellow_x", "yellow_y"]:
            self.yellow_timer += dt
            if self.yellow_timer >= self.yellow_duration:
                # Switch to the opposite green after yellow
                self.state = "green_y" if self.state == "yellow_x" else "green_x"
                self.green_timer = 0
            return

        # Fixed cycle mode
        if self.mode == "fixed":
            if self.timer >= self.cycle_time:
                self.start_yellow()
                self.timer = 0

        # Adaptive V2I mode
        elif self.mode == "adaptive":
            if self.green_timer < self.min_green_time:
                return
            if self.state == "green_x" and self.queue_y - self.queue_x >= 2:
                self.start_yellow()
            elif self.state == "green_y" and self.queue_x - self.queue_y >= 2:
                self.start_yellow()

        # Reinforcement Learning mode
        elif self.mode == "rl" and rl_action is not None:
            # Count how long one direction has been red
            if (self.state == "green_x" and rl_action == 0) or \
               (self.state == "green_y" and rl_action == 0):
                self.red_timer += dt
            else:
                self.red_timer = 0

            # Switch based on RL action or red-time limit
            if rl_action == 1 and self.green_timer >= self.min_green_time:
                self.start_yellow()
            elif self.red_timer >= self.max_red_time:
                self.start_yellow()
                self.red_timer = 0

    def start_yellow(self):
        """
        Initiate the yellow phase before switching directions.
        """
        self.yellow_timer = 0
        if self.state == "green_x":
            self.state = "yellow_x"
        else:
            self.state = "yellow_y"

    def allows_movement(self, direction, vehicle_pos, stop_line):
        """
        Check if a vehicle is allowed to move based on the current signal state.
        """
        if self.state == "green_x" and direction == "x":
            return True
        if self.state == "green_y" and direction == "y":
            return True
        if self.state == "yellow_x" and direction == "x":
            return vehicle_pos >= stop_line
        if self.state == "yellow_y" and direction == "y":
            return vehicle_pos >= stop_line
        return False
