# analyze_log.py

import pandas as pd
import matplotlib.pyplot as plt

LOG_FILE = "data/traffic_log.csv"

# читаем лог
df = pd.read_csv(LOG_FILE)
times = sorted(df["time"].unique())

# --- Queue length ---
queue_length = df.groupby("time")["stopped"].sum()
plt.figure(figsize=(8,4))
plt.plot(times, queue_length, marker="o", color="darkred")
plt.title("Queue Length Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Stopped vehicles")
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_length.png")
plt.show()

# --- Vehicle Trajectories ---
plt.figure(figsize=(10,5))
for vid, group in df.groupby("vehicle_id"):
    if group["troublemaker"].any():
        plt.plot(group["time"], group["position"],
                 label=f"Vehicle {vid} (Troublemaker)", color="purple", linewidth=2)
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

# --- Vehicle Speeds ---
plt.figure(figsize=(10,5))
for vid, group in df.groupby("vehicle_id"):
    style = "--" if group["troublemaker"].any() else "-"
    plt.plot(group["time"], group["speed"],
             label=f"Vehicle {vid}", linestyle=style)
plt.title("Vehicle Speeds Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/speeds.png")
plt.show()

# --- Lane Changes ---
lane_changes = {}
for vid, group in df.groupby("vehicle_id"):
    lanes = list(group["lane"])
    changes = sum(lanes[i] != lanes[i-1] for i in range(1, len(lanes)))
    lane_changes[vid] = changes

plt.figure(figsize=(8,4))
plt.bar(lane_changes.keys(), lane_changes.values(), color="teal")
plt.title("Number of Lane Changes per Vehicle")
plt.xlabel("Vehicle ID")
plt.ylabel("Lane changes")
plt.grid(True, axis="y")
plt.tight_layout()
plt.savefig("visuals/lane_changes.png")
plt.show()

print("Lane changes per vehicle:", lane_changes)
