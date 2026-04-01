from traffic_env.server.environment import TrafficEnvironment
from traffic_env.models import TrafficAction
import random

env = TrafficEnvironment()

# --- DUMB AGENT ---
obs = env.reset()
print("--- DUMB AGENT (random lane) ---")
print(f"Episode started | Lanes: {obs.lanes}")
print("-" * 50)
total_reward = 0

for step in range(100):
    action = TrafficAction(lane=random.randint(0, 3))
    obs = env.step(action)
    total_reward += obs.reward
    print(
        f"Step {step+1:3d} | "
        f"Green: Lane {action.lane} | "
        f"Lanes: {obs.lanes} | "
        f"Wait: {obs.total_wait} | "
        f"Reward: {obs.reward:.1f}"
    )

print("-" * 50)
print(f"Dumb agent total reward: {total_reward:.1f}")

# --- SMART AGENT ---
obs = env.reset()
print("\n--- SMART AGENT (always picks busiest lane) ---")
print(f"Episode started | Lanes: {obs.lanes}")
print("-" * 50)
total_reward = 0

for step in range(100):
    busiest_lane = obs.lanes.index(max(obs.lanes))
    action = TrafficAction(lane=busiest_lane)
    obs = env.step(action)
    total_reward += obs.reward
    print(
        f"Step {step+1:3d} | "
        f"Green: Lane {action.lane} | "
        f"Lanes: {obs.lanes} | "
        f"Wait: {obs.total_wait} | "
        f"Reward: {obs.reward:.1f}"
    )

print("-" * 50)
print(f"Smart agent total reward: {total_reward:.1f}")
print("\nRL agent goal: beat both these scores.")