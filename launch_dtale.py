"""Launch D-Tale to explore the sample sales dataset interactively."""

from pathlib import Path
import sys
import webbrowser


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
        # D-Tale starts a local web app and opens the default browser.
        instance = dtale.show(
            sales_data,
            name="Sales Dataset",
            host="127.0.0.1",
            open_browser=False,
        )
    except Exception as error:
        raise RuntimeError(f"Could not launch D-Tale: {error}") from error

    instance_url = getattr(instance, "_url", None)
    if not instance_url:
        raise RuntimeError("D-Tale started but did not provide an access URL.")

    # Use loopback explicitly so the link works on this computer even when
    # the machine hostname is not resolvable by the browser.
    from urllib.parse import urlsplit

    port = urlsplit(instance_url).port
    if port is None:
        raise RuntimeError(f"Could not determine D-Tale's port from {instance_url}.")
    url = f"http://127.0.0.1:{port}"
    browser_opened = webbrowser.open(url, new=2)

    print("D-Tale launched successfully.")
    print(f"Open the interactive EDA interface at: {url}")
    if not browser_opened:
        print("The browser did not open automatically; copy the URL above into it.")
    print("Keep this Python session running while using D-Tale.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, FileNotFoundError, ValueError) as error:
        print(f"D-Tale launch failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
