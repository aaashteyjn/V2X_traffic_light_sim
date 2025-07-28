# animated_compare.py

import random
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from vehicle import Vehicle
from traffic_light import TrafficLight

# --- параметры ---
NUM_VEHICLES = 12
NUM_LANES = 2
LIGHT_POSITION = 100
SIM_DURATION = 50
DT = 0.5


def generate_vehicles():
    """Создаём многополосный набор машин"""
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

light_fixed = TrafficLight(position=LIGHT_POSITION, mode="fixed")
light_adaptive = TrafficLight(position=LIGHT_POSITION, mode="adaptive")

# --- графика ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

light_box_fixed = setup_scene(ax1, "Fixed Timer")
light_box_adaptive = setup_scene(ax2, "Adaptive (V2I)")

vehicle_patches_fixed, vehicle_patches_adaptive = [], []

for v in vehicles_fixed:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches_fixed.append(rect)
    ax1.add_patch(rect)

for v in vehicles_adaptive:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches_adaptive.append(rect)
    ax2.add_patch(rect)


# --- обновление кадров ---
def update(frame):
    t = frame * DT

    # --- Fixed Timer ---
    data_fixed = [v.send_data(LIGHT_POSITION) for v in vehicles_fixed]
    light_fixed.receive_data(data_fixed)
    light_fixed.update(DT)

    for i, v in enumerate(vehicles_fixed):
        # проверка перестроений
        if v.can_change_lane(vehicles_fixed, NUM_LANES, -1):
            v.change_lane(-1)
        elif v.can_change_lane(vehicles_fixed, NUM_LANES, +1):
            v.change_lane(+1)

        front = None
        for ov in vehicles_fixed:
            if ov.lane == v.lane and ov.position > v.position:
                if front is None or ov.position < front.position:
                    front = ov

        v.move(DT, front_vehicle=front, light_state=light_fixed.state, light_position=LIGHT_POSITION)

        # цвет
        if v.stopped and v.speed < 0.1:
            color = "red"
        elif v.is_troublemaker:
            color = "purple"
        elif v.type == "car":
            color = "blue"
        else:
            color = "orange"

        vehicle_patches_fixed[i].set_xy((v.position, v.lane_y()))
        vehicle_patches_fixed[i].set_width(v.length)
        vehicle_patches_fixed[i].set_color(color)

    light_box_fixed.set_color("green" if light_fixed.state == "green" else "red")
    ax1.set_title(f"Fixed Timer | Time {t:.1f}s")

    # --- Adaptive ---
    data_adaptive = [v.send_data(LIGHT_POSITION) for v in vehicles_adaptive]
    light_adaptive.receive_data(data_adaptive)
    light_adaptive.update(DT)

    for i, v in enumerate(vehicles_adaptive):
        if v.can_change_lane(vehicles_adaptive, NUM_LANES, -1):
            v.change_lane(-1)
        elif v.can_change_lane(vehicles_adaptive, NUM_LANES, +1):
            v.change_lane(+1)

        front = None
        for ov in vehicles_adaptive:
            if ov.lane == v.lane and ov.position > v.position:
                if front is None or ov.position < front.position:
                    front = ov

        v.move(DT, front_vehicle=front, light_state=light_adaptive.state, light_position=LIGHT_POSITION)

        if v.stopped and v.speed < 0.1:
            color = "red"
        elif v.is_troublemaker:
            color = "purple"
        elif v.type == "car":
            color = "blue"
        else:
            color = "orange"

        vehicle_patches_adaptive[i].set_xy((v.position, v.lane_y()))
        vehicle_patches_adaptive[i].set_width(v.length)
        vehicle_patches_adaptive[i].set_color(color)

    light_box_adaptive.set_color("green" if light_adaptive.state == "green" else "red")
    ax2.set_title(f"Adaptive (V2I) | Time {t:.1f}s")

    return vehicle_patches_fixed + vehicle_patches_adaptive + [light_box_fixed, light_box_adaptive]


# --- анимация ---
frames = int(SIM_DURATION / DT)
ani = animation.FuncAnimation(fig, update, frames=frames,
                              interval=500, blit=True, repeat=False)

plt.tight_layout()
plt.show()

# --- сохранить как GIF (по желанию) ---
# ani.save("visuals/compare_animation.gif", writer="pillow", fps=2)
