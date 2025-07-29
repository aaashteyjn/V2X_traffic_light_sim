import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Logs
LOG_FIXED = "data/traffic_log_fixed.csv"
LOG_ADAPT = "data/traffic_log_adaptive.csv"
LOG_RL = "data/traffic_log_rl.csv"

fixed_log = pd.read_csv(LOG_FIXED)
adapt_log = pd.read_csv(LOG_ADAPT)
rl_log = pd.read_csv(LOG_RL)

def compute_metrics(df):
    times = sorted(df["time"].unique())
    
    # очередь: количество остановившихся машин в X и Y
    queue_x = df[df["direction"] == "x"].groupby("time")["stopped"].sum()
    queue_y = df[df["direction"] == "y"].groupby("time")["stopped"].sum()
    queue_total = df.groupby("time")["stopped"].sum()

    # средняя скорость по каждому направлению
    avg_speed_x = df[df["direction"] == "x"].groupby("time")["speed"].mean().mean()
    avg_speed_y = df[df["direction"] == "y"].groupby("time")["speed"].mean().mean()
    avg_speed_total = df.groupby("time")["speed"].mean().mean()

    return (times, queue_x, queue_y, queue_total,
            queue_total.mean(), avg_speed_total, avg_speed_x, avg_speed_y)

# --- считаем метрики ---
times_f, qx_f, qy_f, qtot_f, avg_q_f, avg_s_f, avg_sx_f, avg_sy_f = compute_metrics(fixed_log)
times_a, qx_a, qy_a, qtot_a, avg_q_a, avg_s_a, avg_sx_a, avg_sy_a = compute_metrics(adapt_log)
times_r, qx_r, qy_r, qtot_r, avg_q_r, avg_s_r, avg_sx_r, avg_sy_r = compute_metrics(rl_log)

# --- График общей очереди ---
plt.figure(figsize=(10,5))
plt.plot(times_f, qtot_f, label="Fixed Timer", color="red")
plt.plot(times_a, qtot_a, label="Adaptive V2I", color="green")
plt.plot(times_r, qtot_r, label="RL Agent", color="blue")
plt.title("Total Queue Length Over Time (X + Y)")
plt.xlabel("Time (s)")
plt.ylabel("Stopped Vehicles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_total_comparison.png")
plt.show()

# --- График очередей по направлениям (пример: RL) ---
plt.figure(figsize=(10,5))
plt.plot(times_r, qx_r, label="Queue X (RL)", color="blue")
plt.plot(times_r, qy_r, label="Queue Y (RL)", color="purple")
plt.title("Queue Length by Direction (RL Agent)")
plt.xlabel("Time (s)")
plt.ylabel("Stopped Vehicles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("visuals/queue_rl_by_direction.png")
plt.show()

# --- Столбчатая диаграмма средних значений ---
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
plt.savefig("visuals/performance_comparison_intersection.png")
plt.show()

# --- Итог ---
print("=== Performance Summary ===")
print(f"Fixed Timer    | Avg Queue: {avg_q_f:.2f}, Avg Speed Total: {avg_s_f:.2f} m/s (X: {avg_sx_f:.2f}, Y: {avg_sy_f:.2f})")
print(f"Adaptive V2I   | Avg Queue: {avg_q_a:.2f}, Avg Speed Total: {avg_s_a:.2f} m/s (X: {avg_sx_a:.2f}, Y: {avg_sy_a:.2f})")
print(f"RL Agent       | Avg Queue: {avg_q_r:.2f}, Avg Speed Total: {avg_s_r:.2f} m/s (X: {avg_sx_r:.2f}, Y: {avg_sy_r:.2f})")
