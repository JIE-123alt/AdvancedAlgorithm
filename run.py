"""Run each independent question from the correct folder."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", choices=("1", "2", "3", "benchmark", "tests"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if args.question == "tests":
        for folder in ("q1_hashing", "q2_graph", "q3_concurrency"):
            subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=ROOT / folder,
                           check=True)
        return
    folder, script = {"1": ("q1_hashing", "inventory_system.py"),
                      "2": ("q2_graph", "main.py"),
                      "3": ("q3_concurrency", "experiment.py"),
                      "benchmark": ("q1_hashing", "benchmark.py")}[args.question]
    command = [sys.executable, "-u", script]
    if args.quick and args.question in ("3", "benchmark"):
        command.append("--quick")
    subprocess.run(command, cwd=ROOT / folder, check=True)


if __name__ == "__main__":
    main()
