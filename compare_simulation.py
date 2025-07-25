from vehicle import Vehicle
from traffic_light import TrafficLight
import matplotlib.pyplot as plt

NUM_VEHICLES = 5
LIGHT_POSITION = 100
SIM_DURATION = 30
DT = 1

def run_simulation(mode):
    vehicles = [Vehicle(id=i, position=i * -20, speed=10) for i in range(NUM_VEHICLES)]
    light = TrafficLight(position=LIGHT_POSITION, mode=mode)
    queue_lengths = []

    for t in range(0, SIM_DURATION, DT):
        for v in vehicles:
            v.move(DT)

        data = [v.send_data(LIGHT_POSITION) for v in vehicles]
        light.receive_data(data)
        light.update()

        for v in vehicles:
            dist = v.distance_to_light(LIGHT_POSITION)
            v.stopped = dist < 5 and light.state == "red"

        stopped_count = sum(1 for v in vehicles if v.stopped)
        queue_lengths.append(stopped_count)

    return queue_lengths

# both sims
adaptive_queue = run_simulation("adaptive")
fixed_queue = run_simulation("fixed")

# plot
plt.plot(adaptive_queue, label="Adaptive (V2I)", marker="o")
plt.plot(fixed_queue, label="Default (timer)", marker="s")
plt.title("Compare queues in time")
plt.xlabel("Time (sec)")
plt.ylabel("Cars in queue")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_comparison.png")
plt.show()
