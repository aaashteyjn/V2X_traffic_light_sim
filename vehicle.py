import random

# Distance from the traffic light where vehicles must stop
STOP_LINE_DISTANCE = 20

class Vehicle:
    """
    A class representing a vehicle in the traffic simulation.
    Vehicles can be regular cars or trucks, follow acceleration/deceleration
    rules, and respond to traffic lights and other vehicles.
    """

    def __init__(self, vid, direction="x", start_pos=None, lane=0,
                 is_troublemaker=False, fast_start=True):
        self.id = vid
        self.length = random.choice([4.5, 6.0])  # meters
        self.type = "car" if self.length == 4.5 else "truck"

        # Urban driving speeds: ~22–43 km/h
        self.max_speed = random.uniform(6, 12)   # m/s
        self.speed = random.uniform(5, self.max_speed) if fast_start else random.uniform(4, self.max_speed)
        self.acceleration = 1.5   # m/s²
        self.deceleration = 3.0   # m/s²
        self.reaction_delay = random.uniform(0.3, 0.8)  # reaction delay in seconds

        self.direction = direction
        self.lane = lane
        self.is_troublemaker = is_troublemaker
        self.stopped = False
        self.delay_timer = 0.0

        # Initial position
        if direction == "x":
            self.x = start_pos if start_pos is not None else -60
            self.y = lane
        else:
            self.x = lane
            self.y = start_pos if start_pos is not None else -60

    def send_data(self, light_pos):
        """
        Send vehicle data to the traffic light (V2I communication).
        """
        return {
            "id": self.id,
            "direction": self.direction,
            "lane": self.lane,
            "speed": self.speed,
            "stopped": self.stopped,
            "troublemaker": self.is_troublemaker
        }

    def move(self, dt, front_vehicle=None, light=None, light_pos=0):
        """
        Update the vehicle's position and speed based on:
        - traffic light state,
        - leading vehicle behavior,
        - reaction delay,
        - possible random braking (troublemaker).
        """
        self.delay_timer += dt
        must_stop = False
        pos = self.x if self.direction == "x" else self.y
        stop_line = light_pos - STOP_LINE_DISTANCE
        approach_distance = 15  # meters before the stop line

        # --- Traffic light check ---
        if light and pos < stop_line:
            can_go = light.allows_movement(self.direction, pos, stop_line)

            # Strict check for the first few vehicles (to avoid red-light running)
            if self.id < 4 and not can_go:
                must_stop = True

            if not can_go:
                distance_to_line = stop_line - pos
                if distance_to_line <= approach_distance:
                    must_stop = True
                else:
                    # Smooth deceleration when still far from the stop line
                    self.speed = max(self.speed - self.deceleration * dt * 0.5,
                                     self.max_speed * 0.5)

        # --- Leading vehicle check ---
        if front_vehicle:
            if self.direction == "x":
                gap = front_vehicle.x - self.x - self.length
            else:
                gap = front_vehicle.y - self.y - self.length

            safe_gap = 7 + self.speed * 0.3  # dynamic safe distance
            if gap < safe_gap or (front_vehicle.stopped and gap < safe_gap + 2):
                must_stop = True

        # --- Reaction delay ---
        if must_stop and self.delay_timer >= self.reaction_delay:
            self.speed = max(0, self.speed - self.deceleration * dt)
            self.stopped = self.speed < 0.1
        else:
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)
            self.stopped = False

        # --- Random braking for troublemaker vehicles ---
        if self.is_troublemaker and pos < stop_line and random.random() < 0.01:
            self.speed = max(0, self.speed - self.deceleration * dt)

        # --- Position update ---
        if self.direction == "x":
            self.x += self.speed * dt
        else:
            self.y += self.speed * dt

        if self.stopped:
            self.delay_timer = 0
