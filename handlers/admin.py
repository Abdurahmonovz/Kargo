import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import Config
from db import DB
from keyboards.admin import (
    admin_menu, district_filter_kb, payment_filter_kb, export_kb,
    AdmCb, order_actions_kb
)
from utils.excel import build_orders_xlsx_with_images
from utils.subs import normalize_chat

router = Router()

STATUS_TEXT = {
    "uz": {
        "ACCEPTED": "✅ Buyurtmangiz qabul qilindi",
        "PICKED_UP": "📦 Buyurtmangiz olib ketildi",
        "ON_THE_WAY": "🚚 Buyurtmangiz yo‘lda",
        "DELIVERED": "📬 Buyurtmangiz yetkazildi",
    },
    "tr": {
        "ACCEPTED": "✅ Siparişiniz kabul edildi",
        "PICKED_UP": "📦 Siparişiniz alındı",
        "ON_THE_WAY": "🚚 Siparişiniz yolda",
        "DELIVERED": "📬 Siparişiniz teslim edildi",
    }
}

def is_admin(user_id: int, config: Config) -> bool:
    return user_id in (config.admin_ids or [])

def brief(o: dict) -> str:
    return (
        f"🆔 <b>{o.get('order_code')}</b>\n"
        f"Hudud/İlçe: <b>{o.get('district')}</b>\n"
        f"Manzil/Adres: {o.get('address')}\n"
        f"Kg: <b>{o.get('kg')}</b>\n"
        f"Maps: {o.get('maps_link')}\n"
        f"Pay: <b>{o.get('payment_type')}</b> | <b>{o.get('payment_status')}</b>\n"
        f"Status: <b>{o.get('status')}</b>\n"
    )

async def download_file_by_id(bot, file_id: str, dest_path: str):
    f = await bot.get_file(file_id)
    Path(os.path.dirname(dest_path)).mkdir(parents=True, exist_ok=True)
    await bot.download_file(f.file_path, destination=dest_path)

async def prepare_images_dir(bot, rows: list[dict], images_dir: str):
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    os.makedirs(images_dir, exist_ok=True)

    for r in rows:
        oc = r.get("order_code") or str(r.get("id"))

        if r.get("passport_front_file_id"):
            await download_file_by_id(bot, r["passport_front_file_id"], os.path.join(images_dir, f"{oc}_passport_front.jpg"))
        if r.get("passport_back_file_id"):
            await download_file_by_id(bot, r["passport_back_file_id"], os.path.join(images_dir, f"{oc}_passport_back.jpg"))
        if r.get("items_list_file_id"):
            await download_file_by_id(bot, r["items_list_file_id"], os.path.join(images_dir, f"{oc}_items.jpg"))
        if r.get("payment_screenshot_file_id"):
            await download_file_by_id(bot, r["payment_screenshot_file_id"], os.path.join(images_dir, f"{oc}_payment.jpg"))

@router.message(Command("admin"))
async def admin_entry(m: Message, config: Config):
    if not is_admin(m.from_user.id, config):
        await m.answer(f"❌ Admin emassiz.\nSizning ID: <code>{m.from_user.id}</code>")
        return
    await m.answer("Admin panel:", reply_markup=admin_menu())

@router.message(Command("id"))
async def my_id(m: Message):
    await m.answer(f"ID: <code>{m.from_user.id}</code>")

@router.message(F.text == "🆕 Yangi buyurtmalar")
async def new_orders(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    rows = await db.list_orders_limit(30)
    if not rows:
        await m.answer("Buyurtma yo‘q.")
        return
    for o in rows:
        await m.answer(brief(o), reply_markup=order_actions_kb(int(o["id"]), o.get("payment_status"), o.get("payment_type")))

@router.message(F.text == "🗓 Bugungi buyurtmalar")
async def today(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    rows = await db.list_orders_today()
    if not rows:
        await m.answer("Bugun buyurtma yo‘q.")
        return
    for o in rows[:30]:
        await m.answer(brief(o), reply_markup=order_actions_kb(int(o["id"]), o.get("payment_status"), o.get("payment_type")))

@router.message(F.text == "🏙 Tuman bo‘yicha filter")
async def filter_dist_menu(m: Message, config: Config):
    if not is_admin(m.from_user.id, config):
        return
    await m.answer("Tumanni tanlang:", reply_markup=district_filter_kb())

@router.message(F.text == "💳 To‘lov bo‘yicha filter")
async def filter_pay_menu(m: Message, config: Config):
    if not is_admin(m.from_user.id, config):
        return
    await m.answer("To‘lov filter:", reply_markup=payment_filter_kb())

@router.callback_query(F.data.startswith("f:dist:"))
async def apply_dist_filter(c: CallbackQuery, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return
    dist = c.data.split(":", 2)[2]
    if dist == "ALL":
        rows = await db.list_orders_limit(30)
        title = "Hammasi"
    else:
        rows = await db.list_orders_by_district(dist, 30)
        title = dist

    await c.message.answer(f"📌 Filter (tuman): <b>{title}</b>")
    if not rows:
        await c.message.answer("Natija yo‘q.")
        await c.answer(); return

    for o in rows:
        await c.message.answer(brief(o), reply_markup=order_actions_kb(int(o["id"]), o.get("payment_status"), o.get("payment_type")))
    await c.answer()

@router.callback_query(F.data.startswith("f:pay:"))
async def apply_pay_filter(c: CallbackQuery, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return
    val = c.data.split(":", 2)[2]
    if val == "ALL":
        rows = await db.list_orders_limit(30); title = "Hammasi"
    elif val == "WAITING_ADMIN":
        rows = await db.list_orders_by_payment_status("WAITING_ADMIN", 30); title = "Karta (admin kutilmoqda)"
    else:
        rows = await db.list_orders_by_payment_type(val, 30); title = val

    await c.message.answer(f"📌 Filter (to‘lov): <b>{title}</b>")
    if not rows:
        await c.message.answer("Natija yo‘q.")
        await c.answer(); return

    for o in rows:
        await c.message.answer(brief(o), reply_markup=order_actions_kb(int(o["id"]), o.get("payment_status"), o.get("payment_type")))
    await c.answer()

@router.callback_query(AdmCb.filter(F.action == "status"))
async def set_status(c: CallbackQuery, callback_data: AdmCb, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return

    order_id = callback_data.order_id
    status = callback_data.value or "NEW"
    await db.update_order(order_id, status=status)

    o = await db.get_order(order_id)
    await c.message.answer(f"✅ Status yangilandi: <b>{o.get('order_code')}</b> → <b>{status}</b>")

    # userga til bo'yicha tushunarli xabar
    user_lang = o.get("lang") or "uz"
    msg = STATUS_TEXT.get(user_lang, STATUS_TEXT["uz"]).get(status, status)
    try:
        await c.bot.send_message(o["user_id"], f"{msg}\n🆔 {o.get('order_code')}")
    except Exception:
        pass

    await c.answer()

@router.callback_query(AdmCb.filter(F.action == "pay_ok"))
async def pay_ok(c: CallbackQuery, callback_data: AdmCb, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return

    order_id = callback_data.order_id
    await db.update_order(order_id, payment_status="CONFIRMED")

    o = await db.get_order(order_id)
    await c.message.answer(f"✅ To‘lov tasdiqlandi: <b>{o.get('order_code')}</b>")

    try:
        await c.bot.send_message(o["user_id"], f"✅ To‘lov tasdiqlandi.\n🆔 {o.get('order_code')}")
    except Exception:
        pass

    await c.answer()

@router.callback_query(AdmCb.filter(F.action == "pay_no"))
async def pay_no(c: CallbackQuery, callback_data: AdmCb, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return

    order_id = callback_data.order_id
    await db.update_order(order_id, payment_status="REJECTED")

    o = await db.get_order(order_id)
    await c.message.answer(f"❌ To‘lov rad etildi: <b>{o.get('order_code')}</b>")

    try:
        await c.bot.send_message(o["user_id"], f"❌ Chek rad etildi. Qayta yuboring.\n🆔 {o.get('order_code')}")
    except Exception:
        pass

    await c.answer()

@router.message(F.text == "📢 Kanallar")
async def channels_menu(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    chs = [normalize_chat(x) for x in await db.list_channels()]
    txt = "📢 Majburiy kanallar:\n" + ("\n".join(chs) if chs else "(bo‘sh)") + "\n\n"
    txt += "Qo‘shish: /add_channel @kanal\nO‘chirish: /del_channel @kanal"
    await m.answer(txt)

@router.message(Command("add_channel"))
async def add_channel(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await m.answer("Misol: /add_channel @mychannel yoki https://t.me/mychannel")
        return
    ch = normalize_chat(parts[1].strip())
    await db.add_channel(ch)
    await m.answer(f"✅ Kanal qo‘shildi: {ch}")

@router.message(Command("del_channel"))
async def del_channel(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await m.answer("Misol: /del_channel @mychannel")
        return
    ch = normalize_chat(parts[1].strip())
    await db.del_channel(ch)
    await m.answer(f"✅ Kanal o‘chirildi: {ch}")

@router.message(F.text == "⚙️ Kurslar")
async def rates_hint(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    usd_try, usd_uzs, try_uzs = await db.get_rates(config.usd_try_rate, config.usd_uzs_rate, config.try_uzs_rate)
    await m.answer(
        "Hozirgi kurslar:\n"
        f"USD→TRY: <b>{usd_try}</b>\n"
        f"USD→UZS: <b>{usd_uzs}</b>\n"
        f"TRY→UZS: <b>{try_uzs}</b>\n\n"
        "Yangilash:\n/rates USD_TRY USD_UZS TRY_UZS\nMisol: /rates 32 12500 390"
    )

@router.message(Command("rates"))
async def set_rates(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    parts = (m.text or "").split()
    if len(parts) != 4:
        await m.answer("Misol: /rates 32 12500 390")
        return
    _, usd_try, usd_uzs, try_uzs = parts
    await db.set_setting("USD_TRY_RATE", usd_try)
    await db.set_setting("USD_UZS_RATE", usd_uzs)
    await db.set_setting("TRY_UZS_RATE", try_uzs)
    await m.answer("✅ Kurslar saqlandi.")

@router.message(F.text == "📊 Statistika")
async def stats(m: Message, config: Config, db: DB):
    if not is_admin(m.from_user.id, config):
        return
    today_kg = await db.stats_today_kg()
    month_kg = await db.stats_month_kg()
    await m.answer(f"📊 Statistika\n\nBugun jami kg: <b>{today_kg}</b>\nShu oy jami kg: <b>{month_kg}</b>")

@router.message(F.text == "📤 Excel export")
async def export_menu(m: Message, config: Config):
    if not is_admin(m.from_user.id, config):
        return
    await m.answer("Qaysi oraliq eksport qilinsin?", reply_markup=export_kb())

@router.callback_query(F.data.startswith("exp:"))
async def export_do(c: CallbackQuery, config: Config, db: DB):
    if not is_admin(c.from_user.id, config):
        await c.answer("No access"); return

    mode = c.data.split(":", 1)[1]
    if mode == "today":
        rows = await db.list_orders_days(0)
        name = "orders_today.xlsx"
    elif mode == "7":
        rows = await db.list_orders_days(7)
        name = "orders_last_7_days.xlsx"
    else:
        rows = await db.list_orders_limit(50)
        name = "orders_last_50.xlsx"

    if not rows:
        await c.message.answer("Eksport uchun buyurtma topilmadi.")
        await c.answer(); return

    tmp_dir = os.path.join("tmp_export", f"exp_{int(datetime.now().timestamp())}")
    await prepare_images_dir(c.bot, rows, tmp_dir)

    bio = build_orders_xlsx_with_images(rows, tmp_dir)
    out_path = os.path.join(tmp_dir, name)
    with open(out_path, "wb") as f:
        f.write(bio.getvalue())

    await c.message.answer_document(FSInputFile(out_path), caption="✅ Excel tayyor")

    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass

    await c.answer()