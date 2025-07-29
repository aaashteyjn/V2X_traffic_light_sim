# V2X Traffic Light Simulation

This project is my attempt to build and test a simulation of traffic lights with V2I (Vehicle-to-Infrastructure) communication and reinforcement learning.  
The idea is to see how "smart" traffic lights could reduce queues and improve flow compared to the usual fixed-timer mode.

---

## What the Project Does

- Two crossing roads with stop lines and a traffic light in the middle
- Cars and trucks with different speeds, lengths, and reaction delays
- A "troublemaker" vehicle that sometimes brakes suddenly
- Three traffic light modes:
  - **Fixed Timer** (regular green-red cycle)
  - **Adaptive (V2I)** (switches depending on queue length)
  - **RL Agent (PPO)** (trained to optimize flow)

The simulation runs as an animation so you can actually watch the cars move and react to the lights.  
All runs are logged in CSV files so I can analyze queues, speeds, and compare the three modes.

---

## Architecture

- **Vehicle** — simulates movement, speed, braking, and V2I communication  
- **TrafficLight** — manages states (`green_x`, `green_y`, `yellow`) and evaluates queues  
- **IntersectionEnv** — Gymnasium-based RL environment for agent training  
- **Simulation scripts** — run and visualize the modes  
- **Analyzer** — computes metrics and generates comparative plots

---

## Project Structure

```
v2x_traffic_light_sim/
├──  vehicle.py # Vehicle behavior
├── traffic_light.py # Traffic light logic
├── intersection_env.py # RL environment
├── animated_compare.py # Main visualization
├── analyze_log.py # Performance analysis
├── train_rl.py # RL agent training
├── data/ # Simulation logs
├── visuals/ # Plots and animations
├── README.md
├── technical_description.md
├── requirements.txt
├── .gitignore
└── archive/ # Old scripts and prototypes
```

---

## Results

- Adaptive (V2I) mode usually gives shorter queues than the fixed timer.
- The RL agent can learn to control the light, but it still needs longer training to clearly beat adaptive mode.
- Average speeds are higher in adaptive and RL compared to fixed.
- The "troublemaker" makes the traffic less predictable, which shows how the system reacts to sudden changes.

### Logging

During each simulation, detailed logs are recorded in the `data/` directory:

- `traffic_log_fixed.csv` — Fixed Timer mode
- `traffic_log_adaptive.csv` — Adaptive (V2I) mode
- `traffic_log_rl.csv` — Reinforcement Learning mode

Each entry contains:  
`time, vehicle_id, direction, position_x, position_y, speed, stopped, troublemaker, light_state`

---

### Visual Outputs

- `queue_total_comparison.png` — Total queue length over time (all modes)  
- `queue_rl_by_direction.png` — Queue lengths in RL mode by direction  
- `performance_comparison_intersection.png` — Bar chart of average queue length and speed  
- Live **animated simulation** (`animated_compare.py`) with visible roads, vehicles, and traffic lights  

---

## Simulation Preview

### Side-by-Side Simulation
The following animation shows traffic flow under three control modes (Fixed Timer, Adaptive V2I, RL Agent):

![Simulation](visuals/simulation_comparison.gif)

---

## Key Figures

- **Total Queue Length Over Time**  
  ![Queue Total](visuals/queue_total_comparison.png)

- **Queue by Direction (RL Agent)**  
  ![Queue RL](visuals/queue_rl_by_direction.png)

- **Performance Comparison**  
  ![Performance](visuals/performance_comparison_intersection.png)

---

## Installation

```bash
git clone https://github.com/your-username/V2X_Traffic_Light_Sim.git
cd V2X_Traffic_Light_Sim
pip install -r requirements.txt
```

## Run the animated simulation

```bash
python animated_compare.py
```

**Train the RL-agent (takes a while)**

```bash
python train_rl.py
```

**Analyze logs and generate performance plot**

```bash
python analyze_log.py
```

---

## Parameter Justification

| Parameter                  | Value                   | Rationale                                                       |
| -------------------------- | ----------------------- | --------------------------------------------------------------- |
| Number of vehicles         | 8                       | Provides enough density to realistically form queues            |
| Traffic light position     | 0 m (vehicles start up to -100 m) | Intersection reference point; vehicles are generated up to 100 m before the stop line |
| Stop threshold             | 5 m                     | Reflects typical braking distance at urban speeds               |
| Reaction delay             | 0.3–0.8 s               | Models human driver reaction times (empirical average ~0.7 s)   |
| Troublemaker probability   | 1 per simulation        | Introduces stochastic behavior to mimic unpredictable drivers   |
| Adaptive trigger condition | ≥3 vehicles within 30 m | Threshold for detecting significant traffic clusters            |

---

## Techn stack

- Python 3.10+
- Matplotlib for visualization
- Pandas & NumPy for analysis
- Gymnasium for RL environment
- Stable-Baselines3 (PPO) for training RL agent
- PyTorch backend

---

## Technical description (md)

[Technical description (Markdown)](docs/technical_description.md)

---

## Author

Student lab-project,
V2X-based control using Python
Alina Dobershteyjn, 2025

## Contacts

For questions: [adobershteyjn@gmail.com / GitHub aaashteyjn / Telegram @user896745]
