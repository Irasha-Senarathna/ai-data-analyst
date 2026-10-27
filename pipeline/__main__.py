"""`python -m pipeline`: materialize every asset once and print its metadata."""

import sys

from dagster import materialize

from pipeline.definitions import olist_files, warehouse, weather_files

ASSETS = [olist_files, weather_files, warehouse]


def main() -> int:
    result = materialize(ASSETS)
    if not result.success:
        return 1
    for name in ("olist_files", "weather_files", "warehouse"):
        for materialization in result.asset_materializations_for_node(name):
            print(name)
            for key, value in materialization.metadata.items():
                print(f"  {key}: {value.value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
