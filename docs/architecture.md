# Architecture

## Overview

The project is split into two sides — a **server** (the environment) and a **client** (the agent). They communicate over HTTP. The server knows nothing about which agent is playing; it just simulates traffic and responds to actions.

```
┌──────────────────────────────────┐        ┌──────────────────────────────┐
│           CLIENT SIDE            │        │         SERVER SIDE          │
│                                  │        │                              │
│  inference.py  (LLM agent)       │──POST /step──▶  app.py (FastAPI)     │
│  train.py      (RL training)     │◀──observation──  environment.py      │
│  agent.py      (Q-table logic)   │        │                              │
└──────────────────────────────────┘        └──────────────────────────────┘
```

> `train.py` is an exception — it imports `TrafficEnvironment` directly (no HTTP) for speed.

---

## Server (`traffic_env/server/`)

### `environment.py` — Simulation Core

The single source of truth for the traffic world.

- Maintains lane state: `[north, south, east, west]` car counts
- Each `step()` call:
  1. Adds cars randomly (40% chance per lane)
  2. Clears 1 car from the agent's chosen lane
  3. Computes reward: `-(total_wait) / 10.0`
- `reset()` wipes all state and starts a fresh episode

### `app.py` — FastAPI Layer

Wraps the environment in HTTP. Also contains `/grader` and `/baseline` which run their own **internal random agent** — they do not use your trained or LLM agent.

---

## Client Side

### `agent.py` — Q-Learning Agent

- State space: each lane bucketed into 4 levels (empty / light / medium / heavy) → `4^4 = 256` possible states
- Q-table stored as a Python dictionary
- Epsilon-greedy exploration decaying each episode

### `train.py` — Training Loop

- Runs 1000 episodes directly against `TrafficEnvironment` (no HTTP)
- Saves `training_progress.png` at the end

### `inference.py` — LLM Agent

- Calls the FastAPI server over HTTP each step
- Formats lane counts into a natural language prompt
- Parses a single digit (`0–3`) from the model response
- Falls back to `argmax(lanes)` if parsing fails

---

## Data Flow (one step)

```
agent picks lane
      │
      ▼
POST /step  {"action": {"lane": 2}}
      │
      ▼
environment.py
  1. add cars (random arrivals)
  2. clear 1 car from lane 2
  3. compute reward = -(total_wait) / 10.0
      │
      ▼
response: { observation: {lanes, total_wait}, reward, done }
      │
      ▼
agent reads observation → picks next lane
```

---

## Data Models (`traffic_env/models.py`)

| Model | Fields |
|-------|--------|
| `TrafficAction` | `lane: int` (0–3) |
| `TrafficObservation` | `lanes: List[int]`, `total_wait: int`, `message: str` |
| `TrafficState` | `episode_id`, `step_count`, `max_steps`, `current_step`, `total_reward` |

---

## Task Grading (`traffic_env/tasks.py`)

Grading is stateless — you pass in collected history and get a score back.

| Task | Input | Pass Condition | Score |
|------|-------|----------------|-------|
| `task1_easy` | `wait_history` (50 values) | All values < 20 | Binary (1.0 or partial) |
| `task2_medium` | `wait_history` (100 values) | Average < 5.0 | Partial based on distance to target |
| `task3_hard` | `lane_history` (100 snapshots) | No lane ever ≥ 10 | % of balanced steps |
