from vehicle import Vehicle
from traffic_light import TrafficLight
import csv
import os
import matplotlib.pyplot as plt

# simulation settings
NUM_VEHICLES = 5
SIM_DURATION = 20  # seconds
LIGHT_POSITION = 100
DT = 1

# dirs
os.makedirs("data", exist_ok=True)
os.makedirs("visuals", exist_ok=True)

# create objects
vehicles = [Vehicle(id=i, position=i * -20, speed=10) for i in range(NUM_VEHICLES)]
traffic_light = TrafficLight(position=LIGHT_POSITION)

# log-file
log_path = "data/traffic_log.csv"
with open(log_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["time", "light_state", "stopped_vehicles"])

    for t in range(0, SIM_DURATION, DT):
        # movement
        for v in vehicles:
            v.move(DT)

        # data for traffic light
        data_for_light = [v.send_data(LIGHT_POSITION) for v in vehicles]
        traffic_light.receive_data(data_for_light)
        traffic_light.update()

        # stop (red light)
        for v in vehicles:
            dist = v.distance_to_light(LIGHT_POSITION)
            if dist < 5 and traffic_light.state == "red":
                v.stopped = True
            else:
                v.stopped = False

        # log
        stopped_count = sum(1 for v in vehicles if v.stopped)
        writer.writerow([t, traffic_light.state, stopped_count])

        # text-output
        print(f"\n⏱ Time: {t} s")
        print(f"🚦 Traffic light: {traffic_light.state.upper()}")
        for v in vehicles:
            print(f"🚗 Car {v.id}: position={v.position:.1f}m, {'WAIT' if v.stopped else 'move'}")

# plot
def plot_queue(log_file):
    times, queues = [], []
    with open(log_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(int(row["time"]))
            queues.append(int(row["stopped_vehicles"]))

    plt.plot(times, queues, marker='o')
    plt.title("Compare queues in time")
    plt.xlabel("Time (sec)")
    plt.ylabel("Cars in queue")
    plt.grid(True)
    plt.savefig("visuals/queue_plot.png")
    plt.show()

plot_queue(log_path)
