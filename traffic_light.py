
class TrafficLight:
    def __init__(self, position):
        self.position = position
        self.state = "green"  # or "red"
        self.timer = 0

    def receive_data(self, vehicle_data_list):
        self.vehicle_data_list = vehicle_data_list

    def update(self):
        # logic: if > N cars in 30m — green light
        close_cars = [v for v in self.vehicle_data_list if v['distance_to_light'] < 30]
        if len(close_cars) >= 3:
            self.state = "green"
        else:
            self.state = "red"
