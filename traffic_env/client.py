from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from traffic_env.models import TrafficAction, TrafficObservation, TrafficState

class TrafficEnv(EnvClient[TrafficAction, TrafficObservation, TrafficState]):

    def _step_payload(self, action: TrafficAction) -> dict:
        return {"lane": action.lane}

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})
        return StepResult(
            observation=TrafficObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                lanes=obs_data.get("lanes", [0, 0, 0, 0]),
                total_wait=obs_data.get("total_wait", 0),
                message=obs_data.get("message", ""),
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> TrafficState:
        return TrafficState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            max_steps=payload.get("max_steps", 100),
            current_step=payload.get("current_step", 0),
            total_reward=payload.get("total_reward", 0.0),
        )