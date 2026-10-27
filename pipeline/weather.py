"""Daily historical weather for each Brazilian state capital (Open-Meteo, CC BY 4.0)."""

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx

from pipeline.download import DownloadResult, download_file
from pipeline.settings import DBT_DIR

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_START = date(2016, 9, 1)
WEATHER_END = date(2018, 10, 31)
DAILY_VARIABLES = ("temperature_2m_max", "temperature_2m_min", "precipitation_sum")
STATES_SEED = DBT_DIR / "seeds" / "brazil_states.csv"


@dataclass(frozen=True)
class Capital:
    state: str
    city: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class WeatherRow:
    state: str
    weather_date: date
    temperature_2m_max: float | None
    temperature_2m_min: float | None
    precipitation_sum: float | None


def load_capitals(seed_path: Path = STATES_SEED) -> tuple[Capital, ...]:
    with seed_path.open(encoding="utf-8") as file:
        return tuple(
            Capital(row["state"], row["capital"], float(row["latitude"]), float(row["longitude"]))
            for row in csv.DictReader(file)
        )


CAPITALS = load_capitals()


def weather_url(capital: Capital) -> str:
    query = {
        "latitude": capital.latitude,
        "longitude": capital.longitude,
        "start_date": WEATHER_START.isoformat(),
        "end_date": WEATHER_END.isoformat(),
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "auto",  # each capital's own local day
    }
    return f"{ARCHIVE_URL}?{urlencode(query)}"


def weather_file(raw_dir: Path, state: str) -> Path:
    return raw_dir / "weather" / f"{state}.json"


def download_weather(client: httpx.Client, raw_dir: Path) -> list[DownloadResult]:
    return [
        download_file(client, weather_url(capital), weather_file(raw_dir, capital.state))
        for capital in CAPITALS
    ]


def parse_weather(payload: dict[str, Any], state: str) -> list[WeatherRow]:
    daily = payload["daily"]
    return [
        WeatherRow(
            state=state,
            weather_date=date.fromisoformat(day),
            temperature_2m_max=daily["temperature_2m_max"][i],
            temperature_2m_min=daily["temperature_2m_min"][i],
            precipitation_sum=daily["precipitation_sum"][i],
        )
        for i, day in enumerate(daily["time"])
    ]


def read_weather(raw_dir: Path) -> list[WeatherRow]:
    rows: list[WeatherRow] = []
    for capital in CAPITALS:
        payload = json.loads(weather_file(raw_dir, capital.state).read_text())
        rows.extend(parse_weather(payload, capital.state))
    return rows
