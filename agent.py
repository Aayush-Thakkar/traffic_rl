import numpy as np
import random

class QLearningAgent:
    def __init__(self, n_actions=4, learning_rate=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        # n_actions = 4 lanes to choose from
        self.n_actions = n_actions

        # learning_rate = how fast agent updates its knowledge
        self.lr = learning_rate

        # gamma = how much agent cares about future rewards vs immediate
        self.gamma = gamma

        # epsilon = exploration rate (1.0 = fully random, 0.01 = mostly smart)
        self.epsilon = epsilon

        # epsilon_decay = how fast agent stops exploring and starts exploiting
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q table — dictionary mapping state → [value of each action]
        self.q_table = {}

    def _state_key(self, lanes):
    # Bucket lane counts into 4 categories instead of exact numbers
        def bucket(n):
            if n == 0:    return 0  # empty
            elif n <= 3:  return 1  # light
            elif n <= 7:  return 2  # medium
            else:         return 3  # heavy
        return tuple(bucket(n) for n in lanes)

    def get_q_values(self, lanes):
        # Look up Q values for this state, create if not seen before
        key = self._state_key(lanes)
        if key not in self.q_table:
            # Initialize all actions with 0 value for new states
            self.q_table[key] = np.zeros(self.n_actions)
        return self.q_table[key]

    def choose_action(self, lanes):
        # Epsilon-greedy: explore randomly OR exploit best known action
        if random.random() < self.epsilon:
            # Explore — pick random lane
            return random.randint(0, self.n_actions - 1)
        else:
            # Exploit — pick lane with highest Q value
            return int(np.argmax(self.get_q_values(lanes)))

    def update(self, lanes, action, reward, next_lanes, done):
        # This is the core Q-learning formula
        current_q = self.get_q_values(lanes)[action]

        if done:
            target = reward
        else:
            # Reward now + discounted best future reward
            target = reward + self.gamma * np.max(self.get_q_values(next_lanes))

        # Update Q value for this state-action pair
        self.q_table[self._state_key(lanes)][action] += self.lr * (target - current_q)

    def decay_epsilon(self):
        # After each episode, reduce exploration rate
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)