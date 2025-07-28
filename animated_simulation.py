# animated_simulation.py

import random
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from vehicle import Vehicle
from traffic_light import TrafficLight

# --- параметры ---
NUM_VEHICLES = 12
NUM_LANES = 2
LIGHT_POSITION = 100
SIM_DURATION = 50  # секунд
DT = 0.5           # шаг по времени
LOG_FILE = "data/traffic_log.csv"

# --- генерация машин ---
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

# --- светофор ---
traffic_light = TrafficLight(position=LIGHT_POSITION)

# --- логирование ---
with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "time", "vehicle_id", "type", "position", "speed",
        "stopped", "troublemaker", "lane", "light_state"
    ])

# --- графика ---
fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(-120, 120)
ax.set_ylim(-2, 2 + NUM_LANES)
ax.axis("off")

road = patches.Rectangle((-120, -0.5), 240, NUM_LANES * 0.8 + 0.5, color="lightgray")
ax.add_patch(road)

light_box = patches.Rectangle((LIGHT_POSITION + 2, -0.2), 0.6, 0.6, color="green")
ax.add_patch(light_box)

vehicle_patches = []
for v in vehicles:
    rect = patches.Rectangle((v.position, v.lane_y()), v.length, 0.6, color="blue")
    vehicle_patches.append(rect)
    ax.add_patch(rect)

# --- функция обновления ---
def update(frame):
    t = frame * DT

    # данные в светофор
    data = [v.send_data(LIGHT_POSITION) for v in vehicles]
    traffic_light.receive_data(data)
    traffic_light.update()

    # обновление движения и лог
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        for i, v in enumerate(vehicles):
            # проверка возможности перестроения
            if v.can_change_lane(vehicles, NUM_LANES, -1):
                v.change_lane(-1)
            elif v.can_change_lane(vehicles, NUM_LANES, +1):
                v.change_lane(+1)

            # поиск ближайшей впереди
            front = None
            for ov in vehicles:
                if ov.lane == v.lane and ov.position > v.position:
                    if front is None or ov.position < front.position:
                        front = ov

            v.move(DT, front_vehicle=front,
                   light_state=traffic_light.state,
                   light_position=LIGHT_POSITION)

            # цвет
            if v.stopped and v.speed < 0.1:
                color = "red"
            elif v.is_troublemaker:
                color = "purple"
            elif v.type == "car":
                color = "blue"
            else:
                color = "orange"

            vehicle_patches[i].set_xy((v.position, v.lane_y()))
            vehicle_patches[i].set_width(v.length)
            vehicle_patches[i].set_color(color)

            # запись в лог
            writer.writerow([
                round(t, 1), v.id, v.type, round(v.position, 2),
                round(v.speed, 2), v.stopped, v.is_troublemaker,
                v.lane, traffic_light.state
            ])

    light_box.set_color("green" if traffic_light.state == "green" else "red")
    ax.set_title(f"⏱ Time: {t:.1f}s | Light: {traffic_light.state.upper()}")

    return vehicle_patches + [light_box]

# --- запуск анимации ---
frames = int(SIM_DURATION / DT)
ani = animation.FuncAnimation(fig, update, frames=frames,
                              interval=500, blit=True, repeat=False)

plt.tight_layout()
plt.show()

# --- сохранить гиф ---
# ani.save("visuals/traffic_animation.gif", writer="pillow", fps=2)
