import random
import uuid
from openenv.core.env_server import Environment
from traffic_env.models import TrafficAction, TrafficObservation, TrafficState

NUM_LANES = 4
MAX_STEPS = 100
CAR_ARRIVAL_PROB = 0.4

class TrafficEnvironment(Environment):

    def __init__(self):
        self._lanes = [0] * NUM_LANES
        self._state = TrafficState()
        self._current_step = 0
        self._total_reward = 0.0

    def reset(self) -> TrafficObservation:
        """Start a fresh episode."""
        self._lanes = [0] * NUM_LANES
        self._current_step = 0
        self._total_reward = 0.0
        self._state = TrafficState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            max_steps=MAX_STEPS,
            current_step=0,
            total_reward=0.0,
        )
        return TrafficObservation(
            done=False,
            reward=None,
            lanes=self._lanes.copy(),
            total_wait=sum(self._lanes),
            message="Episode started. All lanes clear.",
        )

    def step(self, action: TrafficAction) -> TrafficObservation:
        """Agent picks a lane, simulation runs one step."""
        self._current_step += 1
        self._state.step_count += 1

        # --- CAR ARRIVALS ---
        for i in range(NUM_LANES):
            if random.random() < CAR_ARRIVAL_PROB:
                self._lanes[i] += 1

        # --- AGENT DECISION ---
        green = action.lane
        if self._lanes[green] > 0:
            self._lanes[green] -= 1

        # --- REWARD ---
        total_wait = sum(self._lanes)
        reward = -float(total_wait) / 10.0 #scale down reward
        self._total_reward += reward
        self._state.total_reward = self._total_reward
        self._state.current_step = self._current_step

        # --- DONE? ---
        done = self._current_step >= MAX_STEPS

        message = (
            f"Step {self._current_step}: Green→Lane {green} | "
            f"Lanes: {self._lanes} | Wait: {total_wait}"
        )

        return TrafficObservation(
            done=done,
            reward=reward,
            lanes=self._lanes.copy(),
            total_wait=total_wait,
            message=message,
        )

    @property
    def state(self) -> TrafficState:
        return self._state