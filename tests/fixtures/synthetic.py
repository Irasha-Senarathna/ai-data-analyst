"""Generate a small, deterministic dataset shaped exactly like Olist + Open-Meteo.

Tests and CI use this instead of the real (licensed, 126 MB) data. It keeps the
real data's quirks so the cleaning logic is exercised:
- review_id repeated across two orders
- products with no category, and a category with no English translation
- orders with no items (unavailable / canceled)
- the same person (customer_unique_id) with several customer_ids
- duplicate geolocation rows per zip prefix, one with coordinates outside Brazil
"""

import csv
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from pipeline.olist import OLIST_TABLES
from pipeline.weather import WeatherRow

SEED = 7
START = datetime(2017, 1, 1)
END = datetime(2018, 8, 31)

STATES = {  # state -> (city, zip prefix base)
    "SP": ("sao paulo", 1000),
    "RJ": ("rio de janeiro", 20000),
    "MG": ("belo horizonte", 30000),
    "RS": ("porto alegre", 90000),
    "PR": ("curitiba", 80000),
    "BA": ("salvador", 40000),
    "PE": ("recife", 50000),
    "DF": ("brasilia", 70000),
    "AM": ("manaus", 69000),
}
STATE_WEIGHTS = [40, 14, 12, 6, 5, 6, 4, 3, 2]

CATEGORIES = {
    "beleza_saude": "health_beauty",
    "cama_mesa_banho": "bed_bath_table",
    "esporte_lazer": "sports_leisure",
    "informatica_acessorios": "computers_accessories",
    "moveis_decoracao": "furniture_decor",
    "utilidades_domesticas": "housewares",
    "relogios_presentes": "watches_gifts",
}
UNTRANSLATED_CATEGORY = "pc_gamer"

HEADERS = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ],
    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "sellers": ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
    "category_translation": ["product_category_name", "product_category_name_english"],
}

Row = list[str]


@dataclass
class SyntheticData:
    tables: dict[str, list[Row]] = field(default_factory=lambda: {t: [] for t in HEADERS})
    weather: list[WeatherRow] = field(default_factory=list)


def ts(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


def make_id(rng: random.Random) -> str:
    return f"{rng.getrandbits(128):032x}"


def random_moment(rng: random.Random) -> datetime:
    seconds = int((END - START).total_seconds())
    return START + timedelta(seconds=rng.randrange(seconds))


def zip_prefix(state: str, rng: random.Random) -> str:
    return f"{STATES[state][1] + rng.randrange(50):05d}"


def add_customers(data: SyntheticData, rng: random.Random, count: int) -> list[str]:
    people = [make_id(rng) for _ in range(int(count * 0.9))]
    customer_ids = []
    for i in range(count):
        state = rng.choices(list(STATES), STATE_WEIGHTS)[0]
        person = people[i % len(people)]  # the last 10% are repeat customers
        customer_id = make_id(rng)
        customer_ids.append(customer_id)
        data.tables["customers"].append(
            [customer_id, person, zip_prefix(state, rng), STATES[state][0], state]
        )
    return customer_ids


def add_sellers(data: SyntheticData, rng: random.Random, count: int) -> list[str]:
    seller_ids = []
    for _ in range(count):
        state = rng.choices(list(STATES), STATE_WEIGHTS)[0]
        seller_id = make_id(rng)
        seller_ids.append(seller_id)
        data.tables["sellers"].append([seller_id, zip_prefix(state, rng), STATES[state][0], state])
    return seller_ids


def add_products(data: SyntheticData, rng: random.Random, count: int) -> list[str]:
    categories = [*CATEGORIES, UNTRANSLATED_CATEGORY]
    product_ids = []
    for i in range(count):
        product_id = make_id(rng)
        product_ids.append(product_id)
        category = "" if i < 2 else categories[i % len(categories)]
        dims = [str(rng.randint(10, 60)) for _ in range(3)]
        data.tables["products"].append(
            [
                product_id,
                category,
                str(rng.randint(20, 60)),
                str(rng.randint(100, 2000)),
                str(rng.randint(1, 6)),
                str(rng.randint(100, 5000)),
                *dims,
            ]
        )
    for portuguese, english in CATEGORIES.items():
        data.tables["category_translation"].append([portuguese, english])
    return product_ids


def add_order(
    data: SyntheticData,
    rng: random.Random,
    customer_id: str,
    product_ids: list[str],
    seller_ids: list[str],
    status: str,
) -> str:
    order_id = make_id(rng)
    purchased = random_moment(rng)
    approved = purchased + timedelta(hours=rng.randint(1, 30))
    estimated = purchased + timedelta(days=rng.randint(10, 30))
    carrier = approved + timedelta(days=rng.randint(1, 4)) if status != "canceled" else None
    delivered = (
        carrier + timedelta(days=rng.randint(2, 25)) if carrier and status == "delivered" else None
    )
    data.tables["orders"].append(
        [
            order_id,
            customer_id,
            status,
            ts(purchased),
            ts(approved),
            ts(carrier),
            ts(delivered),
            ts(estimated.replace(hour=0, minute=0, second=0)),
        ]
    )
    if status == "unavailable":
        return order_id  # no items, like the real data

    total = 0.0
    for item_number in range(1, rng.choice([1, 1, 1, 2, 3]) + 1):
        price = round(rng.uniform(10, 500), 2)
        freight = round(rng.uniform(5, 50), 2)
        total += price + freight
        data.tables["order_items"].append(
            [
                order_id,
                str(item_number),
                rng.choice(product_ids),
                rng.choice(seller_ids),
                ts(approved + timedelta(days=5)),
                f"{price:.2f}",
                f"{freight:.2f}",
            ]
        )
    if rng.random() < 0.1:  # split between a voucher and a card
        voucher = round(total * 0.3, 2)
        data.tables["order_payments"].append([order_id, "1", "voucher", "1", f"{voucher:.2f}"])
        data.tables["order_payments"].append(
            [order_id, "2", "credit_card", "3", f"{total - voucher:.2f}"]
        )
    else:
        method = rng.choices(["credit_card", "boleto", "debit_card"], [75, 20, 5])[0]
        installments = str(rng.randint(1, 10)) if method == "credit_card" else "1"
        data.tables["order_payments"].append([order_id, "1", method, installments, f"{total:.2f}"])
    return order_id


def add_review(data: SyntheticData, rng: random.Random, order_id: str, review_id: str) -> None:
    created = random_moment(rng)
    score = rng.choices([1, 2, 3, 4, 5], [10, 3, 8, 20, 59])[0]
    message = "" if rng.random() < 0.6 else "Produto chegou, tudo certo."
    data.tables["order_reviews"].append(
        [
            review_id,
            order_id,
            str(score),
            "",
            message,
            ts(created.replace(hour=0, minute=0, second=0)),
            ts(created + timedelta(days=1)),
        ]
    )


def add_orders(
    data: SyntheticData,
    rng: random.Random,
    customer_ids: list[str],
    product_ids: list[str],
    seller_ids: list[str],
) -> None:
    statuses = ["delivered"] * 92 + ["shipped"] * 3 + ["canceled"] * 2 + ["unavailable"] * 3
    reviewed: list[str] = []
    for customer_id in customer_ids:
        status = rng.choice(statuses)
        order_id = add_order(data, rng, customer_id, product_ids, seller_ids, status)
        if status == "delivered":
            reviewed.append(order_id)
    shared_review = make_id(rng)
    for i, order_id in enumerate(reviewed):
        review_id = shared_review if i < 2 else make_id(rng)  # one review covers two orders
        add_review(data, rng, order_id, review_id)


def add_geolocation(data: SyntheticData, rng: random.Random) -> None:
    for state, (city, base) in STATES.items():
        for offset in range(50):
            prefix = f"{base + offset:05d}"
            for _ in range(2):  # duplicates per prefix, like the source
                lat, lng = -15 + rng.uniform(-5, 5), -47 + rng.uniform(-5, 5)
                data.tables["geolocation"].append([prefix, f"{lat:.6f}", f"{lng:.6f}", city, state])
    data.tables["geolocation"].append(["01000", "42.0", "10.0", "sao paulo", "SP"])  # bad point


def add_weather(data: SyntheticData, rng: random.Random) -> None:
    day = START.date()
    while day <= END.date():
        for state in STATES:
            rain = round(rng.uniform(5, 40), 1) if rng.random() < 0.3 else 0.0
            data.weather.append(
                WeatherRow(
                    state, day, round(rng.uniform(24, 34), 1), round(rng.uniform(14, 22), 1), rain
                )
            )
        day += timedelta(days=1)


def generate(orders: int = 600) -> SyntheticData:
    rng = random.Random(SEED)
    data = SyntheticData()
    customer_ids = add_customers(data, rng, orders)
    seller_ids = add_sellers(data, rng, 30)
    product_ids = add_products(data, rng, 40)
    add_orders(data, rng, customer_ids, product_ids, seller_ids)
    add_geolocation(data, rng)
    add_weather(data, rng)
    return data


def write_csvs(data: SyntheticData, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for table, filename in OLIST_TABLES.items():
        path = out_dir / filename
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS[table])
            writer.writerows(data.tables[table])
        paths[table] = path
    return paths


def last_day() -> date:
    return END.date()
