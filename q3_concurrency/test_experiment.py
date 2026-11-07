"""Small inputs check correctness and worker failures without a long experiment."""
import unittest
from unittest.mock import patch
from experiment import run_sequentially, run_with_threads
from fibonacci import fibonacci, fibonacci_iterative, primitive_operations, recursive_call_count


class ExperimentTests(unittest.TestCase):
    def test_recursive_values_match_independent_reference(self):
        for n in range(16):
            self.assertEqual(fibonacci(n), fibonacci_iterative(n))
        self.assertEqual([fibonacci_iterative(n) for n in (35, 38, 40)],
                         [9227465, 39088169, 102334155])

    def test_three_threaded_results_match_sequential(self):
        targets = (10, 12, 14)
        threaded = run_with_threads(targets)
        sequential = run_sequentially(targets)
        self.assertEqual(threaded.values, sequential.values)
        self.assertGreater(threaded.total_ns, 0)

    def test_failure_in_worker_is_reported_to_caller(self):
        with patch("experiment.fibonacci", side_effect=ValueError("test failure")):
            with self.assertRaises(RuntimeError):
                run_with_threads((2, 3, 4))

    def test_three_workers_use_earliest_start_and_latest_finish(self):
        class ImmediateThread:
            def __init__(self, target, args):
                self.target, self.args = target, args

            def start(self):
                self.target(*self.args)

            def join(self):
                pass

        # Deliberately use nonmonotonic supplied timestamps to ensure the formula
        # chooses extrema, rather than assuming target order is finish order.
        with patch("experiment.threading.Thread", side_effect=ImmediateThread) as make_thread:
            with patch("experiment.perf_counter_ns", side_effect=[100, 160, 110, 220, 120, 190]):
                run = run_with_threads((2, 3, 4))
        self.assertEqual(make_thread.call_count, 3)
        self.assertEqual(run.total_ns, 120)

    def test_recursive_call_formula(self):
        self.assertEqual(recursive_call_count(0), 1)
        self.assertEqual(recursive_call_count(5), 15)

    def test_primitive_operation_formula(self):
        def counted(n):
            """Same recursion as fibonacci(), but returns (value, operations used)."""
            if n <= 1:
                return n, 2                         # comparison + return
            a, ops_a = counted(n - 1)
            b, ops_b = counted(n - 2)
            return a + b, ops_a + ops_b + 5         # comparison, 2 subtractions, addition, return
        for n in range(16):
            self.assertEqual(counted(n)[1], primitive_operations(n))
        self.assertEqual(primitive_operations(5), 51)


if __name__ == "__main__":
    unittest.main()
