import random

# --- CONFIGURATION ---
NUM_LANES = 4          # 4-way intersection: North, South, East, West
MAX_STEPS = 100        # One episode = 100 time steps
CAR_ARRIVAL_PROB = 0.4 # 40% chance a new car arrives at each lane each step

def run_simulation():
    # Each lane starts with 0 cars waiting
    lanes = [0] * NUM_LANES  # e.g. [0, 0, 0, 0]

    total_wait = 0           # We'll accumulate total cars waiting across all steps
    green_light = 0          # Start by giving green to lane 0

    for step in range(MAX_STEPS):

        # --- CAR ARRIVALS ---
        # Randomly add cars to each lane this step
        for i in range(NUM_LANES):
            if random.random() < CAR_ARRIVAL_PROB:
                lanes[i] += 1   # One new car joins lane i

        # --- MOVE CARS ---
        # The green lane clears one car per step (car passes through)
        if lanes[green_light] > 0:
            lanes[green_light] -= 1

        # --- DUMB CONTROLLER ---
        # Round-robin: just rotate green light every step
        green_light = (green_light + 1) % NUM_LANES

        # --- STATS ---
        wait_this_step = sum(lanes)   # Total cars waiting right now
        total_wait += wait_this_step

        print(f"Step {step+1:3d} | Lanes: {lanes} | Green: {green_light} | Wait: {wait_this_step}")

    print(f"\n✅ Episode done. Total wait: {total_wait}")
    return total_wait

# Entry point
if __name__ == "__main__":
    run_simulation()