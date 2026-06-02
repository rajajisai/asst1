#!/usr/bin/env python3

import subprocess
import re
import sys
import os
import matplotlib.pyplot as plt

def usage():
    print("Usage: python3 plot_thread_times.py -t <num_threads> [-v <view>]")
    sys.exit(1)

# Parse arguments
num_threads = None
view = None

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "-t" and i + 1 < len(args):
        num_threads = int(args[i + 1])
        i += 2
    elif args[i] == "-v" and i + 1 < len(args):
        view = int(args[i + 1])
        i += 2
    else:
        usage()

if num_threads is None:
    usage()

# Build command
cmd = ["./mandelbrot", "-t", str(num_threads)]
if view is not None:
    cmd += ["-v", str(view)]

# Run and capture output
result = subprocess.run(cmd, capture_output=True, text=True)
output = result.stdout + result.stderr

# Parse per-thread times: "Thread <id> finished in <time> seconds"
pattern = re.compile(r"Thread (\d+) finished in ([0-9.]+) seconds")
matches = pattern.findall(output)

if not matches:
    print("No per-thread timing data found. Make sure the binary prints:")
    print('  "Thread <id> finished in <time> seconds"')
    sys.exit(1)

# Keep minimum time per thread ID (binary runs 5 trials)
from collections import defaultdict
best = defaultdict(lambda: float("inf"))
for tid, t in matches:
    best[int(tid)] = min(best[int(tid)], float(t))
thread_data = sorted(best.items())
thread_ids = [str(d[0]) for d in thread_data]
times_ms = [d[1] * 1000 for d in thread_data]

# Plot
fig, ax = plt.subplots(figsize=(max(8, num_threads // 2 if num_threads else 8), 5))
bars = ax.bar(thread_ids, times_ms, color="steelblue", edgecolor="black")

ax.set_xlabel("Thread ID")
ax.set_ylabel("Time (ms)")
view_label = f"View {view}" if view else "View 1 (default)"
ax.set_title(f"Per-Thread Compute Time — {num_threads} Threads, {view_label}")
ax.axhline(y=sum(times_ms) / len(times_ms), color="red", linestyle="--", label="Average")
ax.legend()

for bar, val in zip(bars, times_ms):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}", ha="center", va="bottom", fontsize=7)

plt.tight_layout()
os.makedirs("graphs", exist_ok=True)
outfile = f"graphs/thread_times_t{num_threads}_v{view or 1}.png"
plt.savefig(outfile, dpi=150)
print(f"Graph saved to {outfile}")
