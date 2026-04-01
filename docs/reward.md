# Reward

## Formula

```
reward = -(total_wait) / 10.0
```

Computed after every `step()` call, once cars have arrived and one car has been cleared.

---

## Why Negative?

Reinforcement learning agents are trained to **maximize** reward. By making reward negative and proportional to waiting cars, maximizing reward is equivalent to minimizing queue length — which is exactly the goal.

| Situation | total_wait | reward |
|-----------|-----------|--------|
| All lanes empty | 0 | 0.0 ← best possible |
| 4 cars waiting | 4 | -0.4 |
| 10 cars waiting | 10 | -1.0 |
| 20 cars waiting | 20 | -2.0 |
| 40 cars waiting | 40 | -4.0 |

---

## Why Divide by 10?

Pure scaling — keeps reward values in a small range (roughly `-0.0` to `-5.0` per step) which helps the Q-learning agent learn stable Q-values. Without scaling, large raw wait counts would produce large Q-values that are harder to converge.

---

## Total Reward Over an Episode

Total reward accumulates across all steps:

```
total_reward = sum(reward_t for t in 1..N)
```

For 100 steps:
- **Perfect agent** (0 cars always): `0.0`
- **LLM agent** (avg ~1.2 cars): `~-12.0`
- **Random agent** (avg ~37.9 cars): `~-379.0`

A less negative total reward = better performance.

---

## What Reward Does NOT Capture

- **Fairness** — a lane starved for 50 steps then cleared is treated the same as balanced service
- **Lane overflow** — no extra penalty for a single lane hitting 20+ cars vs spread across lanes
- **Throughput** — reward only penalizes waiting, not how many cars were successfully cleared

These gaps are why task3_hard (per-lane cap) exists as a separate grading criterion — the reward alone doesn't enforce lane balance.
