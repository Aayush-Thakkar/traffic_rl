from openenv.core.env_server import create_fastapi_app
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from traffic_env.models import TrafficAction, TrafficObservation
from traffic_env.server.environment import TrafficEnvironment
from traffic_env.tasks import ALL_TASKS, Task1Easy, Task2Medium, Task3Hard
import random

# Persistent environment instance
_env = TrafficEnvironment()

# Create a base app FIRST and register our routes before OpenEnv adds its own
app = FastAPI(title="OpenEnv Environment HTTP API", version="1.0.0")

@app.post("/reset")
def reset():
    obs = _env.reset()
    return {
        "observation": {
            "lanes": obs.lanes,
            "total_wait": obs.total_wait,
            "message": obs.message,
            "surge_active": obs.surge_active,
            "surge_lanes": obs.surge_lanes,
        },
        "reward": obs.reward,
        "done": obs.done,
    }

@app.post("/step")
def step(request: dict):
    lane = request.get("action", {}).get("lane", 0)
    obs = _env.step(TrafficAction(lane=lane))
    return {
        "observation": {
            "lanes": obs.lanes,
            "total_wait": obs.total_wait,
            "message": obs.message,
            "surge_active": obs.surge_active,
            "surge_lanes": obs.surge_lanes,
        },
        "reward": obs.reward,
        "done": obs.done,
    }

# Now let OpenEnv register its remaining routes (/health, /schema, /metadata, /mcp etc)
from openenv.core.env_server.http_server import HTTPEnvServer
_server = HTTPEnvServer(TrafficEnvironment, TrafficAction, TrafficObservation)
_server.register_routes(app)

# --- / root endpoint ---
@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(content="""
    <html>
    <head><meta charset="utf-8"><title>Smart Traffic Controller API</title></head>
    <body style="font-family: sans-serif; max-width: 640px; margin: 40px auto; color: #222;">
        <h2>&#x1F6A6; Smart Traffic Controller API</h2>
        <p>Server is running. Available endpoints:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%;">
            <tr style="background:#f0f0f0;"><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>POST</td><td><a href="/docs#/default/reset">/reset</a></td><td>Start a new episode</td></tr>
            <tr><td>POST</td><td><a href="/docs#/default/step">/step</a></td><td>Send action {"lane": 0-3}</td></tr>
            <tr><td>GET</td><td><a href="/tasks">/tasks</a></td><td>List all tasks</td></tr>
            <tr><td>GET</td><td><a href="/grader/task1_easy">/grader/{task_id}</a></td><td>Grade random agent on a task</td></tr>
            <tr><td>GET</td><td><a href="/baseline">/baseline</a></td><td>Run random agent on all tasks</td></tr>
            <tr><td>GET</td><td><a href="/docs">/docs</a></td><td>Interactive Swagger UI</td></tr>
            <tr><td>GET</td><td><a href="/redoc">/redoc</a></td><td>ReDoc API reference</td></tr>
        </table>
    </body>
    </html>
    """)

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