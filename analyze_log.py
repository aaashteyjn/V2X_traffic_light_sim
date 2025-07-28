# analyze_log.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- загрузка логов ---
LOG_FIXED = "data/traffic_log_fixed.csv"
LOG_ADAPT = "data/traffic_log_adaptive.csv"
LOG_RL = "data/traffic_log_rl.csv"

fixed_log = pd.read_csv(LOG_FIXED)
adapt_log = pd.read_csv(LOG_ADAPT)
rl_log = pd.read_csv(LOG_RL)

def compute_metrics(df):
    """Вычисляет ключевые метрики для одного режима"""
    times = sorted(df["time"].unique())
    queue_length = df.groupby("time")["stopped"].sum()
    avg_queue = queue_length.mean()
    avg_speed = df.groupby("time")["speed"].mean().mean()
    return times, queue_length, avg_queue, avg_speed

# --- считаем метрики ---
times_f, q_fixed, avg_q_f, avg_s_f = compute_metrics(fixed_log)
times_a, q_adapt, avg_q_a, avg_s_a = compute_metrics(adapt_log)
times_r, q_rl, avg_q_r, avg_s_r = compute_metrics(rl_log)

# --- график длины очереди ---
plt.figure(figsize=(10,5))
plt.plot(times_f, q_fixed, label="Fixed Timer", color="red")
plt.plot(times_a, q_adapt, label="Adaptive V2I", color="green")
plt.plot(times_r, q_rl, label="RL Agent", color="blue")
plt.title("Queue Length Over Time: Fixed vs Adaptive vs RL")
plt.xlabel("Time (s)")
plt.ylabel("Stopped Vehicles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_comparison_3modes.png")
plt.show()

# --- столбчатая диаграмма ---
labels = ["Fixed Timer", "Adaptive V2I", "RL Agent"]
avg_queues = [avg_q_f, avg_q_a, avg_q_r]
avg_speeds = [avg_s_f, avg_s_a, avg_s_r]

x = np.arange(len(labels))
width = 0.35

fig, ax1 = plt.subplots(figsize=(9,5))

ax1.bar(x - width/2, avg_queues, width, label="Avg Queue Length", color="orange")
ax1.set_ylabel("Avg Queue Length")
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.bar(x + width/2, avg_speeds, width, label="Avg Speed (m/s)", color="teal")
ax2.set_ylabel("Avg Speed (m/s)")
ax2.legend(loc="upper right")

plt.title("Performance Comparison of Traffic Light Modes")
plt.tight_layout()
plt.savefig("visuals/performance_comparison.png")
plt.show()

# --- печать итогов ---
print("=== Performance Summary ===")
print(f"Fixed Timer    | Avg Queue: {avg_q_f:.2f}, Avg Speed: {avg_s_f:.2f} m/s")
print(f"Adaptive V2I   | Avg Queue: {avg_q_a:.2f}, Avg Speed: {avg_s_a:.2f} m/s")
print(f"RL Agent       | Avg Queue: {avg_q_r:.2f}, Avg Speed: {avg_s_r:.2f} m/s")
