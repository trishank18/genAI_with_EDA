"""Create HTML EDA reports for the sample sales dataset."""

from importlib import metadata
from pathlib import Path
import re
import sys


DATA_FILE = Path("sales_data.csv")
YDATA_REPORT_FILE = Path("ydata_report.html")
SWEETVIZ_REPORT_FILE = Path("sweetviz_report.html")
MINIMUM_VERSIONS = {
    "pandas": (2, 0, 0),
    "ydata-profiling": (4, 6, 0),
    "sweetviz": (2, 3, 0),
}


def numeric_version(version: str) -> tuple[int, ...]:
    """Return the numeric part of a package version for minimum checks."""
    numbers = re.match(r"\d+(?:\.\d+)*", version)
    if numbers is None:
        raise ValueError(f"Cannot read package version: {version}")
    return tuple(int(part) for part in numbers.group().split("."))


def verify_versions() -> None:
    """Confirm required packages are installed at supported versions."""
    for package, minimum in MINIMUM_VERSIONS.items():
        try:
            installed = metadata.version(package)
        except metadata.PackageNotFoundError as error:
            raise RuntimeError(
                f"{package} is not installed. Install it with: "
                'python -m pip install "pandas>=2.0.0" '
                '"ydata-profiling>=4.6.0" "sweetviz>=2.3.0"'
            ) from error

        if numeric_version(installed) < minimum:
            minimum_text = ".".join(map(str, minimum))
            raise RuntimeError(
                f"{package}>={minimum_text} is required; found {installed}."
            )
        print(f"Verified {package} {installed}.")


def main() -> None:
    """Load sales data and save YData Profiling and Sweetviz reports."""
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required.")
    print(f"Using Python {sys.version.split()[0]}.")

    verify_versions()

    # Import only after checking package availability and supported versions.
    import pandas as pd
    import sweetviz as sv
    from ydata_profiling import ProfileReport

    try:
        sales_data = pd.read_csv(DATA_FILE)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Could not find {DATA_FILE.resolve()}. Run this script from the "
            "folder containing sales_data.csv."
        ) from error
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        raise RuntimeError(f"Could not load {DATA_FILE}: {error}") from error
    print(f"Loaded {len(sales_data):,} rows from {DATA_FILE}.")

    try:
        profile = ProfileReport(sales_data, minimal=True)
        profile.to_file(YDATA_REPORT_FILE)
    except Exception as error:
        raise RuntimeError(f"Could not create the YData report: {error}") from error
    print(f"Saved YData Profiling report to {YDATA_REPORT_FILE.resolve()}.")

    try:
        # Sweetviz requires a target column with no missing values. Keep all
        # rows in the YData report, and exclude only missing-target rows here.
        sweetviz_data = sales_data.dropna(subset=["revenue"])
        excluded_rows = len(sales_data) - len(sweetviz_data)
        if sweetviz_data.empty:
            raise ValueError("No rows have a non-missing revenue target.")
        if excluded_rows:
            print(
                f"Excluding {excluded_rows:,} rows with missing revenue "
                "from the Sweetviz report."
            )

        sweetviz_report = sv.analyze(sweetviz_data, target_feat="revenue")
        sweetviz_report.show_html(
            filepath=str(SWEETVIZ_REPORT_FILE), open_browser=False
        )
    except Exception as error:
        raise RuntimeError(f"Could not create the Sweetviz report: {error}") from error
    print(f"Saved Sweetviz report to {SWEETVIZ_REPORT_FILE.resolve()}.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, FileNotFoundError, ValueError) as error:
        print(f"EDA report generation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
