"""Unit tests for the generic HashTable.   Run:  python -m unittest -v"""

import unittest
from datetime import date

from hash_table import (STATE_DELETED, STATE_EMPTY, DuplicateKeyError, HashTable,
                        HashTableFullError)
from product import Product


class HashTableTests(unittest.TestCase):

    def test_insert_returns_home_slot_when_free(self):
        table = HashTable(11)
        self.assertEqual(table.insert(25, "a"), 25 % 11)

    def test_collision_uses_next_free_slot(self):
        table = HashTable(11)
        first = table.insert(3, "a")
        second = table.insert(14, "b")        # 14 % 11 == 3 -> collision
        third = table.insert(25, "c")         # 25 % 11 == 3 -> collision
        self.assertEqual((first, second, third), (3, 4, 5))
        self.assertEqual(table.search(25), "c")
        self.assertEqual(table.last_probes, 3)

    def test_probing_wraps_around_to_slot_zero(self):
        table = HashTable(5, auto_resize=False)
        self.assertEqual(table.insert(4, "a"), 4)
        self.assertEqual(table.insert(9, "b"), 0)       # 9 % 5 == 4 -> wraps to 0
        self.assertEqual(table.search(9), "b")

    def test_duplicate_key_rejected(self):
        table = HashTable(11)
        table.insert(7, "x")
        with self.assertRaises(DuplicateKeyError):
            table.insert(7, "y")
        self.assertEqual(table.search(7), "x")
        self.assertEqual(len(table), 1)

    def test_search_missing_returns_default(self):
        table = HashTable(11)
        self.assertIsNone(table.search(99))
        self.assertEqual(table.search(99, "n/a"), "n/a")

    def test_delete_keeps_probe_chain_intact(self):
        table = HashTable(11)
        table.insert(3, "a")
        table.insert(14, "b")      # slot 4
        table.insert(25, "c")      # slot 5
        self.assertTrue(table.delete(14))          # tombstone in slot 4
        self.assertEqual(table.search(25), "c")    # still reachable past the tombstone
        self.assertNotIn(14, table)
        states = {index: state for index, state, _, _ in table.slot_view()}
        self.assertEqual(states[4], STATE_DELETED)

    def test_tombstone_is_reused_by_insert(self):
        table = HashTable(11)
        table.insert(3, "a")
        table.insert(14, "b")
        table.delete(3)                            # tombstone in the home slot
        self.assertEqual(table.insert(25, "c"), 3)  # new key recycles the tombstone
        self.assertEqual(table.search(14), "b")

    def test_delete_missing_returns_false(self):
        self.assertFalse(HashTable(11).delete(5))

    def test_update(self):
        table = HashTable(11)
        table.insert(5, "old")
        self.assertTrue(table.update(5, "new"))
        self.assertEqual(table.search(5), "new")
        self.assertFalse(table.update(6, "x"))

    def test_auto_resize_keeps_all_keys(self):
        table = HashTable(5, max_load_factor=0.7)
        for key in range(100):
            table.insert(key * 7, key)
        self.assertGreater(table.size, 5)
        self.assertGreater(table.resize_count, 0)
        self.assertLessEqual(table.load_factor(), 0.7)
        for key in range(100):
            self.assertEqual(table.search(key * 7), key)
        self.assertEqual(len(table), 100)

    def test_full_table_without_resize_raises(self):
        table = HashTable(3, auto_resize=False)
        for key in (1, 2, 3):
            table.insert(key, key)
        with self.assertRaises(HashTableFullError):
            table.insert(4, 4)
        self.assertEqual(table.search(4), None)    # search terminates on a full table

    def test_string_keys_are_deterministic(self):
        a, b = HashTable(31), HashTable(31)
        expected = sum(ord(char) for char in "paracetamol") % 31
        self.assertEqual(a.hash_function("paracetamol"), expected)
        self.assertEqual(a.hash_function("paracetamol"), b.hash_function("paracetamol"))
        a.insert("paracetamol", 1)
        self.assertEqual(a.search("paracetamol"), 1)

    def test_negative_integer_key(self):
        table = HashTable(11)
        slot = table.insert(-5, "neg")
        self.assertTrue(0 <= slot < 11)
        self.assertEqual(table.search(-5), "neg")

    def test_empty_slots_reported(self):
        table = HashTable(4)
        table.insert(1, "a")
        states = [state for _, state, _, _ in table.slot_view()]
        self.assertEqual(states.count(STATE_EMPTY), 3)

    def test_items_lists_live_entries_only(self):
        table = HashTable(11)
        for key in (1, 2, 3):
            table.insert(key, key * 10)
        table.delete(2)
        self.assertEqual(sorted(table.items()), [(1, 10), (3, 30)])


class ProductTests(unittest.TestCase):

    def make(self, **overrides):
        values = dict(product_id=1042, name="Paracetamol 500mg", category="Pain Relief",
                      price="5.9", stock_quantity=120, expiry_date=date(2027, 8, 31))
        values.update(overrides)
        return Product(**values)

    def test_price_rounded_and_displayed_to_two_decimals(self):
        self.assertIsInstance(self.make().price, float)
        self.assertEqual(self.make(price="5.999").price, 6.0)
        self.assertEqual(f"{self.make().price:.2f}", "5.90")

    def test_str_matches_expected_format(self):
        self.assertEqual(str(self.make()),
                         "ID: 1042 | Name: Paracetamol 500mg | Price: RM5.90 | Stock: 120")

    def test_invalid_values_rejected(self):
        for bad in (dict(product_id=0), dict(product_id=-3), dict(product_id=True),
                    dict(name="   "), dict(price="abc"), dict(price="-1"),
                    dict(stock_quantity=-1), dict(stock_quantity=1.5),
                    dict(expiry_date="2027-01-01")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.make(**bad)


if __name__ == "__main__":
    unittest.main()
