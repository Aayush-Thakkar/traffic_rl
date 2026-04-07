import random
import uuid
from openenv.core.env_server import Environment
from traffic_env.models import TrafficAction, TrafficObservation, TrafficState

NUM_LANES = 4
MAX_STEPS = 100
CAR_ARRIVAL_PROB = 0.4

# --- TIME-OF-DAY SCHEDULE ---
# 100 steps × 5 min/step = 500 min ≈ 8 hours (7:00am–3:00pm weekday)
# Each entry: (start_step, end_step, arrival_prob, surge, label)
TIME_SCHEDULE = [
    (0,   11,  0.20, False, "7:00am–8:00am  early morning"),
    (12,  23,  0.80, True,  "8:00am–9:00am  morning rush"),
    (24,  47,  0.40, False, "9:00am–1:00pm  midday"),
    (48,  59,  0.50, False, "1:00pm–2:00pm  lunch"),
    (60,  71,  0.40, False, "2:00pm–3:00pm  afternoon"),
    (72,  83,  0.55, False, "3:00pm–4:00pm  pre-rush"),
    (84,  95,  0.80, True,  "4:00pm–5:00pm  evening rush"),
    (96,  99,  0.25, False, "5:00pm–5:20pm  winding down"),
]

def _get_time_slot(step: int) -> tuple:
    """Return (arrival_prob, surge, label) for the given step."""
    for start, end, prob, surge, label in TIME_SCHEDULE:
        if start <= step <= end:
            return prob, surge, label
    return CAR_ARRIVAL_PROB, False, "unknown"

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

        # --- TIME SLOT ---
        arrival_prob, surge, time_label = _get_time_slot(self._current_step)

        # --- CAR ARRIVALS ---
        for i in range(NUM_LANES):
            if random.random() < arrival_prob:
                self._lanes[i] += 1

        # --- SURGE: 2 random lanes get +2 extra cars during rush hours ---
        surge_lanes = []
        if surge:
            surge_lanes = random.sample(range(NUM_LANES), 2)
            for i in surge_lanes:
                self._lanes[i] += 2

        # --- AGENT DECISION ---
        green = action.lane
        if not (0 <= green < NUM_LANES):
            green = 0  # invalid lane fallback — default to lane 0
        if self._lanes[green] > 0:
            self._lanes[green] -= 1

        # --- REWARD ---
        total_wait = sum(self._lanes)
        reward = -float(total_wait) / 10.0
        self._total_reward += reward
        self._state.total_reward = self._total_reward
        self._state.current_step = self._current_step

        # --- DONE? ---
        done = self._current_step >= MAX_STEPS

        surge_tag = f" [RUSH HOUR: {time_label}]" if surge else f" [{time_label}]"
        message = (
            f"Step {self._current_step}: Green→Lane {green} | "
            f"Lanes: {self._lanes} | Wait: {total_wait}{surge_tag}"
        )

        return TrafficObservation(
            done=done,
            reward=reward,
            lanes=self._lanes.copy(),
            total_wait=total_wait,
            message=message,
            surge_active=surge,
            surge_lanes=surge_lanes,
        )

    @property
    def state(self) -> TrafficState:
        return self._state