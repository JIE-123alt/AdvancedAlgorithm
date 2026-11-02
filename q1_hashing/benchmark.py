"""benchmark.py - Q1: the same products and the same queries are searched in the
hash table and in a one-dimensional list, for several data sizes.

Run:  python benchmark.py            full run (used for the report)
      python benchmark.py --quick    smaller run, only to check that the script works
"""

import csv
import json
import platform
import random
import statistics
import sys
from datetime import date
from pathlib import Path
from time import get_clock_info, perf_counter_ns

from hash_table import HashTable
from inventory_system import linear_search
from product import DEFAULT_CATEGORY, Product

DEFAULT_SIZES = (10, 100, 1_000, 10_000, 100_000)   # number of products per round
RESULTS_DIR = Path(__file__).resolve().parent / "results"
SEED = 2026             # fixed seed: every run uses the same products and queries
BATCHES = 5             # timed batches per structure; the median is reported
QUERIES = 100           # searches per batch
START_SIZE = 11         # the table starts small and grows by itself
NS_PER_MICROSECOND = 1000
FIRST_ID = 10_000       # product IDs are drawn from FIRST_ID upwards
ID_SPREAD = 10          # ID range is ID_SPREAD x n wide, so IDs are sparse and never repeat

# Every generated product only needs a valid ID; the other fields are the same filler.
FILLER_CATEGORY = DEFAULT_CATEGORY
FILLER_PRICE = 5.90
FILLER_STOCK = 100
FILLER_EXPIRY = date(2028, 1, 1)


def time_batch(search, keys):
    """Average time of one search, in microseconds, over a batch of keys."""
    start = perf_counter_ns()
    for key in keys:
        search(key)
    return (perf_counter_ns() - start) / len(keys) / NS_PER_MICROSECOND


def compare_searches(hash_find, array_find, keys):
    """Time both structures on identical keys; returns (hash median, array median).

    One untimed warm-up pass first. The order of the two structures alternates from
    batch to batch so that neither one always runs first.
    """
    hash_samples, array_samples = [], []
    for key in keys:
        hash_find(key)
        array_find(key)
    for batch in range(BATCHES):
        order = ((hash_find, hash_samples), (array_find, array_samples))
        if batch % 2:
            order = order[::-1]
        for search, samples in order:
            samples.append(time_batch(search, keys))
    return statistics.median(hash_samples), statistics.median(array_samples)


def run_search_benchmark(sizes=DEFAULT_SIZES):
    """Return one result row (a dict) for each data size."""
    rng = random.Random(SEED)
    rows = []
    for n in sizes:
        ids = rng.sample(range(FIRST_ID, FIRST_ID + ID_SPREAD * n), n)
        array = [Product(pid, f"Medicine {pid}", FILLER_CATEGORY, FILLER_PRICE,
                         FILLER_STOCK, FILLER_EXPIRY) for pid in ids]
        table = HashTable(START_SIZE)
        for product in array:
            table.insert(product.product_id, product)

        def array_find(key):
            index = linear_search(array, key)
            return None if index < 0 else array[index]

        # Four kinds of query: random existing IDs, IDs that are not stored,
        # the first stored ID and the last stored ID (best and worst case for the list).
        cases = {"found": rng.choices(ids, k=QUERIES),
                 "missing": rng.sample(range(FIRST_ID + ID_SPREAD * n,
                                             FIRST_ID + 2 * ID_SPREAD * n), QUERIES),
                 "first": [ids[0]] * QUERIES,
                 "last": [ids[-1]] * QUERIES}

        row = {"n": n, "table_size": table.size, "load_factor": table.load_factor()}
        for label, keys in cases.items():
            for key in keys:                    # check correctness outside the timing
                if table.search(key) != array_find(key):
                    raise RuntimeError("Search results disagree")
            hash_us, array_us = compare_searches(table.search, array_find, keys)
            row[f"hash_{label}_us"] = hash_us
            row[f"array_{label}_us"] = array_us
        row["speedup_found"] = row["array_found_us"] / row["hash_found_us"]
        rows.append(row)
    return rows


def print_search_table(rows):
    print("\nMedian batch average per search (microseconds)")
    print(f"Seed={SEED}; {BATCHES} batches; {QUERIES} identical queries per case and structure")
    print(f"{'n':>8} {'load':>6} {'hash hit':>10} {'array hit':>10} {'hash miss':>10} "
          f"{'array miss':>11} {'array first':>12} {'array last':>11} {'ratio':>8}")
    for r in rows:
        print(f"{r['n']:8,} {r['load_factor']:6.3f} {r['hash_found_us']:10.3f} "
              f"{r['array_found_us']:10.3f} {r['hash_missing_us']:10.3f} "
              f"{r['array_missing_us']:11.3f} {r['array_first_us']:12.3f} "
              f"{r['array_last_us']:11.3f} {r['speedup_found']:7.2f}x")
    print("ratio = array hit time / hash hit time; CSV also includes hash first/last timings.")


def save_results(rows, sizes, tag):
    """Write the rows to a CSV file and the test environment to a JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / f"q1_{tag}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    environment = {"python": sys.version, "platform": platform.platform(), "seed": SEED,
                   "sizes": sizes, "batches": BATCHES, "queries_per_case": QUERIES,
                   "clock_resolution_seconds": get_clock_info("perf_counter").resolution}
    json_path = RESULTS_DIR / f"q1_{tag}_environment.json"
    json_path.write_text(json.dumps(environment, indent=2), encoding="utf-8")
    return csv_path


def main():
    quick = "--quick" in sys.argv
    sizes = DEFAULT_SIZES[:-1] if quick else DEFAULT_SIZES
    rows = run_search_benchmark(sizes)
    print_search_table(rows)
    csv_path = save_results(rows, sizes, "quick" if quick else "full")
    print(f"Saved {RESULTS_DIR.name}/{csv_path.name}")      # relative, no personal path


if __name__ == "__main__":
    main()
