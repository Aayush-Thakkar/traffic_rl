# Design Decisions

The reasoning behind key choices made in this project.

---

## 1. Why a FastAPI Server Instead of a Gym Environment?

Most RL projects use [OpenAI Gym](https://gymnasium.farama.org/) directly as a Python object. Here, the environment is wrapped in a FastAPI server.

**Reason:** This follows the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) pattern, which treats environments as HTTP services. This makes the environment language-agnostic and allows any client — Python, JavaScript, curl — to interact with it. It also makes it trivial to swap agents (LLM vs RL vs random) without touching the environment code.

**Tradeoff:** HTTP overhead makes training slower. That's why `train.py` bypasses the server entirely and imports `TrafficEnvironment` directly.

---

## 2. Why Tabular Q-Learning Instead of Deep RL?

The state space is `4^4 = 256` states (4 lanes × 4 buckets each). This is tiny — a dictionary Q-table is sufficient and trains in seconds.

**Reason:** Deep RL (DQN, PPO) would be overkill here. Tabular Q-learning is transparent, fast, and easy to debug. You can print the entire Q-table and inspect what the agent learned.

**Tradeoff:** The bucketing loses information. Two states with `[3,3,3,3]` and `[1,1,1,1]` both map to the same bucket tuple `(1,1,1,1)` and get the same Q-values, even though the first is more urgent.

---

## 3. Why Bucket Lane Counts Instead of Using Raw Numbers?

Raw lane counts could range from 0 to 50+, giving an enormous state space that would rarely be visited during training.

**Reason:** Bucketing into 4 levels (empty/light/medium/heavy) compresses the state space to 256 states, ensuring every state is visited many times during 1000 training episodes. This leads to better-converged Q-values.

**Tradeoff:** Precision is lost. The agent treats 1 car and 3 cars identically (both "light"), which may cause suboptimal decisions at the boundary.

---

## 4. Why Negative Reward?

Standard RL convention is to maximize reward. The goal here is to minimize waiting cars.

**Reason:** By setting `reward = -(total_wait) / 10.0`, minimizing wait becomes maximizing reward — no special handling needed. The `/10.0` scaling keeps Q-values in a numerically stable range.

**Tradeoff:** Reward is always ≤ 0, which can be unintuitive when reading logs. A reward of `-0.5` is good; `-4.0` is bad.

---

## 5. Why Does the LLM Agent Use a Simple Prompt?

The prompt just lists lane counts and asks for a single digit. No chain-of-thought, no history, no system prompt.

**Reason:** Simplicity first. Even a minimal prompt achieves ~1.2 avg wait vs ~37.9 for random — a 30x improvement. The LLM's world knowledge about traffic is enough for near-optimal greedy decisions.

**Tradeoff:** The LLM has no memory of past steps. It cannot detect trends (e.g. a lane growing fast) or plan ahead. Adding history to the prompt would likely improve performance further.

---

## 6. Why `argmax(lanes)` as the LLM Fallback?

When the LLM returns an unparseable response, the agent picks the lane with the most cars.

**Reason:** `argmax` is the greedy-optimal strategy for this environment — always clear the busiest lane. It's a sensible default that performs well on its own.

**Tradeoff:** The fallback is silent. There's no logging when it triggers, so you can't tell how often the LLM is actually being used vs the fallback.

---

## 7. Why Three Tasks With Different Metrics?

A single reward metric doesn't capture all aspects of good traffic management.

**Reason:**
- `task1_easy` — tests absolute worst-case (never let it get catastrophic)
- `task2_medium` — tests average performance (consistent efficiency)
- `task3_hard` — tests fairness (no single lane neglected)

These three together give a more complete picture of agent quality than total reward alone.

---

## 8. Why 40% Car Arrival Probability?

**Reason:** At 40%, expected arrivals per step are `4 × 0.4 = 1.6 cars`, while the agent can only clear 1. This creates mild pressure — queues will grow if the agent is careless, but a smart agent can keep them near zero. Lower probability would make the task trivial; higher would make it impossible to keep queues at zero.
