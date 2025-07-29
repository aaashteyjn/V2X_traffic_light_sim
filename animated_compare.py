import random
import copy
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from stable_baselines3 import PPO
import numpy as np
from vehicle import Vehicle, STOP_LINE_DISTANCE
from traffic_light import TrafficLight
import os

# Fix OpenMP warning
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# --- Parameters ---
NUM_VEHICLES_X = 8
NUM_VEHICLES_Y = 8
LIGHT_POSITION = 0
SIM_DURATION = 60
DT = 0.5

# RL model
try:
    model = PPO.load("traffic_rl_model")
    RL_AVAILABLE = True
except:
    print("⚠️ RL model not found, RL mode will be skipped.")
    RL_AVAILABLE = False

# Logs
LOG_FIXED = "data/traffic_log_fixed.csv"
LOG_ADAPT = "data/traffic_log_adaptive.csv"
LOG_RL = "data/traffic_log_rl.csv"

for path in [LOG_FIXED, LOG_ADAPT, LOG_RL]:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time", "vehicle_id", "direction", "position_x", "position_y",
            "speed", "stopped", "troublemaker", "light_state"
        ])

def generate_vehicle(direction, lane, start_pos, vid, troublemaker_id):
    return Vehicle(
        id=vid,
        direction=direction,
        start_pos=start_pos,
        lane=lane,
        is_troublemaker=(vid == troublemaker_id)
    )

def generate_vehicles():
    vehicles = []
    troublemaker_id = random.randint(0, NUM_VEHICLES_X + NUM_VEHICLES_Y - 1)
    vid = 0

    for lane in [-3, +3]:  # Horizontal (X)
        pos = -100
        for _ in range(NUM_VEHICLES_X // 2):
            v = generate_vehicle("x", lane, pos, vid, troublemaker_id)
            vehicles.append(v)
            pos -= random.randint(20, 30)
            vid += 1

    for lane in [-3, +3]:  # Vertical (Y)
        pos = -100
        for _ in range(NUM_VEHICLES_Y // 2):
            v = generate_vehicle("y", lane, pos, vid, troublemaker_id)
            vehicles.append(v)
            pos -= random.randint(20, 30)
            vid += 1

    return vehicles

def setup_scene(ax, title):
    ax.set_xlim(-120, 120)
    ax.set_ylim(-120, 120)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title)

    road_x = patches.Rectangle((-120, -8), 240, 16, color="lightgray")
    road_y = patches.Rectangle((-8, -120), 16, 240, color="lightgray")
    ax.add_patch(road_x)
    ax.add_patch(road_y)

    # стоп-линии
    stop_x = patches.Rectangle((-STOP_LINE_DISTANCE, -8), 2, 16, color="darkred")
    stop_y = patches.Rectangle((-8, -STOP_LINE_DISTANCE), 16, 2, color="darkred")
    ax.add_patch(stop_x)
    ax.add_patch(stop_y)

    # светофоры
    light_x = patches.Circle((-15, 0), radius=3, color="green")
    light_y = patches.Circle((0, -15), radius=3, color="red")
    ax.add_patch(light_x)
    ax.add_patch(light_y)

    return light_x, light_y

def init_vehicle_patches(ax, vehicles):
    car_patches = []
    for v in vehicles:
        rect = patches.Rectangle((v.x - 2, v.y - 2), 4, 4,
                                 color="blue" if v.type == "car" else "orange")
        car_patches.append(rect)
        ax.add_patch(rect)
    return car_patches

def update_lights(light, lights):
    if light.state == "yellow_x" or light.state == "yellow_y":
        lights[0].set_color("yellow")
        lights[1].set_color("yellow")
    else:
        lights[0].set_color("green" if light.state == "green_x" else "red")
        lights[1].set_color("green" if light.state == "green_y" else "red")

# Setup
random.seed(42)
vehicles_fixed = generate_vehicles()
vehicles_adaptive = copy.deepcopy(vehicles_fixed)
vehicles_rl = copy.deepcopy(vehicles_fixed) if RL_AVAILABLE else []

light_fixed = TrafficLight(position=LIGHT_POSITION, mode="fixed")
light_adaptive = TrafficLight(position=LIGHT_POSITION, mode="adaptive")
light_rl = TrafficLight(position=LIGHT_POSITION, mode="rl") if RL_AVAILABLE else None

# Graphs
cols = 3 if RL_AVAILABLE else 2
fig, axes = plt.subplots(1, cols, figsize=(6 * cols, 6))
if cols == 2:
    ax1, ax2 = axes
    ax3 = None
else:
    ax1, ax2, ax3 = axes

lights_fixed = setup_scene(ax1, "Fixed Timer")
lights_adaptive = setup_scene(ax2, "Adaptive (V2I)")
if RL_AVAILABLE:
    lights_rl = setup_scene(ax3, "Reinforcement Learning")

patches_fixed = init_vehicle_patches(ax1, vehicles_fixed)
patches_adaptive = init_vehicle_patches(ax2, vehicles_adaptive)
patches_rl = init_vehicle_patches(ax3, vehicles_rl) if RL_AVAILABLE else []

def update(frame):
    t = frame * DT

    def sim_step(vehicles, light, patches, logfile, lights, rl=False):
        if rl and RL_AVAILABLE:
            queue_x = sum(1 for v in vehicles if v.direction == "x" and v.stopped)
            queue_y = sum(1 for v in vehicles if v.direction == "y" and v.stopped)
            state_num = 0 if light.state.startswith("green_x") else 1
            obs = np.array([queue_x, queue_y, state_num], dtype=np.float32)
            action, _ = model.predict(obs, deterministic=True)
            light.update(DT, rl_action=action)
        else:
            data = [v.send_data(LIGHT_POSITION) for v in vehicles]
            light.receive_data(data)
            light.update(DT)

        with open(logfile, "a", newline="") as f:
            writer = csv.writer(f)
            for i, v in enumerate(vehicles):
                if v.direction == "x":
                    front = min([ov for ov in vehicles if ov.direction == "x" and ov.x > v.x],
                                key=lambda x: x.x, default=None)
                else:
                    front = min([ov for ov in vehicles if ov.direction == "y" and ov.y > v.y],
                                key=lambda x: x.y, default=None)

                v.move(DT, front_vehicle=front,
                       light=light, light_pos=LIGHT_POSITION)

                color = "purple" if v.is_troublemaker else "red" if v.stopped else (
                        "blue" if v.type == "car" else "orange")
                patches[i].set_xy((v.x - 2, v.y - 2))
                patches[i].set_color(color)

                writer.writerow([round(t,1), v.id, v.direction, round(v.x,2), round(v.y,2),
                                 round(v.speed,2), v.stopped, v.is_troublemaker, light.state])

        update_lights(light, lights)
        return light.state

    sim_step(vehicles_fixed, light_fixed, patches_fixed, LOG_FIXED, lights_fixed)
    sim_step(vehicles_adaptive, light_adaptive, patches_adaptive, LOG_ADAPT, lights_adaptive)
    if RL_AVAILABLE:
        sim_step(vehicles_rl, light_rl, patches_rl, LOG_RL, lights_rl, rl=True)

    drawn = patches_fixed + patches_adaptive
    if RL_AVAILABLE:
        drawn += patches_rl + [lights_rl[0], lights_rl[1]]
    return drawn + [lights_fixed[0], lights_fixed[1], lights_adaptive[0], lights_adaptive[1]]

frames = int(SIM_DURATION / DT)
ani = animation.FuncAnimation(fig, update, frames=frames, interval=300, blit=True, repeat=False)
plt.tight_layout()
plt.show()
