# analyze_log.py

import pandas as pd
import matplotlib.pyplot as plt

LOG_FILE = "data/traffic_log.csv"

# читаем лог
df = pd.read_csv(LOG_FILE)

# преобразуем время в ось
times = sorted(df["time"].unique())

# --- График длины очереди ---
queue_length = df.groupby("time")["stopped"].sum()

plt.figure(figsize=(8,4))
plt.plot(times, queue_length, marker="o")
plt.title("Queue Length Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of stopped vehicles")
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_length.png")
plt.show()


# --- Траектории движения ---
plt.figure(figsize=(10,5))
for vid, group in df.groupby("vehicle_id"):
    if group["troublemaker"].any():
        plt.plot(group["time"], group["position"], label=f"Vehicle {vid} (Troublemaker)", color="purple", linewidth=2)
    else:
        plt.plot(group["time"], group["position"], label=f"Vehicle {vid}")

plt.title("Vehicle Trajectories")
plt.xlabel("Time (s)")
plt.ylabel("Position (m)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/trajectories.png")
plt.show()


# --- Скорость по времени ---
plt.figure(figsize=(10,5))
for vid, group in df.groupby("vehicle_id"):
    plt.plot(group["time"], group["speed"], label=f"Vehicle {vid}", linestyle="--" if group["troublemaker"].any() else "-")

plt.title("Vehicle Speeds Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/speeds.png")
plt.show()
