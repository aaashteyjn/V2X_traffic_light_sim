# animated_compare.py

import random
import copy
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from stable_baselines3 import PPO
import numpy as np
from vehicle import Vehicle
from traffic_light import TrafficLight
import os

# фиксим OpenMP баг
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# --- параметры ---
NUM_VEHICLES = 12
NUM_LANES = 2
LIGHT_POSITION = 100
SIM_DURATION = 50
DT = 0.5

# загрузка обученной RL модели
model = PPO.load("traffic_rl_model")

# --- файлы логов ---
LOG_FIXED = "data/traffic_log_fixed.csv"
LOG_ADAPT = "data/traffic_log_adaptive.csv"
LOG_RL = "data/traffic_log_rl.csv"

for path in [LOG_FIXED, LOG_ADAPT, LOG_RL]:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time", "vehicle_id", "type", "position", "speed",
            "stopped", "troublemaker", "lane", "light_state"
        ])

def generate_vehicles():
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

def setup_scene(ax, title):
    ax.set_xlim(-120, 120)
    ax.set_ylim(-1, NUM_LANES)
    ax.axis("off")
    ax.set_title(title)
    road = patches.Rectangle((-120, -0.5), 240, NUM_LANES * 0.8 + 0.5, color="lightgray")
    ax.add_patch(road)
    light_box = patches.Rectangle((LIGHT_POSITION + 2, -0.2), 0.6, 0.6, color="green")
    ax.add_patch(light_box)
    return light_box

# --- подготовка ---
random.seed(42)
base_vehicles = generate_vehicles()
vehicles_fixed = copy.deepcopy(base_vehicles)
vehicles_adaptive = copy.deepcopy(base_vehicles)
vehicles_rl = copy.deepcopy(base_vehicles)

light_fixed = TrafficLight(position=LIGHT_POSITION, mode="fixed")
light_adaptive = TrafficLight(position=LIGHT_POSITION, mode="adaptive")
light_rl_state = "green"
rl_green_steps = 0
RL_MAX_GREEN = 20  # лимит зелёного в анимации

# --- графика ---
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

light_box_fixed = setup_scene(ax1, "Fixed Timer")
light_box_adaptive = setup_scene(ax2, "Adaptive (V2I)")
light_box_rl = setup_scene(ax3, "Reinforcement Learning")

vehicle_patches_fixed, vehicle_patches_adaptive, vehicle_patches_rl = [], [], []

for v in vehicles_fixed:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches_fixed.append(rect)
    ax1.add_patch(rect)

for v in vehicles_adaptive:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches_adaptive.append(rect)
    ax2.add_patch(rect)

for v in vehicles_rl:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches_rl.append(rect)
    ax3.add_patch(rect)

# --- функция обновления ---
def update(frame):
    global light_rl_state, rl_green_steps
    t = frame * DT

    # -------- Fixed Timer --------
    data_fixed = [v.send_data(LIGHT_POSITION) for v in vehicles_fixed]
    light_fixed.receive_data(data_fixed)
    light_fixed.update(DT)

    with open(LOG_FIXED, "a", newline="") as f:
        writer = csv.writer(f)
        for i, v in enumerate(vehicles_fixed):
            if v.can_change_lane(vehicles_fixed, NUM_LANES, -1):
                v.change_lane(-1)
            elif v.can_change_lane(vehicles_fixed, NUM_LANES, +1):
                v.change_lane(+1)
            front = min([ov for ov in vehicles_fixed if ov.lane == v.lane and ov.position > v.position],
                        key=lambda x: x.position, default=None)
            v.move(DT, front_vehicle=front, light_state=light_fixed.state, light_position=LIGHT_POSITION)
            color = "purple" if v.is_troublemaker else "red" if v.stopped else ("blue" if v.type=="car" else "orange")
            vehicle_patches_fixed[i].set_xy((v.position, v.lane_y()))
            vehicle_patches_fixed[i].set_color(color)
            writer.writerow([round(t,1), v.id, v.type, round(v.position,2), round(v.speed,2),
                             v.stopped, v.is_troublemaker, v.lane, light_fixed.state])
    light_box_fixed.set_color("green" if light_fixed.state == "green" else "red")

    # -------- Adaptive --------
    data_adapt = [v.send_data(LIGHT_POSITION) for v in vehicles_adaptive]
    light_adaptive.receive_data(data_adapt)
    light_adaptive.update(DT)

    with open(LOG_ADAPT, "a", newline="") as f:
        writer = csv.writer(f)
        for i, v in enumerate(vehicles_adaptive):
            if v.can_change_lane(vehicles_adaptive, NUM_LANES, -1):
                v.change_lane(-1)
            elif v.can_change_lane(vehicles_adaptive, NUM_LANES, +1):
                v.change_lane(+1)
            front = min([ov for ov in vehicles_adaptive if ov.lane == v.lane and ov.position > v.position],
                        key=lambda x: x.position, default=None)
            v.move(DT, front_vehicle=front, light_state=light_adaptive.state, light_position=LIGHT_POSITION)
            color = "purple" if v.is_troublemaker else "red" if v.stopped else ("blue" if v.type=="car" else "orange")
            vehicle_patches_adaptive[i].set_xy((v.position, v.lane_y()))
            vehicle_patches_adaptive[i].set_color(color)
            writer.writerow([round(t,1), v.id, v.type, round(v.position,2), round(v.speed,2),
                             v.stopped, v.is_troublemaker, v.lane, light_adaptive.state])
    light_box_adaptive.set_color("green" if light_adaptive.state == "green" else "red")

    # -------- RL --------
    queue_len = sum(1 for v in vehicles_rl if v.stopped and v.speed < 0.1)
    avg_speed = np.mean([v.speed for v in vehicles_rl])
    light_state_num = 0 if light_rl_state == "green" else 1
    obs = np.array([queue_len, avg_speed, light_state_num], dtype=np.float32)
    action, _ = model.predict(obs, deterministic=True)

    if action == 1:
        light_rl_state = "red" if light_rl_state == "green" else "green"
        rl_green_steps = 0
    if light_rl_state == "green":
        rl_green_steps += 1
        if rl_green_steps > RL_MAX_GREEN:
            light_rl_state = "red"
            rl_green_steps = 0

    with open(LOG_RL, "a", newline="") as f:
        writer = csv.writer(f)
        for i, v in enumerate(vehicles_rl):
            if v.can_change_lane(vehicles_rl, NUM_LANES, -1):
                v.change_lane(-1)
            elif v.can_change_lane(vehicles_rl, NUM_LANES, +1):
                v.change_lane(+1)
            front = min([ov for ov in vehicles_rl if ov.lane == v.lane and ov.position > v.position],
                        key=lambda x: x.position, default=None)
            v.move(DT, front_vehicle=front, light_state=light_rl_state, light_position=LIGHT_POSITION)
            color = "purple" if v.is_troublemaker else "red" if v.stopped else ("blue" if v.type=="car" else "orange")
            vehicle_patches_rl[i].set_xy((v.position, v.lane_y()))
            vehicle_patches_rl[i].set_color(color)
            writer.writerow([round(t,1), v.id, v.type, round(v.position,2), round(v.speed,2),
                             v.stopped, v.is_troublemaker, v.lane, light_rl_state])
    light_box_rl.set_color("green" if light_rl_state == "green" else "red")

    return vehicle_patches_fixed + vehicle_patches_adaptive + vehicle_patches_rl + \
           [light_box_fixed, light_box_adaptive, light_box_rl]

# --- запуск анимации ---
frames = int(SIM_DURATION / DT)
ani = animation.FuncAnimation(fig, update, frames=frames,
                              interval=500, blit=True, repeat=False)
plt.tight_layout()
plt.show()
