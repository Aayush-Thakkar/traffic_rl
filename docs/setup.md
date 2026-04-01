# Setup Guide

## Prerequisites

- Python 3.9+
- pip
- An OpenAI-compatible API key (only needed for LLM inference)

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd traffic_rl
```

---

## 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the Environment Server

The FastAPI server must be running before you train or run inference.

```bash
uvicorn traffic_env.server.app:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Verify it's live by visiting `http://127.0.0.1:8000/tasks` in your browser.

---

## 5. Train the RL Agent

```bash
python train.py
```

- Runs 1000 episodes
- Prints avg reward every 50 episodes
- Saves `training_progress.png` when done

> The training loop imports the environment directly (no HTTP), so the server does not need to be running for training.

---

## 6. Run LLM Inference

Set these environment variables before running:

```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=<your_api_key>
export ENV_URL=http://127.0.0.1:8000
```

Then:

```bash
python inference.py
```

The server **must be running** for inference since it communicates over HTTP.

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `https://api.openai.com/v1` | Base URL for OpenAI-compatible API |
| `MODEL_NAME` | `gpt-4o-mini` | Model to use for inference |
| `HF_TOKEN` | `""` | Your API key |
| `ENV_URL` | `http://127.0.0.1:8000` | URL of the running FastAPI server |

---

## Common Issues

**Port already in use**
```bash
uvicorn traffic_env.server.app:app --port 8001
export ENV_URL=http://127.0.0.1:8001
```

**Module not found errors**
Make sure you're running commands from the `traffic_rl/` root directory, not from inside a subdirectory.

**API key errors**
Ensure `HF_TOKEN` is set and valid for the model you're using.
