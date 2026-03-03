def calc_prices(kg: int, price_per_kg_usd: float, taxi_fee_try: float,
                usd_try_rate: float, usd_uzs_rate: float, try_uzs_rate: float) -> dict:
    usd_part = kg * price_per_kg_usd
    total_try = usd_part * usd_try_rate + taxi_fee_try
    total_uzs = usd_part * usd_uzs_rate + taxi_fee_try * try_uzs_rate
    return {"usd_part": usd_part, "taxi_try": taxi_fee_try, "total_try": total_try, "total_uzs": total_uzs}

def fmt_try(x: float) -> str:
    return f"{int(round(x)):,} TL".replace(",", " ")

def fmt_uzs(x: float) -> str:
    return f"{int(round(x)):,} so‘m".replace(",", " ")