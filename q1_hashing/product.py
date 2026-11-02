"""product.py - entity class for one product sold by the pharmacy."""

import math
from datetime import date

CURRENCY = "RM"
DEFAULT_CATEGORY = "General"      # used when the category is left blank


class Product:
    """A medicine / health product stocked by the pharmacy.

    product_id             int    unique key of the product (used by the hash table)
    name                   str    display name, e.g. "Paracetamol 500mg"
    category               str    grouping such as "Pain Relief" (DEFAULT_CATEGORY if blank)
    price                  float  unit price in ringgit, rounded to 2 decimal places
    stock_quantity         int    units currently on the shelf
    expiry_date            date   expiry of the current batch
    requires_prescription  bool   True if it can only be sold with a prescription
    """

    def __init__(self, product_id, name, category, price, stock_quantity,
                 expiry_date, requires_prescription=False):
        # Validate every value first, so a bad record is never created.
        # `type(x) is not int` also rejects True/False, which Python treats as ints.
        if type(product_id) is not int or product_id <= 0:
            raise ValueError("Product ID must be a positive whole number.")

        name = str(name).strip()
        if not name:
            raise ValueError("Product name cannot be empty.")

        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError("Price must be a number.") from None
        if not math.isfinite(price) or price < 0:
            raise ValueError("Price must be a finite number, 0 or more.")

        if type(stock_quantity) is not int or stock_quantity < 0:
            raise ValueError("Stock quantity must be a whole number, 0 or more.")

        if type(expiry_date) is not date:
            raise ValueError("Expiry date must be a valid date.")

        if type(requires_prescription) is not bool:
            raise ValueError("Prescription status must be True or False.")

        self._product_id = product_id
        self.name = name
        self.category = str(category).strip() or DEFAULT_CATEGORY
        self.price = round(price, 2)
        self.stock_quantity = stock_quantity
        self.expiry_date = expiry_date
        self.requires_prescription = requires_prescription

    def __str__(self):
        """One-line summary used when a product is found."""
        return (f"ID: {self.product_id} | Name: {self.name} | "
                f"Price: {CURRENCY}{self.price:.2f} | Stock: {self.stock_quantity}")
        
    @property
    def product_id(self):
        """Read-only lookup key assigned when the product is created."""
        return self._product_id

    def extra_details(self):
        """Second line with the remaining attributes."""
        prescription = "Yes" if self.requires_prescription else "No"
        return (f"Category: {self.category} | Expiry: {self.expiry_date.isoformat()} | "
                f"Prescription needed: {prescription}")
