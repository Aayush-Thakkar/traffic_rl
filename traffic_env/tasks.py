from dataclasses import dataclass
from typing import List

@dataclass
class TaskResult:
    task_id: str
    score: float        # always between 0.0 and 1.0
    passed: bool
    message: str

class Task1Easy:
    """
    Easy: Keep total wait under 20 in 50 steps.
    Score 1.0 if achieved, 0.0 if not.
    """
    id = "task1_easy"
    description = "Keep total waiting cars under 20 for 50 steps"
    max_steps = 50

    def grade(self, history: List[int]) -> TaskResult:
        # history = list of total_wait values per step
        passed = all(wait < 20 for wait in history)
        score = 1.0 if passed else round(
            sum(1 for w in history if w < 20) / len(history), 2
        )
        return TaskResult(
            task_id=self.id,
            score=score,
            passed=passed,
            message=f"Kept wait under 20 for {int(score*100)}% of steps"
        )

class Task2Medium:
    """
    Medium: Keep average wait under 5 per step for 100 steps.
    Partial score based on how close to target.
    """
    id = "task2_medium"
    description = "Keep average wait under 5 cars per step across 100 steps"
    max_steps = 100

    def grade(self, history: List[int]) -> TaskResult:
        avg_wait = sum(history) / len(history)
        target = 5.0

        if avg_wait <= target:
            score = 1.0
            passed = True
        else:
            # Partial score — closer to target = higher score
            score = round(max(0.0, 1.0 - (avg_wait - target) / 20.0), 2)
            passed = False

        return TaskResult(
            task_id=self.id,
            score=score,
            passed=passed,
            message=f"Average wait was {avg_wait:.1f} (target: <{target})"
        )

class Task3Hard:
    """
    Hard: No single lane exceeds 10 cars for entire 100 step episode.
    Score based on how long all lanes stayed balanced.
    """
    id = "task3_hard"
    description = "Keep all lanes under 10 cars for entire episode"
    max_steps = 100

    def grade(self, lane_history: List[List[int]]) -> TaskResult:
        # lane_history = list of lane snapshots e.g [[3,0,5,2], [4,1,5,2]...]
        balanced_steps = sum(
            1 for lanes in lane_history if max(lanes) < 10
        )
        score = round(balanced_steps / len(lane_history), 2)
        passed = score == 1.0

        return TaskResult(
            task_id=self.id,
            score=score,
            passed=passed,
            message=f"All lanes balanced for {int(score*100)}% of steps"
        )

# Export all tasks
ALL_TASKS = [Task1Easy(), Task2Medium(), Task3Hard()]