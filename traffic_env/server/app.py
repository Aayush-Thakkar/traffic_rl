from openenv.core.env_server import create_fastapi_app
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from traffic_env.models import TrafficAction, TrafficObservation
from traffic_env.server.environment import TrafficEnvironment
from traffic_env.tasks import ALL_TASKS, Task1Easy, Task2Medium, Task3Hard
import random

# Core OpenEnv app
app = create_fastapi_app(TrafficEnvironment, TrafficAction, TrafficObservation)

# --- /tasks endpoint ---
@app.get("/tasks")
def get_tasks():
    return JSONResponse([
        {
            "id": t.id,
            "description": t.description,
            "max_steps": t.max_steps,
            "action_schema": {"lane": "int (0-3)"}
        }
        for t in ALL_TASKS
    ])

# --- /grader endpoint ---
@app.get("/grader/{task_id}")
def grade_task(task_id: str):
    env = TrafficEnvironment()
    obs = env.reset()

    wait_history = []
    lane_history = []

    # determine steps based on task
    task_map = {t.id: t for t in ALL_TASKS}
    if task_id not in task_map:
        return JSONResponse({"error": f"Unknown task: {task_id}"}, status_code=404)

    task = task_map[task_id]

    for _ in range(task.max_steps):
        action = TrafficAction(lane=random.randint(0, 3))
        obs = env.step(action)
        wait_history.append(obs.total_wait)
        lane_history.append(obs.lanes.copy())

    if task_id == "task1_easy":
        result = Task1Easy().grade(wait_history[:50])
    elif task_id == "task2_medium":
        result = Task2Medium().grade(wait_history)
    else:
        result = Task3Hard().grade(lane_history)

    return JSONResponse({
        "task_id": result.task_id,
        "score": result.score,
        "passed": result.passed,
        "message": result.message
    })

# --- /baseline endpoint ---
@app.get("/baseline")
def baseline():
    results = []
    for task in ALL_TASKS:
        env = TrafficEnvironment()
        obs = env.reset()
        wait_history = []
        lane_history = []

        for _ in range(task.max_steps):
            action = TrafficAction(lane=random.randint(0, 3))
            obs = env.step(action)
            wait_history.append(obs.total_wait)
            lane_history.append(obs.lanes.copy())

        if task.id == "task1_easy":
            result = Task1Easy().grade(wait_history[:50])
        elif task.id == "task2_medium":
            result = Task2Medium().grade(wait_history)
        else:
            result = Task3Hard().grade(lane_history)

        results.append({
            "task_id": result.task_id,
            "score": result.score,
            "passed": result.passed,
            "message": result.message
        })

    return JSONResponse(results)