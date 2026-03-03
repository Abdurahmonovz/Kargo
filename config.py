import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _csv_ints(v: str) -> list[int]:
    v = (v or "").strip()
    if not v:
        return []
    return [int(x.strip()) for x in v.split(",") if x.strip()]

@dataclass
class Config:
    bot_token: str
    admin_ids: list[int]
    admin_group_id: int | None
    db_path: str

    usd_try_rate: float
    usd_uzs_rate: float
    try_uzs_rate: float

    price_per_kg_usd: float
    taxi_fee_try: float
    min_kg: int

    iban_owner: str
    iban_number: str

def load_config() -> Config:
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is empty")

    ag = (os.getenv("ADMIN_GROUP_ID") or "").strip()
    admin_group_id = int(ag) if ag else None

    return Config(
        bot_token=token,
        admin_ids=_csv_ints(os.getenv("ADMIN_IDS", "")),
        admin_group_id=admin_group_id,
        db_path=os.getenv("DB_PATH", "data/bot.db"),

        usd_try_rate=float(os.getenv("USD_TRY_RATE", "32.0")),
        usd_uzs_rate=float(os.getenv("USD_UZS_RATE", "12500.0")),
        try_uzs_rate=float(os.getenv("TRY_UZS_RATE", "390.0")),

        price_per_kg_usd=float(os.getenv("PRICE_PER_KG_USD", "8")),
        taxi_fee_try=float(os.getenv("TAXI_FEE_TRY", "500")),
        min_kg=int(os.getenv("MIN_KG", "10")),

        iban_owner=os.getenv("IBAN_OWNER", "NURIDDIN MAKHMUDOV"),
        iban_number=os.getenv("IBAN_NUMBER", "TR520020500009134698200001"),
    )