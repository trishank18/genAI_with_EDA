"""Launch D-Tale to explore the sample sales dataset interactively."""

from pathlib import Path
import sys


DATA_FILE = Path(__file__).resolve().parent / "sales_data.csv"


def main() -> None:
    """Load the CSV and open it in a D-Tale browser session."""
    try:
        import dtale
        import pandas as pd
    except ImportError as error:
        raise RuntimeError(
            'Missing dependency. Install with: python -m pip install '
            '"pandas>=2.0.0" "dtale>=3.10.0"'
        ) from error

    try:
        sales_data = pd.read_csv(DATA_FILE)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}. Place sales_data.csv beside this script."
        ) from error
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        raise RuntimeError(f"Could not load {DATA_FILE}: {error}") from error

    if sales_data.empty:
        raise ValueError(f"The dataset is empty: {DATA_FILE}")

    print(f"Loaded {len(sales_data):,} rows from {DATA_FILE.name}.")

    try:
        # Use an available port and keep the D-Tale server in this process.
        # Foreground mode keeps the terminal active until the user presses Ctrl+C.
        from dtale.app import find_free_port

        port = find_free_port()
        url = f"http://127.0.0.1:{port}"
        print("Starting D-Tale; keep this terminal open while using the GUI.")
        print(f"D-Tale URL: {url}")
        dtale.show(
            sales_data,
            name="Sales Dataset",
            host="127.0.0.1",
            port=port,
            open_browser=True,
            subprocess=False,
        )
    except Exception as error:
        raise RuntimeError(f"Could not launch D-Tale: {error}") from error


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, FileNotFoundError, ValueError) as error:
        print(f"D-Tale launch failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
