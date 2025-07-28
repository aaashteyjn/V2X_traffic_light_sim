# compare_simulation.py

import random
import copy
import matplotlib.pyplot as plt
from vehicle import Vehicle
from traffic_light import TrafficLight

# --- параметры ---
NUM_VEHICLES = 12
NUM_LANES = 2
LIGHT_POSITION = 100
SIM_DURATION = 50  # секунд
DT = 0.5


def generate_vehicles():
    """Создаёт список машин с многополосностью и одним troublemaker"""
    vehicles = []
    position = -100
    troublemaker_id = random.randint(0, NUM_VEHICLES - 1)

    for i in range(NUM_VEHICLES):
        lane = random.randint(0, NUM_LANES - 1)
        is_troublemaker = (i == troublemaker_id)
        v = Vehicle(id=i, position=position, lane=lane, is_troublemaker=is_troublemaker)
        gap = random.randint(10, 25)
        vehicles.append(v)
        position -= (v.length + gap)

    return vehicles


def run_simulation(vehicles_template, mode):
    """Запускает симуляцию для выбранного режима (fixed/adaptive)"""
    vehicles = copy.deepcopy(vehicles_template)
    light = TrafficLight(position=LIGHT_POSITION, mode=mode)
    queue_lengths = []

    for t in range(int(SIM_DURATION / DT)):
        # данные в светофор
        data = [v.send_data(LIGHT_POSITION) for v in vehicles]
        light.receive_data(data)
        light.update(DT)

        # движение
        for v in vehicles:
            # проверка перестроений
            if v.can_change_lane(vehicles, NUM_LANES, -1):
                v.change_lane(-1)
            elif v.can_change_lane(vehicles, NUM_LANES, +1):
                v.change_lane(+1)

            # ближайшая впереди на той же полосе
            front = None
            for ov in vehicles:
                if ov.lane == v.lane and ov.position > v.position:
                    if front is None or ov.position < front.position:
                        front = ov

            v.move(DT, front_vehicle=front,
                   light_state=light.state,
                   light_position=LIGHT_POSITION)

        # считаем остановившихся
        stopped_count = sum(1 for v in vehicles if v.stopped and v.speed < 0.1)
        queue_lengths.append(stopped_count)

    return queue_lengths


# --- запуск сравнения ---
random.seed(42)
vehicles_set = generate_vehicles()

adaptive_queue = run_simulation(vehicles_set, "adaptive")
fixed_queue = run_simulation(vehicles_set, "fixed")

# --- визуализация ---
plt.figure(figsize=(8, 4))
plt.plot(adaptive_queue, label="Adaptive (V2I)", marker="o", color="green")
plt.plot(fixed_queue, label="Fixed Timer", marker="s", color="red")
plt.title("Queue Length Comparison (Adaptive vs Fixed)")
plt.xlabel("Time step")
plt.ylabel("Stopped vehicles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_comparison.png")
plt.show()
