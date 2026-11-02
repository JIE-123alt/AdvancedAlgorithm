"""Regression checks for keeping both storage structures consistent."""

import unittest
from datetime import date

from inventory_system import InventoryService, linear_search
from product import Product


class InventoryTests(unittest.TestCase):

    def make_product(self, **changes):
        fields = dict(product_id=3, name="Example medicine", category="General",
                      price=5.90, stock_quantity=10, expiry_date=date(2028, 1, 1))
        fields.update(changes)
        return Product(**fields)
    
    def test_product_id_cannot_change_after_insertion(self):
        service = InventoryService(11)
        product = self.make_product(product_id=3)
        other = self.make_product(product_id=14)
        service.add_product(product)
        service.add_product(other)

        with self.assertRaises(AttributeError):
            product.product_id = 99

        self.assertIs(service.table.search(3), product)
        self.assertIsNone(service.table.search(99))
        self.assertEqual([p.product_id for p in service.array], [3, 14])

        service.delete_product(3)
        self.assertEqual([p.product_id for p in service.array], [14])
        self.assertIs(service.table.search(14), other)

    def test_edit_and_delete_update_both_structures(self):
        service = InventoryService(11)
        service.add_product(self.make_product())
        service.add_product(self.make_product(product_id=14))  # collides with 3
        updated = service.edit_product(3, stock_quantity=25)
        self.assertEqual(service.table.search(3), updated)
        self.assertEqual(service.array[linear_search(service.array, 3)], updated)
        self.assertEqual(updated.stock_quantity, 25)
        self.assertEqual(updated.name, "Example medicine")      # untouched fields are kept
        self.assertTrue(service.delete_product(3))
        self.assertEqual(linear_search(service.array, 3), -1)
        self.assertIsNotNone(service.table.search(14))
        self.assertEqual(len(service), 1)

    def test_key_edit_cannot_desynchronise_storage(self):
        service = InventoryService()
        service.add_product(self.make_product())
        with self.assertRaises(TypeError):          # product_id cannot be supplied twice
            service.edit_product(3, product_id=99)

    def test_invalid_edit_changes_nothing(self):
        service = InventoryService()
        original = self.make_product()
        service.add_product(original)
        with self.assertRaises(ValueError):
            service.edit_product(3, stock_quantity=-5)
        self.assertIs(service.table.search(3), original)
        self.assertIs(service.array[0], original)

    def test_edit_unknown_product_raises_key_error(self):
        with self.assertRaises(KeyError):
            InventoryService().edit_product(99, name="x")

    def test_special_float_values_are_rejected(self):
        for bad in ("nan", "inf", "-inf"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.make_product(price=bad)

    def test_search_result_counts_work(self):
        service = InventoryService(11)
        service.add_product(self.make_product())
        service.add_product(self.make_product(product_id=14))
        found = service.search(14)
        self.assertEqual(found.product.product_id, 14)
        self.assertEqual(found.array_comparisons, 2)        # second item of the array
        missing = service.search(99)
        self.assertIsNone(missing.product)
        self.assertEqual(missing.array_comparisons, 2)      # whole array examined


if __name__ == "__main__":
    unittest.main()
