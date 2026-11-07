"""fibonacci.py - the Fibonacci functions used in Question 3."""


def fibonacci(n):
    """nth Fibonacci number by plain recursion (F(0) = 0, F(1) = 1).

    Deliberately NOT optimised (no memoisation): its running time is exponential,
    which makes it a good CPU-bound workload for the threading experiment.
    Time complexity O(2^n) (tight bound Theta(phi^n)); space O(n) for the call stack.

    Counting primitive operations (comparison, subtraction, addition, return = 1 each):
        base case n <= 1 : 1 comparison + 1 return                           = 2
        other n          : 1 comparison + 2 subtractions + 1 addition + 1 return = 5,
                           plus the cost of the two recursive calls
    so T(0) = T(1) = 2 and T(n) = T(n-1) + T(n-2) + 5.
    Let U(n) = T(n) + 5. Then U(n) = U(n-1) + U(n-2) with U(0) = U(1) = 7, which is
    7 times the Fibonacci numbers: U(n) = 7*F(n+1), so T(n) = 7*F(n+1) - 5.
    Since F(n) is about phi^n / sqrt(5) with phi = 1.618, T(n) = Theta(phi^n),
    which is also O(2^n).
    """
    if n <= 1:                                   # base case
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)   # two recursive calls


def fibonacci_iterative(n):
    """Fast O(n) reference version, used only to check the recursive results."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def recursive_call_count(n):
    """Exact number of calls fibonacci(n) makes: C(n) = 2*F(n+1) - 1."""
    return 2 * fibonacci_iterative(n + 1) - 1


def primitive_operations(n):
    """Primitive operations of fibonacci(n) from the recurrence above: 7*F(n+1) - 5."""
    return 7 * fibonacci_iterative(n + 1) - 5
