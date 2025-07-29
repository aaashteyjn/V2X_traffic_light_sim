class TrafficLight:
    def __init__(self, position=0, mode="fixed"):
        self.position = position
        self.mode = mode
        self.state = "green_x"
        self.timer = 0
        self.cycle_time = 15

        # adaptive
        self.min_green_time = 5
        self.green_timer = 0
        self.queue_x = 0
        self.queue_y = 0

        # yellow
        self.yellow_timer = 0
        self.yellow_duration = 2

        # RL: ограничение красного
        self.red_timer = 0
        self.max_red_time = 10

    def receive_data(self, vehicle_data):
        self.queue_x = sum(1 for v in vehicle_data if v["direction"] == "x" and v["stopped"])
        self.queue_y = sum(1 for v in vehicle_data if v["direction"] == "y" and v["stopped"])

    def update(self, dt, rl_action=None):
        self.timer += dt
        self.green_timer += dt

        if self.state in ["yellow_x", "yellow_y"]:
            self.yellow_timer += dt
            if self.yellow_timer >= self.yellow_duration:
                self.state = "green_y" if self.state == "yellow_x" else "green_x"
                self.green_timer = 0
            return

        if self.mode == "fixed":
            if self.timer >= self.cycle_time:
                self.start_yellow()
                self.timer = 0

        elif self.mode == "adaptive":
            if self.green_timer < self.min_green_time:
                return
            if self.state == "green_x" and self.queue_y - self.queue_x >= 2:
                self.start_yellow()
            elif self.state == "green_y" and self.queue_x - self.queue_y >= 2:
                self.start_yellow()

        elif self.mode == "rl" and rl_action is not None:
            # считаем время на красном
            if (self.state == "green_x" and rl_action == 0) or \
               (self.state == "green_y" and rl_action == 0):
                self.red_timer += dt
            else:
                self.red_timer = 0

            if rl_action == 1 and self.green_timer >= self.min_green_time:
                self.start_yellow()
            elif self.red_timer >= self.max_red_time:
                self.start_yellow()
                self.red_timer = 0

    def start_yellow(self):
        self.yellow_timer = 0
        if self.state == "green_x":
            self.state = "yellow_x"
        else:
            self.state = "yellow_y"

    def allows_movement(self, direction, vehicle_pos, stop_line):
        if self.state == "green_x" and direction == "x":
            return True
        if self.state == "green_y" and direction == "y":
            return True
        if self.state == "yellow_x" and direction == "x":
            return vehicle_pos >= stop_line
        if self.state == "yellow_y" and direction == "y":
            return vehicle_pos >= stop_line
        return False
