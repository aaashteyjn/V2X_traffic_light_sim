class TrafficLight:
    def __init__(self, position, mode="adaptive"):
        self.position = position
        self.state = "green"
        self.timer = 0
        self.mode = mode
        self.vehicle_data_list = []

    def receive_data(self, vehicle_data_list):
        self.vehicle_data_list = vehicle_data_list

    def update(self):
        self.timer += 1

        if self.mode == "adaptive":
            close_cars = [v for v in self.vehicle_data_list if v['distance_to_light'] < 30]
            if len(close_cars) >= 3:
                self.state = "green"
            else:
                self.state = "red"

        elif self.mode == "fixed":
            if self.timer % 10 < 5:
                self.state = "green"
            else:
                self.state = "red"
