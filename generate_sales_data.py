"""Generate a reproducible sample sales dataset for EDA practice."""

from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError as error:
    raise SystemExit(
        "Missing dependency. Install pandas>=2.0.0 and numpy>=1.24.0."
    ) from error


ROW_COUNT = 100_000
RANDOM_SEED = 42
OUTPUT_FILE = Path("sales_data.csv")


def create_sales_data(row_count: int = ROW_COUNT) -> pd.DataFrame:
    """Create transaction data with controlled missing values.

    Missing-value counts are rounded down to whole rows for custom row counts.
    """
    if row_count <= 0:
        raise ValueError("row_count must be a positive integer.")

    # A local generator keeps this function reproducible without changing the
    # random state used by other code in the same Python process.
    rng = np.random.default_rng(RANDOM_SEED)

    products_by_category = {
        "Electronics": ["Laptop", "Headphones", "Monitor", "Keyboard"],
        "Furniture": ["Desk", "Chair", "Bookshelf", "Table"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers"],
        "Office Supplies": ["Notebook", "Pen Set", "Stapler", "Printer Paper"],
    }
    categories = np.array(list(products_by_category))
    regions = np.array(["North", "South", "East", "West", "Central"])

    category_values = rng.choice(categories, size=row_count)
    product_values = np.array(
        [
            rng.choice(products_by_category[category])
            for category in category_values
        ]
    )
    quantity_values = rng.integers(1, 11, size=row_count)
    price_values = np.round(rng.uniform(5.00, 500.00, size=row_count), 2)

    # Add exactly 5% missing prices and 2% missing regions.
    missing_price_mask = np.zeros(row_count, dtype=bool)
    missing_region_mask = np.zeros(row_count, dtype=bool)
    missing_price_count = int(row_count * 0.05)
    missing_region_count = int(row_count * 0.02)
    missing_price_mask[
        rng.choice(row_count, size=missing_price_count, replace=False)
    ] = True
    missing_region_mask[
        rng.choice(row_count, size=missing_region_count, replace=False)
    ] = True
    price_values[missing_price_mask] = np.nan

    dates = pd.to_datetime(
        rng.integers(
            pd.Timestamp("2023-01-01").value // 86_400_000_000_000,
            (pd.Timestamp("2024-12-31").value // 86_400_000_000_000) + 1,
            size=row_count,
        ),
        unit="D",
        origin="unix",
    )
    region_values = rng.choice(regions, size=row_count).astype(object)
    region_values[missing_region_mask] = None

    data = pd.DataFrame(
        {
            "transaction_id": np.arange(1, row_count + 1),
            "customer_id": rng.integers(1, 20_001, size=row_count),
            "product": product_values,
            "category": category_values,
            "quantity": quantity_values,
            "price": price_values,
            "revenue": np.round(quantity_values * price_values, 2),
            "date": dates,
            "region": region_values,
        }
    )
    return data


def main() -> None:
    """Generate and save the sales dataset."""
    try:
        sales_data = create_sales_data()
        expected_columns = [
            "transaction_id",
            "customer_id",
            "product",
            "category",
            "quantity",
            "price",
            "revenue",
            "date",
            "region",
        ]

        if len(sales_data) != ROW_COUNT:
            raise ValueError(f"Expected {ROW_COUNT:,} rows, got {len(sales_data):,}.")
        if list(sales_data.columns) != expected_columns:
            raise ValueError("The generated columns do not match the expected schema.")

        sales_data.to_csv(OUTPUT_FILE, index=False)
        print(f"Successfully generated {len(sales_data):,} transactions.")
        print(f"Saved dataset to: {OUTPUT_FILE.resolve()}")
        print(f"Missing prices: {sales_data['price'].isna().sum():,}")
        print(f"Missing regions: {sales_data['region'].isna().sum():,}")
    except (OSError, ValueError) as error:
        print(f"Failed to generate the sales dataset: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
