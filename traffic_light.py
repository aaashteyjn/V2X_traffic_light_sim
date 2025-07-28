# traffic_light.py

class TrafficLight:
    def __init__(self, position, mode="adaptive", green_time=10, red_time=10):
        self.position = position
        self.state = "green"
        self.timer = 0
        self.mode = mode
        self.green_time = green_time
        self.red_time = red_time

        # параметры для adaptive
        self.adaptive_threshold = 3  # машин
        self.adaptive_distance = 30  # метров

    def receive_data(self, vehicle_data):
        """Получает данные от машин (список словарей)"""
        self.vehicle_data = vehicle_data

    def update(self, dt=0.5):
        """Обновляет состояние светофора"""
        self.timer += dt

        if self.mode == "fixed":
            # фиксированный цикл
            if self.state == "green" and self.timer >= self.green_time:
                self.state = "red"
                self.timer = 0
            elif self.state == "red" and self.timer >= self.red_time:
                self.state = "green"
                self.timer = 0

        elif self.mode == "adaptive":
            # подсчёт машин в зоне
            nearby = sum(1 for v in self.vehicle_data
                         if v['distance_to_light'] <= self.adaptive_distance)

            if self.state == "red":
                if nearby >= self.adaptive_threshold:
                    self.state = "green"
                    self.timer = 0
            elif self.state == "green":
                if self.timer >= self.green_time:
                    self.state = "red"
                    self.timer = 0
