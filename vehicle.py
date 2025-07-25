
class Vehicle:
    def __init__(self, id, position, speed):
        self.id = id
        self.position = position  # X-coord
        self.speed = speed        # m/sec
        self.stopped = False

    def move(self, dt):
        if not self.stopped:
            self.position += self.speed * dt

    def distance_to_light(self, light_position):
        return max(0, light_position - self.position)

    def send_data(self, light_position):
        return {
            'id': self.id,
            'position': self.position,
            'speed': self.speed,
            'distance_to_light': self.distance_to_light(light_position)
        }
