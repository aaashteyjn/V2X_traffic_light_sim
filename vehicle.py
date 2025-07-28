# vehicle.py

import random

class Vehicle:
    def __init__(self, id, position, lane=0, speed=None, length=None, vtype=None, is_troublemaker=False):
        self.id = id
        self.lane = lane
        self.type = vtype if vtype else random.choice(["car", "truck"])
        self.is_troublemaker = is_troublemaker

        if self.type == "car":
            self.length = length if length else 4.5
            self.max_speed = speed if speed else random.uniform(8, 12)
            self.acceleration = 2.5
            self.deceleration = -4.0
        else:
            self.length = length if length else 10
            self.max_speed = speed if speed else random.uniform(5, 8)
            self.acceleration = 1.5
            self.deceleration = -3.0

        self.position = position
        self.speed = self.max_speed
        self.stopped = False

        # задержка реакции
        self.reaction_delay = random.uniform(0.5, 1.5)
        self.delay_timer = 0

        # вероятность неожиданного торможения
        self.random_brake_chance = 0.05 if is_troublemaker else 0

    def lane_y(self):
        return -0.3 + self.lane * 0.8

    def move(self, dt, front_vehicle=None, light_state="green", light_position=None):
        dist_light = self.distance_to_light(light_position) if light_position else float('inf')
        need_to_stop = False

        if light_state == "red" and dist_light < 10:
            need_to_stop = True

        if front_vehicle:
            gap = (front_vehicle.position - self.position) - front_vehicle.length
            if gap < 5:
                need_to_stop = True

        if self.is_troublemaker and random.random() < self.random_brake_chance:
            need_to_stop = True

        if need_to_stop:
            self.delay_timer += dt
            if self.delay_timer >= self.reaction_delay:
                self.stopped = True
        else:
            self.delay_timer = 0
            self.stopped = False

        if self.stopped:
            self.speed = max(0, self.speed + self.deceleration * dt)
        else:
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)

        self.position += self.speed * dt

    def can_change_lane(self, other_vehicles, num_lanes, direction):
        new_lane = self.lane + direction
        if new_lane < 0 or new_lane >= num_lanes:
            return False

        front = None
        back = None
        for ov in other_vehicles:
            if ov.lane == new_lane:
                if ov.position > self.position and (front is None or ov.position < front.position):
                    front = ov
                if ov.position < self.position and (back is None or ov.position > back.position):
                    back = ov

        safe_front = (front is None) or ((front.position - self.position) > 10)
        safe_back = (back is None) or ((self.position - back.position) > 8)
        if not (safe_front and safe_back):
            return False

        front_current = None
        for ov in other_vehicles:
            if ov.lane == self.lane and ov.position > self.position:
                if front_current is None or ov.position < front_current.position:
                    front_current = ov

        current_speed_ahead = front_current.speed if front_current else self.max_speed
        new_speed_ahead = front.speed if front else self.max_speed

        return new_speed_ahead > current_speed_ahead + 1

    def change_lane(self, direction):
        self.lane += direction

    def distance_to_light(self, light_position):
        return max(0, light_position - (self.position + self.length))

    def send_data(self, light_position):
        return {
            'id': self.id,
            'type': self.type,
            'length': self.length,
            'position': self.position,
            'speed': self.speed,
            'troublemaker': self.is_troublemaker,
            'lane': self.lane,
            'distance_to_light': self.distance_to_light(light_position)
        }

    def broadcast_event(self, event_type, receivers, current_time):
        """Создаёт V2V-сообщения для других машин"""
        messages = []
        for r in receivers:
            if r.id == self.id:
                continue
            delay = random.uniform(0.05, 0.2)  # 50–200 мс
            delivered = random.random() > 0.1  # 10% потерь
            messages.append({
                "time_sent": current_time,
                "time_receive": current_time + delay,
                "sender": self.id,
                "receiver": r.id,
                "event": event_type,
                "delay": round(delay, 3),
                "delivered": delivered
            })
        return messages
