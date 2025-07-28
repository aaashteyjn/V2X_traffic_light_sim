# vehicle.py

import random

class Vehicle:
    def __init__(self, id, position, speed=None, length=None, vtype=None, is_troublemaker=False):
        self.id = id
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

        # фактор непредсказуемости
        self.random_brake_chance = 0.05 if is_troublemaker else 0

    def move(self, dt, front_vehicle=None, light_state="green", light_position=None):
        dist_light = self.distance_to_light(light_position) if light_position else float('inf')
        need_to_stop = False

        # светофор
        if light_state == "red" and dist_light < 10:
            need_to_stop = True

        # машина впереди
        if front_vehicle:
            gap = (front_vehicle.position - self.position) - front_vehicle.length
            if gap < 5:
                need_to_stop = True

        # непредсказуемое торможение
        if self.is_troublemaker and random.random() < self.random_brake_chance:
            need_to_stop = True

        # задержка реакции
        if need_to_stop:
            self.delay_timer += dt
            if self.delay_timer >= self.reaction_delay:
                self.stopped = True
        else:
            self.delay_timer = 0
            self.stopped = False

        # изменение скорости
        if self.stopped:
            self.speed = max(0, self.speed + self.deceleration * dt)
        else:
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)

        # движение
        self.position += self.speed * dt

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
            'distance_to_light': self.distance_to_light(light_position)
        }
