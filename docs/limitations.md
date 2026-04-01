# Limitations & Known Issues

A honest look at the loopholes, vulnerabilities, and design gaps in the current codebase.

---

## 1. `/grader` Never Evaluates Your Agent

**File:** `traffic_env/server/app.py`

The `/grader/{task_id}` and `/baseline` endpoints always run an internal random agent — they have no way to accept or invoke your LLM or RL agent. Calling `/grader/task1_easy` after running `inference.py` does not grade your agent's performance.

**Impact:** You cannot use the built-in grader to benchmark your own agent without modifying the server code.

---

## 2. No Input Validation on `/step`

**File:** `traffic_env/server/app.py`, `traffic_env/server/environment.py`

The `lane` field accepts any integer. Passing `lane=99` or `lane=-1` will not raise an error — the environment will simply skip clearing any car (since `self._lanes[99]` would throw an `IndexError`).

**Impact:** Malformed actions can crash the server silently or produce unexpected behavior.

**Fix:** Add a bounds check in `environment.py`:
```python
if not (0 <= green < NUM_LANES):
    raise ValueError(f"Invalid lane: {green}")
```

---

## 3. Server State is Shared Across All Requests

**File:** `traffic_env/server/environment.py`, `traffic_env/server/app.py`

The `TrafficEnvironment` instance is a singleton. If two clients call `/step` concurrently, they will corrupt the same episode state — lane counts will be wrong and rewards will be meaningless.

**Impact:** Not safe for concurrent use. Running multiple inference scripts against the same server simultaneously will produce garbage results.

---

## 4. No Episode Isolation in `/grader`

**File:** `traffic_env/server/app.py`

The `/grader` endpoint creates its own local `TrafficEnvironment` instance, but the main app environment (used by `/reset` and `/step`) is separate. If you call `/grader` while an episode is in progress via `/step`, the grader runs fine but the active episode state is untouched — this is actually fine, but it means grader results are completely disconnected from any ongoing session.

---

## 5. LLM Fallback is Silent

**File:** `inference.py`

When the LLM returns an unparseable response, the agent silently falls back to `argmax(lanes)`. There is no logging or counter tracking how often this happens.

**Impact:** You have no visibility into how often the LLM is actually making decisions vs the fallback heuristic taking over. A broken API key or rate-limited model would silently degrade to argmax without any warning.

---

## 6. No API Key Validation at Startup

**File:** `inference.py`

`HF_TOKEN` defaults to an empty string `""`. If the environment variable is not set, the OpenAI client is initialized with an empty key and will only fail at the first LLM call — mid-episode.

**Impact:** The script starts successfully, runs the reset, then crashes on the first `ask_llm()` call, wasting the episode setup.

---

## 7. Q-Table is Never Saved

**File:** `train.py`, `agent.py`

After 1000 episodes of training, the Q-table exists only in memory. When `train.py` exits, all learned values are lost. There is no `save()` or `load()` method on `QLearningAgent`.

**Impact:** You cannot reuse a trained agent for inference or evaluation without retraining from scratch every time.

---

## 8. `task1_easy` Grading Slices Incorrectly

**File:** `traffic_env/server/app.py`

In the `/grader` endpoint, `task1_easy` is graded with `wait_history[:50]` even though the loop already runs for exactly `task.max_steps = 50` steps. This is harmless now, but if `max_steps` were ever changed to something other than 50, the slice would silently truncate or use wrong data.

---

## 9. No Rate Limiting or Timeout on LLM Calls

**File:** `inference.py`

`client.chat.completions.create()` has no timeout set. A slow or unresponsive API will hang the entire inference loop indefinitely with no way to recover.

---

## 10. Reward Does Not Penalize Lane Starvation

**File:** `traffic_env/server/environment.py`

The reward is purely `-(total_wait) / 10.0`. An agent could theoretically ignore one lane entirely (letting it grow to 50+ cars) while keeping the other three empty, and still achieve a decent reward. The reward function does not enforce fairness across lanes.

**Impact:** A reward-maximizing agent is not guaranteed to pass `task3_hard` (per-lane cap), since the reward gives no signal about individual lane overflow.
