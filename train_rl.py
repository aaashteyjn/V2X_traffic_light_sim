import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from intersection_env import IntersectionEnv

def make_env():
    """
    Factory function to create a new instance of the intersection environment.
    """
    return IntersectionEnv(sim_duration=120, dt=0.25)

# Vectorized environment for Stable Baselines
env = DummyVecEnv([make_env])

# Define PPO model
model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1, 
    n_steps=1024, 
    batch_size=64, 
    learning_rate=3e-4
)

print("Training RL agent... (this may take several minutes)")
model.learn(total_timesteps=300_000)  # increased training steps for better performance

# Save the trained model
model.save("traffic_rl_model")
print("Model saved as traffic_rl_model.zip")
