# API Reference

Base URL: `http://127.0.0.1:8000` (default)

---

## `POST /reset`

Starts a fresh episode. Call this before every new run.

**Request body:** none

**Response:**
```json
{
  "observation": {
    "lanes": [0, 0, 0, 0],
    "total_wait": 0,
    "message": "Episode started. All lanes clear."
  },
  "done": false,
  "reward": null
}
```

---

## `POST /step`

Sends an action (which lane gets the green light) and advances the simulation by one step.

**Request body:**
```json
{
  "action": {
    "lane": 2
  }
}
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `lane` | int | 0–3 | 0=North, 1=South, 2=East, 3=West |

**Response:**
```json
{
  "observation": {
    "lanes": [1, 0, 2, 3],
    "total_wait": 6,
    "message": "Step 1: Green→Lane 2 | Lanes: [1, 0, 2, 3] | Wait: 6"
  },
  "reward": -0.6,
  "done": false
}
```

| Field | Description |
|-------|-------------|
| `lanes` | Cars waiting in each lane after this step |
| `total_wait` | Sum of all lanes |
| `reward` | `-(total_wait) / 10.0` — negative, closer to 0 is better |
| `done` | `true` when episode reaches `max_steps` (100) |

---

## `GET /tasks`

Lists all available tasks.

**Response:**
```json
[
  {
    "id": "task1_easy",
    "description": "Keep total waiting cars under 20 for 50 steps",
    "max_steps": 50,
    "action_schema": {"lane": "int (0-3)"}
  },
  ...
]
```

---

## `GET /grader/{task_id}`

Runs a **random agent** internally for the given task and returns a grade.

> This does NOT evaluate your trained or LLM agent. It always uses `random.randint(0, 3)`.

**Path parameter:** `task_id` — one of `task1_easy`, `task2_medium`, `task3_hard`

**Response:**
```json
{
  "task_id": "task1_easy",
  "score": 0.48,
  "passed": false,
  "message": "Kept wait under 20 for 48% of steps"
}
```

| Field | Description |
|-------|-------------|
| `score` | Float between 0.0 and 1.0 |
| `passed` | `true` only if fully meeting the task condition |
| `message` | Human-readable summary of performance |

---

## `GET /baseline`

Runs the random agent on all 3 tasks and returns results for each.

**Response:**
```json
[
  {"task_id": "task1_easy", "score": 0.48, "passed": false, "message": "..."},
  {"task_id": "task2_medium", "score": 0.0, "passed": false, "message": "Average wait was 37.9 (target: <5.0)"},
  {"task_id": "task3_hard", "score": 0.39, "passed": false, "message": "..."}
]
```

Use this as a **lower bound** — any smart agent should score higher than this.

---

## Error Responses

| Status | Cause |
|--------|-------|
| `404` | Unknown `task_id` passed to `/grader` |
| `422` | Malformed request body (missing or wrong type for `lane`) |
