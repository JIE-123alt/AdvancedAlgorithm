"""sample_data.py - the pre-defined pharmacy records loaded when the system starts."""

from datetime import date

from product import Product

# (id, name, category, price, stock, expiry, needs prescription)
RAW_RECORDS = [
    (1015, "Ibuprofen 400mg",           "Pain Relief",  8.50,  80, date(2027, 5, 30), False),
    (1073, "Aspirin 100mg",              "Pain Relief",  6.20,  60, date(2027, 11, 30), False),
    (1108, "Amoxicillin 500mg",          "Antibiotic",   14.80, 45, date(2027, 2, 28), True),
    (1131, "Azithromycin 250mg",         "Antibiotic",   18.90, 30, date(2027, 4, 30), True),
    (1204, "Cetirizine 10mg",            "Allergy",      7.30,  90, date(2028, 1, 31), False),
    (1227, "Loratadine 10mg",            "Allergy",      9.10,  70, date(2028, 3, 31), False),
    (1260, "Omeprazole 20mg",            "Digestive",    12.60, 55, date(2027, 9, 30), False),
    (1289, "Loperamide 2mg",             "Digestive",    6.80,  40, date(2027, 7, 31), False),
    (1312, "Oral Rehydration Salts",     "Digestive",    2.50, 200, date(2028, 6, 30), False),
    (1345, "Metformin 500mg",            "Diabetes",     11.40, 65, date(2027, 12, 31), True),
    (1378, "Gliclazide 80mg",            "Diabetes",     13.20, 35, date(2027, 10, 31), True),
    (1401, "Salbutamol Inhaler",         "Respiratory",  22.00, 25, date(2027, 6, 30), True),
    (1434, "Cough Syrup 100ml",          "Respiratory",  10.90, 75, date(2027, 3, 31), False),
    (1467, "Vitamin C 1000mg",           "Vitamins",     24.50, 150, date(2028, 8, 31), False),
    (1500, "Vitamin D3 1000IU",          "Vitamins",     29.90, 95, date(2028, 5, 31), False),
    (1042, "Paracetamol 500mg",          "Pain Relief",  5.90, 120, date(2027, 8, 31), False),
    (1533, "Multivitamin Tablets",       "Vitamins",     35.00, 85, date(2028, 2, 29), False),
    (1566, "Hydrocortisone Cream 1%",    "Skin Care",    9.60,  50, date(2027, 1, 31), False),
    (1599, "Antiseptic Solution 100ml",  "First Aid",    7.80, 110, date(2029, 1, 31), False),
    (1632, "Adhesive Plasters (50 pcs)", "First Aid",    5.50, 180, date(2030, 1, 31), False),
]


def build_sample_products():
    """Create the Product objects for the pre-defined records."""
    return [
        Product(pid, name, category, price, stock, expiry, needs_rx)
        for pid, name, category, price, stock, expiry, needs_rx in RAW_RECORDS
    ]
