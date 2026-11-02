"""inventory_system.py - command-line Pharmacy Inventory System (Question 1).

Layers
------
HashTable (hash_table.py)  general data structure, knows nothing about pharmacies
Product   (product.py)     entity stored in the table
InventoryService           business logic: keeps the hash table AND a plain
                           one-dimensional array (a Python list) holding the same
                           products, so that the two can be compared
menu actions + main()      the command-line user interface
"""

import math
import time
from datetime import date

from hash_table import STATE_DELETED, STATE_EMPTY, DuplicateKeyError, HashTable
from product import DEFAULT_CATEGORY, Product
from sample_data import build_sample_products

INITIAL_SIZE = 31          # table size chosen for the ~20 pre-defined records
TIMING_REPEATS = 1000      # one search takes ~1 microsecond, so average many repeats
NS_PER_SECOND = 1_000_000_000


# --------------------------------------------------------------------------- data access
def linear_search(products, product_id):
    """Sequential search of a one-dimensional array. Returns the index or -1. O(n)."""
    for index, product in enumerate(products):
        if product.product_id == product_id:
            return index
    return -1


class SearchResult:
    """Outcome of one search made in both data structures."""

    def __init__(self, product, hash_seconds, array_seconds, hash_probes, array_comparisons):
        self.product = product
        self.hash_seconds = hash_seconds
        self.array_seconds = array_seconds
        self.hash_probes = hash_probes
        self.array_comparisons = array_comparisons


class InventoryService:
    """Stores products in a hash table (fast lookup) and in an array (for comparison)."""

    def __init__(self, size=INITIAL_SIZE):
        self.table = HashTable(size)
        self.array = []

    def __len__(self):
        return len(self.array)

    def add_product(self, product):
        """Insert into both structures and return the hash-table slot used.

        Raises DuplicateKeyError if the product ID already exists.
        """
        slot = self.table.insert(product.product_id, product)   # fails first on duplicates
        self.array.append(product)
        return slot

    def search(self, product_id):
        """Search both structures, timing each one with a nanosecond clock."""
        clock = time.perf_counter_ns

        start = clock()
        for _ in range(TIMING_REPEATS):
            found = self.table.search(product_id)
        hash_seconds = (clock() - start) / TIMING_REPEATS / NS_PER_SECOND
        hash_probes = self.table.last_probes

        start = clock()
        for _ in range(TIMING_REPEATS):
            index = linear_search(self.array, product_id)
        array_seconds = (clock() - start) / TIMING_REPEATS / NS_PER_SECOND
        comparisons = len(self.array) if index < 0 else index + 1

        return SearchResult(found, hash_seconds, array_seconds, hash_probes, comparisons)

    def edit_product(self, product_id, name=None, category=None, price=None,
                     stock_quantity=None, expiry_date=None):
        """Change selected fields; None means keep the existing value.

        product_id selects the existing record; no replacement ID is accepted.
        A new Product validates the edited values, and both structures store
        the same replacement object.
        """
        old = self.table.search(product_id)
        if old is None:
            raise KeyError(product_id)
        new = Product(
            product_id,
            old.name if name is None else name,
            old.category if category is None else category,
            old.price if price is None else price,
            old.stock_quantity if stock_quantity is None else stock_quantity,
            old.expiry_date if expiry_date is None else expiry_date,
            old.requires_prescription)
        self.table.update(product_id, new)
        self.array[linear_search(self.array, product_id)] = new
        return new

    def delete_product(self, product_id):
        """Remove a product from both structures. Returns False if it does not exist."""
        if not self.table.delete(product_id):
            return False
        del self.array[linear_search(self.array, product_id)]
        return True


# --------------------------------------------------------------------------- input helpers
def prompt_text(label, allow_blank=False):
    while True:
        value = input(label).strip()
        if value or allow_blank:
            return value
        print("  Input cannot be empty.")


def prompt_int(label, minimum=0, allow_blank=False):
    while True:
        raw = input(label).strip()
        if allow_blank and not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if value < minimum:
            print(f"  Value must be {minimum} or more.")
            continue
        return value


def prompt_price(label, allow_blank=False):
    while True:
        raw = input(label).strip()
        if allow_blank and not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            print("  Please enter a number such as 5.90.")
            continue
        if not math.isfinite(value) or value < 0:
            print("  Price must be a finite number, 0 or more.")
            continue
        return value


def prompt_date(label, allow_blank=False):
    while True:
        raw = input(label).strip()
        if allow_blank and not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            print("  Please use the format YYYY-MM-DD (e.g. 2027-08-31).")


def prompt_yes_no(label, default=False):
    raw = input(label).strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


# --------------------------------------------------------------------------- menu actions
def action_insert(service):
    product_id = prompt_int("Enter Product ID: ", minimum=1)
    if product_id in service.table:
        print(f"A product with ID {product_id} already exists. Use Edit to change it.")
        return
    name = prompt_text("Enter Product Name: ")
    category = prompt_text(f"Enter Category (blank = {DEFAULT_CATEGORY}): ", allow_blank=True)
    price = prompt_price("Enter Price: ")
    stock = prompt_int("Enter Stock Quantity: ", minimum=0)
    expiry = prompt_date("Enter Expiry Date (YYYY-MM-DD): ")
    needs_rx = prompt_yes_no("Requires prescription? (y/N): ")

    old_size = service.table.size
    try:
        product = Product(product_id, name, category, price, stock, expiry, needs_rx)
        slot = service.add_product(product)
    except (ValueError, DuplicateKeyError) as error:
        print(f"Could not insert product: {error}")
        return
    print(f"Product inserted successfully into slot [{slot}]")
    if service.table.size != old_size:
        print(f"(Hash table was full enough to trigger a resize: "
              f"{old_size} -> {service.table.size} slots, all keys re-hashed)")


def action_search(service):
    product_id = prompt_int("Enter Product ID to search: ", minimum=1)
    result = service.search(product_id)
    if result.product is None:
        print("Product Not Found.")
    else:
        print("Product Found!")
        print(result.product)
        print(result.product.extra_details())
    # Seconds are shown to nine decimal places; this is display precision, not clock accuracy.
    print(f"Search completed in {result.hash_seconds:.9f} seconds "
          f"(Hash Table - {result.hash_probes} slot(s) examined)")
    print(f"Search completed in {result.array_seconds:.9f} seconds "
          f"(Array - {result.array_comparisons} comparison(s))")
    print(f"(each time is the average of {TIMING_REPEATS} repeated searches)")


def action_edit(service):
    product_id = prompt_int("Enter Product ID to edit: ", minimum=1)
    current = service.table.search(product_id)
    if current is None:
        print("Product Not Found.")
        return
    print("Current record:")
    print(current)
    print(current.extra_details())
    print("Press Enter to keep the current value.")

    name = prompt_text("New name: ", allow_blank=True) or None
    category = prompt_text("New category: ", allow_blank=True) or None
    price = prompt_price("New price: ", allow_blank=True)
    stock = prompt_int("New stock quantity: ", minimum=0, allow_blank=True)
    expiry = prompt_date("New expiry date (YYYY-MM-DD): ", allow_blank=True)

    if all(value is None for value in (name, category, price, stock, expiry)):
        print("Nothing changed.")
        return
    try:
        updated = service.edit_product(product_id, name, category, price, stock, expiry)
    except ValueError as error:
        print(f"Could not update product: {error}")
        return
    print("Product updated:")
    print(updated)


def action_delete(service):
    product_id = prompt_int("Enter Product ID to delete: ", minimum=1)
    product = service.table.search(product_id)
    if product is None:
        print("Product Not Found.")
        return
    print(product)
    if not prompt_yes_no("Delete this product? (y/N): "):
        print("Delete cancelled.")
        return
    service.delete_product(product_id)
    print("Product deleted. (Its slot now holds a tombstone so other keys stay reachable.)")


def action_display(service):
    table = service.table
    print(f"Hash table: {len(table)} products in {table.size} slots "
          f"(load factor {table.load_factor():.2f}, resized {table.resize_count} time(s))")
    for index, state, key, product in table.slot_view():
        if state == STATE_EMPTY:
            print(f"[{index:>3}] ---")
        elif state == STATE_DELETED:
            print(f"[{index:>3}] <deleted>")
        else:
            home = table.hash_function(key)
            note = "" if home == index else f"   <- collision, home slot was [{home}]"
            print(f"[{index:>3}] {key} | {product.name}{note}")


def action_benchmark(service):
    # Imported here, not at the top: benchmark.py imports this file, so a top-level
    # import would be circular.
    from benchmark import DEFAULT_SIZES, print_search_table, run_search_benchmark
    print("Running search benchmark (this takes a few seconds)...")
    print_search_table(run_search_benchmark(DEFAULT_SIZES))


# --------------------------------------------------------------------------- main
# One line per menu option: (key, text shown, function that runs it).
# To add an option, add a line here; the menu, the Exit number and the input check follow.
MENU = [
    ("1", "Insert Product", action_insert),
    ("2", "Search Product", action_search),
    ("3", "Edit Product", action_edit),
    ("4", "Delete Product", action_delete),
    ("5", "Display Hash Table Slots", action_display),
    ("6", "Run Performance Comparison (Hash Table vs Array)", action_benchmark),
]


def main():
    service = InventoryService()
    for product in build_sample_products():
        service.add_product(product)
    table = service.table
    print(f"Loaded {len(service)} pre-defined products into a hash table of "
          f"{table.size} slots (load factor {table.load_factor():.2f}).")

    actions = {key: action for key, _, action in MENU}
    exit_key = str(len(MENU) + 1)
    try:
        while True:
            print("\n==== Pharmacy Inventory System ====")
            for key, title, _ in MENU:
                print(f"{key}. {title}")
            print(f"{exit_key}. Exit")
            choice = input("Enter choice: ").strip()
            if choice == exit_key:
                print("Exiting Inventory System......")
                break
            action = actions.get(choice)
            if action is None:
                print(f"Invalid choice, please enter 1-{exit_key}.")
                continue
            action(service)
    except (EOFError, KeyboardInterrupt):           # Ctrl+D / Ctrl+Z / Ctrl+C
        print("\nInput closed. Exiting Inventory System......")


if __name__ == "__main__":
    main()
