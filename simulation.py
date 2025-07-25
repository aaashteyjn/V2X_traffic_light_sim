from vehicle import Vehicle
from traffic_light import TrafficLight
import time

# simulation settings
NUM_VEHICLES = 5
SIM_DURATION = 20  # seconds
LIGHT_POSITION = 100  # traffic light coord
DT = 1  # sim iter in sec

# objects create
vehicles = [Vehicle(id=i, position=i * -20, speed=10) for i in range(NUM_VEHICLES)]
traffic_light = TrafficLight(position=LIGHT_POSITION)

# simulation
for t in range(0, SIM_DURATION, DT):
    print(f"\n⏱ Время: {t} сек")
    
    # cars movement
    for v in vehicles:
        v.move(DT)

    # for V2I
    data_for_light = [v.send_data(LIGHT_POSITION) for v in vehicles]
    traffic_light.receive_data(data_for_light)
    traffic_light.update()

    # before red light
    for v in vehicles:
        dist = v.distance_to_light(LIGHT_POSITION)
        if dist < 5 and traffic_light.state == "red":
            v.stopped = True
        else:
            v.stopped = False

    # output
    print(f"🚦 Светофор: {traffic_light.state.upper()}")
    for v in vehicles:
        print(f"🚗 Машина {v.id}: позиция={v.position:.1f}м, {'СТОИТ' if v.stopped else 'едет'}")

    time.sleep(0.5)
