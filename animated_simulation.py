# animated_simulation.py

from vehicle import Vehicle
from traffic_light import TrafficLight
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation

# Параметры
NUM_VEHICLES = 5
LIGHT_POSITION = 100
SIM_DURATION = 20  # seconds
DT = 1

# objects
vehicles = [Vehicle(id=i, position=i * -20, speed=10) for i in range(NUM_VEHICLES)]
traffic_light = TrafficLight(position=LIGHT_POSITION)

# graphics
fig, ax = plt.subplots(figsize=(10, 2))
ax.set_xlim(-100, 120)
ax.set_ylim(-2, 2)
ax.set_title("V2X Анимация")
ax.axis('off')  # убираем оси

# background
road = patches.Rectangle((-120, -0.5), 240, 1, color='lightgray')
ax.add_patch(road)

# traffic light
light_box = patches.Rectangle((LIGHT_POSITION + 2, -0.2), 0.4, 0.4, color='green')
ax.add_patch(light_box)

# cars as rectangles
vehicle_patches = []
for v in vehicles:
    rect = patches.Rectangle((v.position, -0.3), 5, 0.6, color='blue')
    vehicle_patches.append(rect)
    ax.add_patch(rect)

# update
def update(frame):
    t = frame * DT
    # movement
    for v in vehicles:
        v.move(DT)

    # update traffic light
    data = [v.send_data(LIGHT_POSITION) for v in vehicles]
    traffic_light.receive_data(data)
    traffic_light.update()

    # stop
    for v in vehicles:
        dist = v.distance_to_light(LIGHT_POSITION)
        v.stopped = dist < 5 and traffic_light.state == "red"

    # car position
    for i, v in enumerate(vehicles):
        color = 'red' if v.stopped else 'blue'
        vehicle_patches[i].set_xy((v.position, -0.3))
        vehicle_patches[i].set_color(color)

    # update traffic light
    light_box.set_color('green' if traffic_light.state == "green" else 'red')
    ax.set_title(f"⏱ Время: {t} сек | Светофор: {traffic_light.state.upper()}")

    return vehicle_patches + [light_box]

# animation
frames = int(SIM_DURATION / DT)
ani = animation.FuncAnimation(fig, update, frames=frames, interval=500, blit=True, repeat=False)

plt.tight_layout()
plt.show()
