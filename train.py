import sys
import os

# Make sure traffic_env is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from traffic_env.server.environment import TrafficEnvironment
from traffic_env.models import TrafficAction
from agent import QLearningAgent
import matplotlib.pyplot as plt

# --- SETUP ---
env = TrafficEnvironment()
agent = QLearningAgent(learning_rate=0.3, gamma=0.9, epsilon_decay=0.99)

EPISODES = 1000          # train for 500 episodes
rewards_per_episode = [] # track total reward each episode

print("Training started...")
print("-" * 50)

# --- TRAINING LOOP ---
for episode in range(EPISODES):

    obs = env.reset()              # fresh episode
    total_reward = 0
    done = False

    while not done:
        # Agent looks at current lanes and picks a lane
        action_idx = agent.choose_action(obs.lanes)

        # Environment executes the action
        obs_next = env.step(TrafficAction(lane=action_idx))

        # Agent learns from what happened
        agent.update(
            lanes=obs.lanes,
            action=action_idx,
            reward=obs_next.reward,
            next_lanes=obs_next.lanes,
            done=obs_next.done
        )

        total_reward += obs_next.reward
        obs = obs_next
        done = obs_next.done

    # After each episode, reduce exploration
    agent.decay_epsilon()
    rewards_per_episode.append(total_reward)

    # Print progress every 50 episodes
    if (episode + 1) % 50 == 0:
        avg = sum(rewards_per_episode[-50:]) / 50
        print(
            f"Episode {episode+1:4d} | "
            f"Avg Reward (last 50): {avg:.1f} | "
            f"Epsilon: {agent.epsilon:.3f}"
        )

print("-" * 50)
print("Training complete!")

# --- PLOT ---
plt.figure(figsize=(10, 5))
plt.plot(rewards_per_episode, alpha=0.4, label='Raw reward')

# Smooth the curve with rolling average
window = 20
smoothed = [
    sum(rewards_per_episode[max(0, i-window):i+1]) / 
    min(window, i+1) 
    for i in range(len(rewards_per_episode))
]
plt.plot(smoothed, label='Smoothed (20 ep)', linewidth=2)

plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('RL Agent Learning Progress')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('training_progress.png')
print("Plot saved as training_progress.png")