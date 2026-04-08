from typing import List, Optional
from openenv.core.env_server import Action, Observation, State

class TrafficAction(Action):
    """Which lane gets the green light."""
    lane: int                    # 0=North, 1=South, 2=East, 3=West

class TrafficObservation(Observation):
    """What the agent sees after each step."""
    lanes: List[int]             # Cars waiting e.g. [3, 0, 5, 2]
    total_wait: int              # Sum of all waiting cars
    message: str                 # Human readable feedback
    surge_active: bool = False   # True during rush hour windows
    surge_lanes: List[int] = []  

class TrafficState(State):
    """Episode metadata."""
    max_steps: int = 100
    current_step: int = 0
    total_reward: float = 0.0