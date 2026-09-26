"""
generate_data.py

Builds a star-schema SQLite database (sales_dashboard.db) and populates it
with 10,000+ synthetic records using Faker, for the Enterprise Analytics &
Forecasting Dashboard Power BI project.

Usage:
    pip install faker pandas --break-system-packages
    python generate_data.py
"""

import sqlite3
from faker import Faker
import random
import datetime

fake = Faker()

# ---------------------------------------------------------------------------
# Connect to SQLite (creates the file if it doesn't exist)
# ---------------------------------------------------------------------------
conn = sqlite3.connect("sales_dashboard.db")
cursor = conn.cursor()

# ---------------------------------------------------------------------------
# Drop old tables if they exist (safe to re-run this script)
# ---------------------------------------------------------------------------
cursor.executescript("""
DROP TABLE IF EXISTS DimCustomer;
DROP TABLE IF EXISTS DimProduct;
DROP TABLE IF EXISTS DimRegion;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS FactSales;
""")

# ---------------------------------------------------------------------------
# Create star-schema tables: 1 fact table + 4 dimension tables
# ---------------------------------------------------------------------------
cursor.executescript("""
CREATE TABLE DimCustomer (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    Segment TEXT,
    AcquisitionCost REAL,
    Retained TEXT
);

CREATE TABLE DimProduct (
    ProductID INTEGER PRIMARY KEY,
    Category TEXT,
    SubCategory TEXT,
    Brand TEXT
);

CREATE TABLE DimRegion (
    RegionID INTEGER PRIMARY KEY,
    Country TEXT,
    State TEXT,
    City TEXT
);

CREATE TABLE DimDate (
    DateID INTEGER PRIMARY KEY,
    FullDate TEXT,
    Month INTEGER,
    Quarter INTEGER,
    Year INTEGER
);

CREATE TABLE FactSales (
    TransactionID INTEGER PRIMARY KEY,
    DateID INTEGER,
    CustomerID INTEGER,
    ProductID INTEGER,
    RegionID INTEGER,
    Revenue REAL,
    Cost REAL,
    Profit REAL,
    FOREIGN KEY(DateID) REFERENCES DimDate(DateID),
    FOREIGN KEY(CustomerID) REFERENCES DimCustomer(CustomerID),
    FOREIGN KEY(ProductID) REFERENCES DimProduct(ProductID),
    FOREIGN KEY(RegionID) REFERENCES DimRegion(RegionID)
);
""")

# ---------------------------------------------------------------------------
# Populate DimCustomer (1,000 customers)
# ---------------------------------------------------------------------------
for i in range(1, 1001):
    cursor.execute("INSERT INTO DimCustomer VALUES (?, ?, ?, ?, ?)", (
        i,
        fake.name(),
        random.choice(["Retail", "Enterprise", "Online"]),
        round(random.uniform(100, 1000), 2),
        random.choice(["Y", "N"])
    ))

# ---------------------------------------------------------------------------
# Populate DimProduct (100 products)
# ---------------------------------------------------------------------------
for i in range(1, 101):
    cursor.execute("INSERT INTO DimProduct VALUES (?, ?, ?, ?)", (
        i,
        random.choice(["Electronics", "Clothing", "Furniture"]),
        random.choice(["Premium", "Standard", "Budget"]),
        fake.company()
    ))

# ---------------------------------------------------------------------------
# Populate DimRegion (20 regions)
# ---------------------------------------------------------------------------
for i in range(1, 21):
    cursor.execute("INSERT INTO DimRegion VALUES (?, ?, ?, ?)", (
        i,
        "India",
        random.choice(["Tamil Nadu", "Karnataka", "Kerala", "Maharashtra"]),
        fake.city()
    ))

# ---------------------------------------------------------------------------
# Populate DimDate (2,000 consecutive days starting 2020-01-01)
# ---------------------------------------------------------------------------
start_date = datetime.date(2020, 1, 1)
for i in range(1, 2001):
    date = start_date + datetime.timedelta(days=i)
    cursor.execute("INSERT INTO DimDate VALUES (?, ?, ?, ?, ?)", (
        i,
        date.strftime("%Y-%m-%d"),
        date.month,
        (date.month - 1) // 3 + 1,
        date.year
    ))

# ---------------------------------------------------------------------------
# Populate FactSales (10,000 transactions, linked to the dimensions above)
# ---------------------------------------------------------------------------
for i in range(1, 10001):
    date_id = random.randint(1, 2000)
    cust_id = random.randint(1, 1000)
    prod_id = random.randint(1, 100)
    region_id = random.randint(1, 20)
    revenue = round(random.uniform(100, 5000), 2)
    cost = round(revenue * random.uniform(0.4, 0.8), 2)
    profit = round(revenue - cost, 2)
    cursor.execute("INSERT INTO FactSales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
        i, date_id, cust_id, prod_id, region_id, revenue, cost, profit
    ))

conn.commit()
conn.close()

print("Database created: sales_dashboard.db")
print("  - 1,000 customers")
print("  - 100 products")
print("  - 20 regions")
print("  - 2,000 dates")
print("  - 10,000 sales transactions")
