# 5022CMD Advanced Algorithms

Three Python programs for pharmacy inventory, course prerequisites and a Fibonacci threading experiment.

## Requirements

Python 3.10 or newer. All programs use the Python standard library. Tested with Python 3.12.14 on Windows 11.

## Run the programs

Open a terminal in the repository folder:

```powershell
python q1_hashing/inventory_system.py
python q2_graph/main.py
python q3_concurrency/experiment.py
```

Run the Q1 search benchmark:

```powershell
python q1_hashing/benchmark.py
```

The full Q3 experiment takes several minutes. Smaller checks are available:

```powershell
python q3_concurrency/experiment.py --quick
python q1_hashing/benchmark.py --quick
```

Use the full commands when collecting report measurements.

## Programs

### Q1 Pharmacy inventory

The custom hash table uses open addressing with linear probing. The menu supports product insertion, search, editing, deletion and slot display. Tombstones preserve searches after deletion, and the table resizes when required. A Python list stores the same Product objects for comparison with sequential search.

The benchmark compares successful, missing, first record and last record searches using datasets of 10, 100, 1,000, 10,000 and 100,000 products. Both structures receive identical data and queries.

### Q2 Course prerequisites

A generic directed graph stores incoming and outgoing neighbours. Course objects are the vertices, and an edge points from a prerequisite to the course that requires it.

The menu lists courses, displays full details, shows prerequisites and dependent courses, adds courses, displays core or elective profiles, and adds or removes prerequisites. The system starts with nine courses and accepts a maximum of ten. Validation rejects duplicate codes, duplicate prerequisites, links from a course to itself and prerequisite cycles.

### Q3 Fibonacci experiment

The program calculates Fibonacci values for 35, 38 and 40 using plain recursion. It compares three threads with sequential execution over ten rounds per method. Threaded elapsed time is the latest worker finish minus the earliest worker start.

Output includes the calculated values, round times, totals and means in nanoseconds. An iterative calculation checks the answers outside the timed sections, and the execution order alternates between rounds.

## Main files

- Q1: `hash_table.py`, `product.py`, `sample_data.py`, `inventory_system.py`, `benchmark.py`.
- Q2: `graph.py`, `course.py`, `course_system.py`, `sample_data.py`, `main.py`.
- Q3: `fibonacci.py`, `experiment.py`.

The Q1 and Q2 `sample_data.py` files contain the predefined records loaded by the programs.

## Data and measurements

Q1 and Q2 store changes in memory for the current session. Restarting either program reloads the predefined records.

Full Q1 benchmark runs save a CSV and environment JSON in `q1_hashing/results/`. Full Q3 runs save the same types of files in `q3_concurrency/results/`. Quick runs use separate filenames. A later run replaces the files with the same names, so preserve the run used for the report and keep its screenshots, calculations and environment details together.
