import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from vehicle import Vehicle, STOP_LINE_DISTANCE
from traffic_light import TrafficLight


class IntersectionEnv(gym.Env):
    """
    Custom Gymnasium environment for a V2X traffic light control simulation.

    State space:
        - queue_x: number of stopped vehicles in the X direction
        - queue_y: number of stopped vehicles in the Y direction
        - light_state: 0 if X is green, 1 if Y is green

    Action space:
        - 0: keep current signal
        - 1: request switch (may trigger yellow and then switch)

    Reward:
        - Negative for queues and crashes
        - Positive for vehicles successfully passing the intersection
        - Small penalty for switching too often
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, num_vehicles_x=8, num_vehicles_y=8, sim_duration=120, dt=0.25):
        super(IntersectionEnv, self).__init__()
        self.num_vehicles_x = num_vehicles_x
        self.num_vehicles_y = num_vehicles_y
        self.sim_duration = sim_duration
        self.dt = dt
        self.time = 0

        self.light = TrafficLight(position=0, mode="rl")
        self.vehicles = []
        self.last_action = 0
        self.action_interval = 8  # agent can act every 8 steps (~2 seconds)
        self.step_counter = 0

        # Observation: [queue_x, queue_y, light_state]
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(3,), dtype=np.float32
        )

        # Actions: 0 = hold, 1 = switch
        self.action_space = spaces.Discrete(2)

    def reset(self, seed=None, options=None):
        """
        Reset the environment to the initial state.
        """
        super().reset(seed=seed)
        random.seed(seed)
        self.time = 0
        self.step_counter = 0
        self.light = TrafficLight(position=0, mode="rl")
        self.vehicles = self._generate_vehicles()
        return self._get_obs(), {}

    def step(self, action):
        """
        Perform one simulation step.
        """
        self.time += self.dt
        self.step_counter += 1
        done = self.time >= self.sim_duration

        # Apply action only every `action_interval` steps
        rl_action = self.last_action
        if self.step_counter % self.action_interval == 0:
            rl_action = action
            self.last_action = action

        self.light.update(self.dt, rl_action=rl_action)

        crashes, queue_x, queue_y, passed = 0, 0, 0, 0

        for v in self.vehicles:
            if v.direction == "x":
                front = min(
                    [ov for ov in self.vehicles if ov.direction == "x" and ov.x > v.x],
                    key=lambda x: x.x,
                    default=None,
                )
            else:
                front = min(
                    [ov for ov in self.vehicles if ov.direction == "y" and ov.y > v.y],
                    key=lambda x: x.y,
                    default=None,
                )

            v.move(self.dt, front_vehicle=front, light=self.light, light_pos=0)

            if v.stopped:
                if v.direction == "x":
                    queue_x += 1
                else:
                    queue_y += 1

            if (v.direction == "x" and v.x >= 0) or (v.direction == "y" and v.y >= 0):
                passed += 1

        # Detect collisions (two vehicles in the same position)
        positions = [(round(v.x, 1), round(v.y, 1)) for v in self.vehicles]
        if len(positions) != len(set(positions)):
            crashes += 1

        # Reward function
        reward = - (queue_x + queue_y) - 10 * crashes + 3 * passed
        if rl_action == 1:
            reward -= 2  # penalty for frequent switching

        obs = self._get_obs(queue_x, queue_y)
        info = {"queue_x": queue_x, "queue_y": queue_y, "crashes": crashes, "passed": passed}
        return obs, reward, done, False, info

    def _generate_vehicles(self):
        """
        Generate initial vehicles for both X and Y directions.
        Includes one random "troublemaker" vehicle.
        """
        vehicles, vid = [], 0
        troublemaker_id = random.randint(0, self.num_vehicles_x + self.num_vehicles_y - 1)

        for lane in [-3, +3]:
            pos = -60
            for _ in range(self.num_vehicles_x // 2):
                v = Vehicle(vid, "x", pos, lane, vid == troublemaker_id)
                vehicles.append(v)
                pos -= random.randint(15, 25)
                vid += 1

        for lane in [-3, +3]:
            pos = -60
            for _ in range(self.num_vehicles_y // 2):
                v = Vehicle(vid, "y", pos, lane, vid == troublemaker_id)
                vehicles.append(v)
                pos -= random.randint(15, 25)
                vid += 1

        return vehicles

    def _get_obs(self, queue_x=None, queue_y=None):
        """
        Construct the observation vector: [queue_x, queue_y, light_state].
        """
        if queue_x is None or queue_y is None:
            queue_x = sum(1 for v in self.vehicles if v.direction == "x" and v.stopped)
            queue_y = sum(1 for v in self.vehicles if v.direction == "y" and v.stopped)
        state_num = 0 if self.light.state.startswith("green_x") else 1
        return np.array([queue_x, queue_y, state_num], dtype=np.float32)
