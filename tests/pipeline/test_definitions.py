from dagster import AssetKey

from pipeline.definitions import defs


def test_pipeline_has_download_and_warehouse_assets() -> None:
    graph = defs.resolve_asset_graph()

    keys = {key.to_user_string() for key in graph.get_all_asset_keys()}

    assert keys == {"olist_files", "weather_files", "warehouse"}


def test_warehouse_depends_on_both_downloads() -> None:
    graph = defs.resolve_asset_graph()

    parents = graph.get(AssetKey("warehouse")).parent_keys

    assert parents == {AssetKey("olist_files"), AssetKey("weather_files")}
