# V2X Traffic Light Simulation — Technical Description

**Author:** Alina Doberstein  
**Year:** 2025  

---

## 1. Project Topic

This project presents a simulation of a traffic light control system at a two-road intersection, integrating **Vehicle-to-Infrastructure (V2I)** communication and **Reinforcement Learning (RL)**.  
The goal is to compare traditional and intelligent control modes in terms of traffic efficiency and safety.

---

## 2. Objective

To design and evaluate a simplified yet realistic intersection model where traffic lights adapt to real-time conditions via V2I communication and reinforcement learning, aiming to reduce waiting times and improve traffic flow.

---

## 3. Tasks

- Develop a Python-based simulation of an intersection with crossing roads.  
- Implement vehicles with stochastic characteristics:  
  - length (car/truck),  
  - speed, acceleration and deceleration,  
  - reaction delays,  
  - random "troublemaker" behavior.  
- Implement three traffic light control modes:  
  1. **Fixed Timer** — static signal cycles.  
  2. **Adaptive (V2I)** — responds to detected queues.  
  3. **Reinforcement Learning Agent (PPO)** — trained to minimize congestion.  
- Log all vehicle states and traffic light changes into CSV files.  
- Produce visualizations:  
  - animated simulation with visible road, vehicles, and traffic lights,  
  - comparative plots of queue lengths and average speeds.  
- Evaluate the performance of each control mode using queue length, speed, and crash metrics.

---

## 4. Technologies Used

- **Programming Language:** Python 3.10+  
- **Visualization:** matplotlib (animations, plots)  
- **Data Analysis:** pandas, numpy  
- **Reinforcement Learning:** Stable-Baselines3 (PPO), PyTorch  
- **Simulation Framework:** Gymnasium (custom environment)  
- **Data Storage:** CSV logs  
- **IDE:** VS Code / Jupyter Notebook  

---

## 5. Model Description

### 5.1 Core Components

- **Vehicle**
  - Attributes: position, speed, length, acceleration, stopped status  
  - Behaviors: movement, delayed reactions, random braking ("troublemaker"), V2I communication  

- **TrafficLight**
  - States: `green_x`, `green_y`, `yellow_x`, `yellow_y`  
  - Modes: Fixed, Adaptive, RL  
  - Decision-making: evaluates queues, applies switching logic  

- **IntersectionEnv (Gymnasium Environment)**
  - Observation: `[queue_x, queue_y, light_state]`  
  - Action: `0 = hold current state`, `1 = request switch`  
  - Reward:  
    - `- (queue_x + queue_y)` (penalty for queues)  
    - `- 10 * crashes` (penalty for collisions)  
    - `+ 3 * passed vehicles` (reward for throughput)  
    - `- 2` for unnecessary switching  

### 5.2 Key Parameters

| Parameter                  | Value                   | Rationale                                                       |
| -------------------------- | ----------------------- | --------------------------------------------------------------- |
| Number of vehicles         | 8                       | Provides sufficient density to form queues                      |
| Traffic light position     | 0 m (vehicles start up to -100 m) | Intersection reference; vehicles generated up to 100 m before the stop line |
| Stop threshold             | 5 m                     | Reflects typical braking distance at urban speeds               |
| Reaction delay             | 0.3–0.8 s               | Models human driver reaction time (average ~0.7 s)              |
| Troublemaker probability   | 1 per simulation        | Adds stochastic driver unpredictability                         |
| Adaptive trigger condition | ≥3 vehicles within 30 m | Detects traffic clusters for adaptive switching                 |
| Yellow light duration      | 2 s                     | Realistic transitional period before switching                  |
| RL training timesteps      | 300,000                 | Ensures stable PPO agent training                              |

---

## 6. Results

- **Adaptive V2I** reduced the average queue length by ~40% compared to the Fixed Timer.  
- **Reinforcement Learning agent (PPO)** demonstrated learning capability but requires extended training to consistently outperform the Adaptive mode.  
- **Average speeds** were higher under Adaptive and RL compared to Fixed Timer.  
- **Troublemaker vehicle** induced local disturbances, effectively testing system robustness.  
- Visualization confirmed smoother and more efficient traffic flow in Adaptive and RL modes.  

### Key Figures

- **Total Queue Length Over Time**  
  ![Queue Total](visuals/queue_total_comparison.png)

- **Queue by Direction (RL Agent)**  
  ![Queue RL](visuals/queue_rl_by_direction.png)

- **Performance Comparison**  
  ![Performance](visuals/performance_comparison_intersection.png)

---

## 7. Conclusion

This project shows that even a simplified V2X-based traffic control system provides measurable efficiency gains over a fixed-timer signal. Adaptive systems already show substantial improvement, and reinforcement learning agents hold promise for further advancements.

Future directions include:  
- Multi-lane and multi-intersection simulations  
- Integration of vehicle priority classes (buses, emergency services)  
- Training with larger datasets and advanced RL algorithms  
- Evaluation under varying traffic density and accident rates  

---

## 8. Appendix

- **animated_compare.py** — visualization of Fixed / Adaptive / RL modes  
- **train_rl.py** — reinforcement learning training script  
- **analyze_log.py** — performance analysis and plots  
- **vehicle.py** — vehicle dynamics model  
- **traffic_light.py** — traffic light logic  
- **intersection_env.py** — custom RL environment  
- **data/** — simulation logs (CSV)  
- **visuals/** — plots and animation outputs  
- **archive/** — legacy scripts for reference
