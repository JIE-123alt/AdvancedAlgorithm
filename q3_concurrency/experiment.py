"""experiment.py - Question 3: three Fibonacci tasks run in three threads, then the same
three tasks run one after another, for ten rounds each.

Run:  python experiment.py            full run (used for the report)
      python experiment.py --quick    smaller inputs, only to check that the script works

T of one round = the latest end time minus the earliest start time, in nanoseconds.
"""

import csv
import json
import os
import platform
import statistics
import sys
import threading
from pathlib import Path
from time import get_clock_info, perf_counter_ns

from fibonacci import fibonacci, fibonacci_iterative, recursive_call_count

TARGETS = (35, 38, 40)          # the three Fibonacci numbers asked for in the brief
QUICK_TARGETS = (20, 22, 24)    # tiny inputs for --quick
ROUNDS = 10
RESULTS_DIR = Path(__file__).resolve().parent / "results"


class RunResult:
    """Outcome of one round: the three Fibonacci values and the time T taken."""

    def __init__(self, values, total_ns):
        self.values = values
        self.total_ns = total_ns


def run_with_threads(targets):
    """One thread per target. Each thread writes only to its own position in the
    lists, so the threads never write to the same place; results are read after join()."""
    count = len(targets)
    values = [0] * count
    starts = [0] * count
    ends = [0] * count
    errors = [None] * count

    def worker(position, n):
        starts[position] = perf_counter_ns()
        try:
            values[position] = fibonacci(n)
        except Exception as error:
            errors[position] = error
        finally:
            ends[position] = perf_counter_ns()

    threads = []
    for position, n in enumerate(targets):
        threads.append(threading.Thread(target=worker, args=(position, n)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()                       # wait until all three have finished

    for error in errors:
        if error is not None:
            raise RuntimeError("Fibonacci worker failed") from error
    return RunResult(values, max(ends) - min(starts))   # latest end - earliest start


def run_sequentially(targets):
    """The same work in the main thread, one task after another."""
    start = perf_counter_ns()
    values = [fibonacci(n) for n in targets]
    return RunResult(values, perf_counter_ns() - start)


def environment():
    """Facts about the computer and Python version, saved with the results."""
    check_gil = getattr(sys, "_is_gil_enabled", None)       # only exists in Python 3.13+
    gil = check_gil() if check_gil else platform.python_implementation() == "CPython"
    return {"python": sys.version, "implementation": platform.python_implementation(),
            "gil_enabled": gil, "platform": platform.platform(),
            "processor": platform.processor(), "logical_cpus": os.cpu_count(),
            "clock_resolution_seconds": get_clock_info("perf_counter").resolution}


def print_summary(label, runs, targets):
    """Print every round, the total and the average T. Returns the average."""
    print(f"\n=== {label} ===")
    for number, run in enumerate(runs, 1):
        values = ", ".join(f"Fib({n})={v:,}" for n, v in zip(targets, run.values))
        print(f"Round {number:2}: {values} | T = {run.total_ns:>16,} ns")
    total = sum(run.total_ns for run in runs)
    average = statistics.mean(run.total_ns for run in runs)
    print(f"Total across {len(runs)} rounds: {total:,} ns")
    print(f"Average T: {average:,.1f} ns")
    return average


def save_results(threaded, sequential, metadata, tag):
    """Write the round times to a CSV file and the environment to a JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / f"q3_{tag}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["round", "with_threads_ns", "sequential_ns"])
        for number, (a, b) in enumerate(zip(threaded, sequential), 1):
            writer.writerow([number, a.total_ns, b.total_ns])
    json_path = RESULTS_DIR / f"q3_{tag}_environment.json"
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return csv_path


def run_experiment(targets, rounds):
    """Run both versions `rounds` times; returns (threaded results, sequential results).

    The order alternates from round to round, so neither version always runs first
    and benefits from a warm processor cache.
    """
    expected = [fibonacci_iterative(n) for n in targets]
    threaded, sequential = [], []
    for i in range(rounds):
        order = ((run_with_threads, threaded), (run_sequentially, sequential))
        if i % 2:
            order = order[::-1]
        for runner, results in order:
            run = runner(targets)
            if run.values != expected:                  # never time a wrong answer
                raise RuntimeError(f"Incorrect Fibonacci values: {run.values}")
            results.append(run)
            print(f"Round {i + 1:2} {runner.__name__}: T = {run.total_ns:,} ns", flush=True)
    return threaded, sequential


def main():
    quick = "--quick" in sys.argv
    targets = QUICK_TARGETS if quick else TARGETS
    metadata = environment()
    metadata.update(targets=targets, rounds=ROUNDS, quick=quick,
                    order="threaded first on odd rounds; sequential first on even rounds")
    print(json.dumps(metadata, indent=2))
    if quick:
        print("SMOKE CHECK ONLY: smaller inputs, not the required experiment.")

    print("Expected: " + ", ".join(f"F({n})={fibonacci_iterative(n):,}" for n in targets))
    calls = [recursive_call_count(n) for n in targets]      # work per task
    print("Recursive calls: " + ", ".join(
        f"Fib({n})={c:,} ({c / sum(calls):.1%})" for n, c in zip(targets, calls)))

    threaded, sequential = run_experiment(targets, ROUNDS)
    mean_t = print_summary("With multithreading", threaded, targets)
    mean_s = print_summary("Without multithreading", sequential, targets)
    print(f"\nSpeed-up = sequential mean / threaded mean = {mean_s / mean_t:.3f}x")
    print(f"Threaded mean change relative to sequential: {(mean_t / mean_s - 1) * 100:+.2f}%")
    print("Positive change means threads took longer. Small differences may be timing noise.")

    csv_path = save_results(threaded, sequential, metadata, "quick" if quick else "full")
    print(f"Saved {RESULTS_DIR.name}/{csv_path.name}")      # relative: no personal folder path


if __name__ == "__main__":
    main()
