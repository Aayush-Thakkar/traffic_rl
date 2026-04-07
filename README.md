---
title: Smart Traffic Controller
emoji: 🚦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# Smart Traffic Controller — RL + LLM

An AI-powered traffic light controller for a 4-way intersection. Supports two agent types:
- **Q-Learning agent** trained via reinforcement learning
- **LLM agent** using an OpenAI-compatible model for zero-shot control

Built on top of [OpenEnv](https://github.com/meta-pytorch/OpenEnv) with a FastAPI simulation server.

---

## How It Works

A 4-lane intersection (North, South, East, West) simulates cars arriving randomly each step (`40%` probability per lane). The agent picks one lane to give a green light, clearing one car. The goal is to minimize total waiting cars across all lanes.

```
Reward = -(total_wait) / 10.0   per step
```

A reward closer to `0` means fewer cars waiting — better performance.

---

## Project Structure

```
traffic_rl/
├── traffic_env/
│   ├── server/
│   │   ├── app.py           # FastAPI server (endpoints)
│   │   └── environment.py   # Simulation logic + reward
│   ├── models.py            # Pydantic models (Action, Observation, State)
│   ├── tasks.py             # Task definitions + graders
│   └── client.py            # HTTP client helpers
├── agent.py                 # Q-Learning agent
├── train.py                 # RL training loop
├── inference.py             # LLM agent inference
├── openenv.yaml             # Environment config
└── requirements.txt
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the environment server

```bash
uvicorn traffic_env.server.app:app --host 0.0.0.0 --port 8000
```

### 3. Train the RL agent

```bash
python train.py
```

Trains for 1000 episodes and saves a `training_progress.png` plot.

### 4. Run LLM inference

Set environment variables first:

```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=<your_api_key>
export ENV_URL=http://127.0.0.1:8000
```

Then run:

```bash
python inference.py
```

---

## Tasks

| Task | Difficulty | Steps | Goal |
|------|------------|-------|------|
| `task1_easy` | Easy | 50 | Keep total wait < 20 every step |
| `task2_medium` | Medium | 100 | Keep average wait < 5 per step |
| `task3_hard` | Hard | 100 | Keep all lanes under 10 cars at all times |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Start a new episode |
| `POST` | `/step` | Send an action `{"action": {"lane": 0-3}}` |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/grader/{task_id}` | Grade a random agent on a task |
| `GET` | `/baseline` | Run random agent on all tasks |

---

## Agents

### Q-Learning Agent (`agent.py`)
- Tabular Q-learning with bucketed state space (empty / light / medium / heavy per lane)
- Epsilon-greedy exploration with decay
- Hyperparameters: `lr=0.3`, `gamma=0.9`, `epsilon_decay=0.99`

### LLM Agent (`inference.py`)
- Sends current lane counts to any OpenAI-compatible model
- Prompts the model to pick the busiest lane
- Falls back to `argmax(lanes)` if model output is unparseable

---

## Results (LLM Agent — gpt-4o-mini)

| Task | Total Reward | Avg Wait/Step |
|------|-------------|---------------|
| task1_easy | -6.1 | ~1.2 cars |
| task2_medium | -11.7 | ~1.2 cars |
| task3_hard | -13.0 | ~1.3 cars |

Random baseline averages ~37.9 cars waiting per step on task2_medium.

---

## Design Tradeoff: Stateless Decision Making

The agent operates purely on current state, mirroring how many real traffic controllers work today. Adding a sliding window of historical lane counts to the prompt is a natural next step that would enable trend detection and proactive signal switching.

This was an intentional choice — real-world traffic signals react to present conditions without access to historical queues. Keeping the agent stateless means shorter prompts, faster inference, and simpler architecture with no state management overhead.

### Future Work

- Add a sliding window of the last 3–5 steps of lane counts to the LLM prompt
- This enables trend detection (e.g. a lane growing steadily) and proactive signal switching before a lane overflows
- Tradeoff: longer prompts increase token usage and add slight latency — manageable with efficient models like Llama 3.1 8B

---

## License

MIT — see [LICENSE](LICENSE)
