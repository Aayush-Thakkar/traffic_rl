# Environment

## The Intersection

A single 4-way intersection with one lane per direction:

```
          NORTH (0)
             │
             │  ↓ cars arrive
             │
WEST (3) ────┼──── EAST (2)
             │
             │  ↑ cars arrive
             │
          SOUTH (1)
```

Each lane is independent — cars arrive and queue up separately. The agent controls a single traffic light that can give green to exactly one lane per step.

---

## Simulation Loop (per step)

1. **Car arrivals** — each of the 4 lanes independently gets +1 car with 40% probability
2. **Agent action** — agent picks one lane (0–3) to give the green light
3. **Car cleared** — if the chosen lane has ≥ 1 car, it removes 1 car
4. **Reward computed** — `-(total_wait) / 10.0`
5. **Done check** — episode ends after `MAX_STEPS = 100` steps

---

## Key Parameters

| Parameter | Value | Location |
|-----------|-------|----------|
| Number of lanes | 4 | `environment.py` |
| Car arrival probability | 0.4 (40%) per lane per step | `environment.py` |
| Max steps per episode | 100 | `environment.py` |
| Cars cleared per step | 1 (from chosen lane only) | `environment.py` |

---

## Expected Arrivals vs Clearance

On average each step:
- **Arrivals:** `4 lanes × 0.4 = 1.6 cars`
- **Clearance:** `1 car` (agent clears exactly one)

This means the system is **supply-constrained** — even a perfect agent cannot clear all arriving cars every step. The best strategy is to always clear the busiest lane to prevent any single lane from overflowing.

---

## State Representation

The raw observation is a list of 4 integers — one per lane:

```python
lanes = [3, 0, 5, 2]   # North=3, South=0, East=5, West=2
```

The Q-learning agent buckets these into 4 levels to keep the state space manageable:

| Cars | Bucket | Label |
|------|--------|-------|
| 0 | 0 | empty |
| 1–3 | 1 | light |
| 4–7 | 2 | medium |
| 8+ | 3 | heavy |

This gives `4^4 = 256` possible states.

---

## Episode Lifecycle

```
reset()  →  step() × N  →  done=True
```

- `reset()` sets all lanes to 0 and returns the initial observation
- Each `step()` advances time by one unit
- `done=True` is returned on the final step — the episode does not auto-reset
- You must call `reset()` again to start a new episode
