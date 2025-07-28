# compare_simulation.py

import random
import copy
import matplotlib.pyplot as plt
from vehicle import Vehicle
from traffic_light import TrafficLight

# параметры
NUM_VEHICLES = 7
LIGHT_POSITION = 100
SIM_DURATION = 40
DT = 0.5


# генерация набора машин (разные типы, скорости, длины)
def generate_vehicles():
    vehicles = []
    position = -100
    for i in range(NUM_VEHICLES):
        v = Vehicle(id=i, position=position)
        gap = random.randint(10, 25)
        vehicles.append(v)
        position -= (v.length + gap)
    return vehicles


# симуляция одного режима
def run_simulation(vehicles_template, mode):
    vehicles = copy.deepcopy(vehicles_template)
    light = TrafficLight(position=LIGHT_POSITION, mode=mode)
    queue_lengths = []

    for t in range(int(SIM_DURATION / DT)):
        # обновляем светофор
        data = [v.send_data(LIGHT_POSITION) for v in vehicles]
        light.receive_data(data)
        light.update()

        # движение машин
        for i, v in enumerate(vehicles):
            front = vehicles[i - 1] if i > 0 else None
            v.move(DT, front_vehicle=front,
                   light_state=light.state,
                   light_position=LIGHT_POSITION)

        # считаем остановившихся
        stopped_count = sum(1 for v in vehicles if v.stopped and v.speed < 0.1)
        queue_lengths.append(stopped_count)

    return queue_lengths


# === точка входа ===
random.seed(42)  # убери для полной случайности
vehicles_set = generate_vehicles()

adaptive_queue = run_simulation(vehicles_set, "adaptive")
fixed_queue = run_simulation(vehicles_set, "fixed")

# визуализация
plt.figure(figsize=(8, 4))
plt.plot(adaptive_queue, label="Adaptive (V2I)", marker="o")
plt.plot(fixed_queue, label="Fixed Timer", marker="s")
plt.title("Queue Length Comparison (Adaptive vs Fixed)")
plt.xlabel("Time step")
plt.ylabel("Number of stopped vehicles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_comparison.png")
plt.show()
