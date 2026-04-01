# Tasks

There are 3 tasks of increasing difficulty. Each task runs for a fixed number of steps and grades performance based on how well the agent managed traffic queues.

---

## task1_easy

**Goal:** Keep total waiting cars under 20 for every step across 50 steps.

**Steps:** 50

**Pass condition:** `total_wait < 20` on ALL 50 steps

**Scoring:**
- `1.0` if every step had wait < 20
- Otherwise: `% of steps where wait < 20`

**Example:**
```
wait_history = [1, 2, 0, 3, 1, ...]   → score: 1.0, passed: true
wait_history = [1, 2, 25, 3, 1, ...]  → score: 0.98, passed: false
```

**Why it's easy:** The threshold of 20 is very generous. Even a mediocre agent rarely lets all 4 lanes pile up to 5+ cars each simultaneously.

---

## task2_medium

**Goal:** Keep the **average** total wait under 5 cars per step across 100 steps.

**Steps:** 100

**Pass condition:** `mean(wait_history) < 5.0`

**Scoring:**
- `1.0` if average ≤ 5.0
- Partial: `max(0, 1.0 - (avg_wait - 5.0) / 20.0)`
- Score hits `0.0` when average wait reaches 25+

**Example:**
```
avg_wait = 1.2  → score: 1.0,  passed: true
avg_wait = 10.0 → score: 0.75, passed: false
avg_wait = 37.9 → score: 0.0,  passed: false  (random baseline)
```

**Why it's medium:** Averaging under 5 requires consistent smart decisions. A random agent averages ~37.9 — well above the target.

---

## task3_hard

**Goal:** Keep **every individual lane** under 10 cars at all times for 100 steps.

**Steps:** 100

**Pass condition:** `max(lanes) < 10` on ALL 100 steps

**Scoring:**
- `% of steps where all lanes had < 10 cars`
- `1.0` only if no lane ever hit 10+

**Example:**
```
all steps balanced  → score: 1.0,  passed: true
balanced 39 steps   → score: 0.39, passed: false  (random baseline)
```

**Why it's hard:** It only takes one neglected lane to fail. The agent must balance all 4 lanes simultaneously, not just minimize total wait.

---

## Comparison

| Task | Metric | Target | Random Baseline |
|------|--------|--------|-----------------|
| task1_easy | Per-step total wait | < 20 | ~48% pass rate |
| task2_medium | Average total wait | < 5.0 | ~37.9 avg wait |
| task3_hard | Per-lane max | < 10 always | ~39% balanced |

---

## How Grading Works

Grading is stateless — you collect history during your episode and pass it to the grader:

```python
# task1 and task2 — pass list of total_wait values
Task1Easy().grade(wait_history)    # wait_history = [int, int, ...]

# task3 — pass list of lane snapshots
Task3Hard().grade(lane_history)    # lane_history = [[int,int,int,int], ...]
```

The grader returns a `TaskResult` with `score`, `passed`, and `message`.
