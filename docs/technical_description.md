# 📝 Technical Description

**Project:** V2X Traffic Light Simulation  
**Author:** Alina Dobershteyjn 
**Year:** 2025  

---

## 1. Project Topic

Simulation of an adaptive traffic light that uses V2I (Vehicle-to-Infrastructure) communication to regulate road traffic based on vehicle density.

---

## 2. Objective

To design and study a simple model of interaction between vehicles and a traffic light using V2X data exchange.  
The goal is to optimize waiting time and reduce traffic queue length at an intersection.

---

## 3. Tasks

- Implement a Python model of a road, vehicles, and a traffic light.
- Add V2I communication: vehicles transmit their data to the traffic light.
- Implement two operating modes:
  - **Adaptive Mode** — decision-making based on real-time V2X input.
  - **Fixed-Timer Mode** — regular phase switching without feedback.
- Compare the efficiency of both approaches using queue length metrics.
- Visualize vehicle movement and analytical results.

---

## 4. Technologies Used

- **Programming Language:** Python 3.10+
- **Libraries:** `matplotlib`
- **Data format:** CSV
- **Visualization:** static plots and animated GIF
- **Development Tools:** VS Code, Jupyter Notebook, or any Python IDE

---

## 5. Model Description

### Entities:

- **Vehicle:**  
  Stores coordinates, speed, and status (moving/stopped).  
  Sends data to the traffic light via V2I.

- **TrafficLight:**  
  Has a position and a signal state (green/red).  
  In adaptive mode, it analyzes V2I input and decides whether to switch the signal.

### Key Parameters:

| Parameter                  | Value                          |
|----------------------------|---------------------------------|
| Number of vehicles         | 5                               |
| Traffic light position     | 100 meters                     |
| Stop threshold             | 5 meters                       |
| V2I trigger condition      | ≥3 vehicles within 30 meters   |

---

## 6. Results

- **Queue length graph over time**  
  → Adaptive mode showed a significant reduction in the number of stopped vehicles.

- **Mode comparison (file: `queue_comparison.png`)**  
  → The adaptive traffic light reduced delay by up to ~40%.

- **Animation (`traffic_animation.gif`)**  
  Visualizes red-light stops and dynamic signal control.

- **V2X Diagram (`v2x_diagram.png`)**  
  Shows the data exchange zone and the role of the traffic light in decision-making.

---

## 7. Conclusion

Even a basic V2I simulation improves traffic efficiency.  
This project can serve as a foundation for more advanced systems involving:
- multi-lane control,  
- multiple intersections,  
- predictive analytics.

Python implementation ensures accessibility, extensibility, and visual clarity.

---

## 8. Attachments

- `simulation.py` — core simulation logic  
- `animated_simulation.py` — animated movement with matplotlib  
- `compare_simulation.py` — side-by-side comparison of modes  
- `visuals/` — graphs, diagrams, and GIFs  
- `README.md` — project overview and usage instructions