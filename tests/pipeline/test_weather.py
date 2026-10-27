import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from pipeline.weather import CAPITALS, download_weather, parse_weather, weather_url

PAYLOAD = {
    "daily": {
        "time": ["2017-01-01", "2017-01-02"],
        "temperature_2m_max": [30.1, 31.5],
        "temperature_2m_min": [20.0, None],
        "precipitation_sum": [0.0, 12.4],
    }
}


def test_one_capital_per_brazilian_state() -> None:
    states = [capital.state for capital in CAPITALS]

    assert len(states) == 27
    assert len(set(states)) == 27
    assert "SP" in states and "DF" in states


def test_weather_url_requests_daily_variables_for_the_order_period() -> None:
    query = parse_qs(urlparse(weather_url(CAPITALS[0])).query)

    assert query["start_date"] == ["2016-09-01"]
    assert query["end_date"] == ["2018-10-31"]
    assert query["daily"] == ["temperature_2m_max,temperature_2m_min,precipitation_sum"]


def test_parse_weather_returns_one_row_per_day() -> None:
    rows = parse_weather(PAYLOAD, "SP")

    assert [row.weather_date.isoformat() for row in rows] == ["2017-01-01", "2017-01-02"]
    assert rows[1].state == "SP"
    assert rows[1].precipitation_sum == 12.4
    assert rows[1].temperature_2m_min is None


def test_download_weather_is_idempotent(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, content=json.dumps(PAYLOAD).encode())

    client = httpx.Client(transport=httpx.MockTransport(handler))

    first = download_weather(client, tmp_path)
    second = download_weather(client, tmp_path)

    assert len(first) == 27
    assert all(result.skipped for result in second)
    assert len(calls) == 27
