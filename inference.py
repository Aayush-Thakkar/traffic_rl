import os
import requests
from openai import OpenAI
from typing import List, Optional

# --- CONFIG ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN", "")
ENV_URL      = os.getenv("ENV_URL", "http://127.0.0.1:8000")

# --- API KEY VALIDATION ---
if not HF_TOKEN:
    print("[WARN] HF_TOKEN is not set. LLM calls will fall back to argmax.", flush=True)

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# --- LOGGING (mandatory format) ---
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

# --- ENV CALLS ---
def reset_env():
    try:
        res = requests.post(f"{ENV_URL}/reset", timeout=30)
        return res.json()
    except Exception as e:
        print(f"[ERROR] Could not connect to environment at {ENV_URL}: {e}", flush=True)
        raise

def step_env(lane: int):
    try:
        res = requests.post(f"{ENV_URL}/step", json={"action": {"lane": lane}}, timeout=30)
        return res.json()
    except Exception as e:
        print(f"[ERROR] Step failed: {e}", flush=True)
        raise

# --- LLM AGENT ---
def ask_llm(observation: dict) -> int:
    lanes = observation["observation"]["lanes"]
    total_wait = observation["observation"]["total_wait"]
    surge_active = observation["observation"].get("surge_active", False)
    surge_lanes = observation["observation"].get("surge_lanes", [])

    lane_names = ["North", "South", "East", "West"]
    surge_context = ""
    if surge_active and surge_lanes:
        affected = " and ".join(f"{lane_names[i]} ({i})" for i in surge_lanes)
        surge_context = f"\n⚠️  RUSH HOUR ACTIVE — {affected} lanes have emergency vehicle surge. Prioritize these lanes."

    prompt = f"""You are a traffic light controller AI.
Current traffic state:
- North lane (0): {lanes[0]} cars waiting
- South lane (1): {lanes[1]} cars waiting
- East lane  (2): {lanes[2]} cars waiting
- West lane  (3): {lanes[3]} cars waiting
- Total waiting: {total_wait} cars{surge_context}
Which lane should get the green light RIGHT NOW?
Reply with ONLY a single digit: 0, 1, 2, or 3."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0.0,
        )
        reply = response.choices[0].message.content.strip()
        for char in reply:
            if char in "0123":
                return int(char)
    except Exception:
        pass

    # Fallback — busiest lane
    fallback = lanes.index(max(lanes))
    print(f"[FALLBACK] LLM response unparseable — defaulting to argmax lane {fallback}", flush=True)
    return fallback

# --- TASK RUNNER ---
def run_task(task_id: str, max_steps: int):
    log_start(task=task_id, env="smart-traffic-controller", model=MODEL_NAME)

    obs = reset_env()
    rewards: List[float] = []
    steps_taken = 0
    success = False

    try:
        for step in range(1, max_steps + 1):
            lane = ask_llm(obs)
            obs = step_env(lane)

            reward = float(obs.get("reward") or 0.0)
            done = bool(obs.get("done", False))
            error = None

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=str(lane), reward=reward, done=done, error=error)

            if done:
                break

        # success = average reward better than -0.5 per step
        success = len(rewards) > 0 and (sum(rewards) / len(rewards)) > -0.5

    finally:
        log_end(success=success, steps=steps_taken, rewards=rewards)

# --- MAIN ---
if __name__ == "__main__":
    tasks = [
        ("task1_easy",   50),
        ("task2_medium", 100),
        ("task3_hard",   100),
    ]
    for task_id, max_steps in tasks:
        run_task(task_id, max_steps)