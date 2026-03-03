from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from db import DB
from config import Config
from states import OrderStates
from locales import t
from keyboards.user import district_kb, location_kb, yes_no_kb, contact_kb, payment_kb
from utils.calc import calc_prices, fmt_try, fmt_uzs

router = Router()

UZ_DISTRICTS = {"toshkent": "Toshkent", "samarqand": "Samarqand", "jizzax": "Jizzax"}
TR_DISTRICTS = {"selçuklu": "Selçuklu", "meram": "Meram", "karatay": "Karatay"}


# ✅ Buyurtma berish tugmasi bosilganda
@router.message(F.text.in_([t("menu_order", "uz"), t("menu_order", "tr")]))
async def start_order(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)

    await state.clear()
    order_id = await db.create_order(m.from_user.id, lang)
    await state.update_data(order_id=order_id)

    await state.set_state(OrderStates.district)
    await m.answer(t("choose_district", lang), reply_markup=district_kb(lang))


# ✅ Tumanni INLINE tugma bosilganda
@router.callback_query(OrderStates.district, F.data.startswith("dist:"))
async def district_cb(c: CallbackQuery, state: FSMContext, db: DB):
    lang = await db.get_lang(c.from_user.id)
    data = await state.get_data()

    if "order_id" not in data:
        await c.answer("Xatolik: order topilmadi. /start ni bosing")
        await state.clear()
        return

    order_id = int(data["order_id"])
    district = c.data.split(":", 1)[1]

    await db.update_order(order_id, district=district)
    await state.set_state(OrderStates.address)

    try:
        await c.message.edit_text(f"{t('choose_district', lang)} ✅ {district}")
    except Exception:
        pass

    await c.message.answer(t("ask_address", lang))
    await c.answer()


# ✅ Tumanni YOZIB yuborsa ham qabul qilamiz (UZ/TR bo‘yicha)
@router.message(OrderStates.district, F.text)
async def district_text(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    txt = (m.text or "").strip().lower()

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])

    mapping = UZ_DISTRICTS if lang == "uz" else TR_DISTRICTS
    found = None
    for key, value in mapping.items():
        if key in txt or value.lower() in txt:
            found = value
            break

    if found:
        await db.update_order(order_id, district=found)
        await state.set_state(OrderStates.address)
        await m.answer(f"{t('choose_district', lang)} ✅ {found}")
        await m.answer(t("ask_address", lang))
        return

    await m.answer(t("choose_district", lang), reply_markup=district_kb(lang))


@router.message(OrderStates.address, F.text)
async def address(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    txt = (m.text or "").strip()

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    if len(txt) < 8:
        await m.answer(t("ask_address", lang))
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, address=txt)

    await state.set_state(OrderStates.kg)
    await m.answer(t("ask_kg", lang))


@router.message(OrderStates.address)
async def address_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_address", lang))


@router.message(OrderStates.kg, F.text)
async def kg(m: Message, state: FSMContext, db: DB, config: Config):
    lang = await db.get_lang(m.from_user.id)
    txt = (m.text or "").strip()

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    if not txt.isdigit():
        await m.answer(t("ask_kg", lang))
        return

    val = int(txt)
    if val < config.min_kg:
        await m.answer(f"{t('ask_kg', lang)}\n❗ MIN: {config.min_kg} kg")
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, kg=val)

    await state.set_state(OrderStates.location)
    await m.answer(t("ask_location", lang), reply_markup=location_kb(t("btn_loc", lang)))


@router.message(OrderStates.kg)
async def kg_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_kg", lang))


@router.message(OrderStates.location, F.location)
async def loc(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)

    # ✅ loading animatsiya
    try:
        await m.bot.send_chat_action(m.chat.id, ChatAction.FIND_LOCATION)
    except Exception:
        pass

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])
    lat = float(m.location.latitude)
    lon = float(m.location.longitude)
    link = f"https://www.google.com/maps?q={lat},{lon}"

    await db.update_order(order_id, lat=lat, lon=lon, maps_link=link)

    await state.set_state(OrderStates.receiver_name)
    await m.answer(t("ask_rec_name", lang))


@router.message(OrderStates.location)
async def loc_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_location", lang), reply_markup=location_kb(t("btn_loc", lang)))


@router.message(OrderStates.receiver_name, F.text)
async def receiver_name(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    txt = (m.text or "").strip()

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    if len(txt) < 3:
        await m.answer(t("ask_rec_name", lang))
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, receiver_name=txt)

    await state.set_state(OrderStates.receiver_phone)
    await m.answer(t("ask_rec_phone", lang))


@router.message(OrderStates.receiver_name)
async def receiver_name_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_rec_name", lang))


@router.message(OrderStates.receiver_phone, F.text)
async def receiver_phone(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    txt = (m.text or "").strip().replace(" ", "")

    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    if lang == "uz":
        # +998901234567 yoki 901234567
        if not (txt.startswith("+998") and len(txt) in (13, 14)) and not (txt.isdigit() and len(txt) == 9):
            await m.answer(t("ask_rec_phone", lang))
            return
        phone = txt if txt.startswith("+998") else "+998" + txt
    else:
        # TR: erkin (faqat +/raqam, uzunlik 9-15)
        cleaned = txt.replace("+", "")
        if not cleaned.isdigit() or len(cleaned) < 9 or len(cleaned) > 15:
            await m.answer(t("ask_rec_phone", lang))
            return
        phone = txt

    order_id = int(data["order_id"])
    await db.update_order(order_id, receiver_phone=phone)

    await state.set_state(OrderStates.passport_front)
    await m.answer(t("ask_pass_front", lang))


@router.message(OrderStates.receiver_phone)
async def receiver_phone_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_rec_phone", lang))


@router.message(OrderStates.passport_front, F.photo)
async def pass_front(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    data = await state.get_data()

    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, passport_front_file_id=m.photo[-1].file_id)

    await state.set_state(OrderStates.passport_back)
    await m.answer(t("ask_pass_back", lang))


@router.message(OrderStates.passport_front)
async def pass_front_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_pass_front", lang))


@router.message(OrderStates.passport_back, F.photo)
async def pass_back(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    data = await state.get_data()

    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, passport_back_file_id=m.photo[-1].file_id)

    await state.set_state(OrderStates.banned_confirm)
    await m.answer(t("ask_banned", lang), reply_markup=yes_no_kb(t("yes", lang), t("no", lang)))


@router.message(OrderStates.passport_back)
async def pass_back_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_pass_back", lang))


@router.callback_query(OrderStates.banned_confirm, F.data.startswith("yn:"))
async def banned(c: CallbackQuery, state: FSMContext, db: DB):
    lang = await db.get_lang(c.from_user.id)
    ans = c.data.split(":", 1)[1]
    data = await state.get_data()

    if "order_id" not in data:
        await state.clear()
        await c.message.edit_text("Xatolik. Iltimos /start ni bosing")
        await c.answer()
        return

    order_id = int(data["order_id"])

    if ans == "no":
        await db.update_order(order_id, banned_ok=0, status="CANCELED")
        await state.clear()
        await c.message.edit_text(t("banned_no", lang))
        await c.answer()
        return

    await db.update_order(order_id, banned_ok=1)
    await state.set_state(OrderStates.items_list_photo)

    try:
        await c.message.edit_text(t("ask_banned", lang) + " ✅")
    except Exception:
        pass

    await c.message.answer(t("ask_items", lang))
    await c.answer()


@router.message(OrderStates.banned_confirm)
async def banned_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_banned", lang), reply_markup=yes_no_kb(t("yes", lang), t("no", lang)))


@router.message(OrderStates.items_list_photo, F.photo)
async def items(m: Message, state: FSMContext, db: DB):
    lang = await db.get_lang(m.from_user.id)
    data = await state.get_data()

    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])
    await db.update_order(order_id, items_list_file_id=m.photo[-1].file_id)

    await state.set_state(OrderStates.contact)
    await m.answer(t("ask_contact", lang), reply_markup=contact_kb(t("btn_contact", lang)))


@router.message(OrderStates.items_list_photo)
async def items_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_items", lang))


@router.message(OrderStates.contact, F.text | F.contact)
async def contact(m: Message, state: FSMContext, db: DB, config: Config):
    lang = await db.get_lang(m.from_user.id)
    data = await state.get_data()

    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. Iltimos /start ni bosing")
        return

    order_id = int(data["order_id"])

    phone = None
    username = None
    if m.contact and m.contact.phone_number:
        phone = m.contact.phone_number
    else:
        txt = (m.text or "").strip()
        if not txt:
            await m.answer(t("ask_contact", lang))
            return
        username = txt

    usd_try, usd_uzs, try_uzs = await db.get_rates(config.usd_try_rate, config.usd_uzs_rate, config.try_uzs_rate)

    o = await db.get_order(order_id)
    if not o:
        await state.clear()
        await m.answer("Xatolik: order topilmadi")
        return

    kg_val = int(o["kg"])

    prices = calc_prices(
        kg=kg_val,
        price_per_kg_usd=config.price_per_kg_usd,
        taxi_fee_try=config.taxi_fee_try,
        usd_try_rate=usd_try,
        usd_uzs_rate=usd_uzs,
        try_uzs_rate=try_uzs,
    )

    await db.update_order(
        order_id,
        contact_phone=phone,
        contact_username=username,
        usd_part=prices["usd_part"],
        taxi_try=prices["taxi_try"],
        total_try=prices["total_try"],
        total_uzs=prices["total_uzs"],
    )

    o = await db.get_order(order_id)
    amount = fmt_try(o["total_try"]) if lang == "tr" else fmt_uzs(o["total_uzs"])
    line = f"{kg_val}kg × {int(config.price_per_kg_usd)}$ + {int(config.taxi_fee_try)} TL"

    text = (
        f"{t('receipt_title', lang)}\n\n"
        f"Hudud/İlçe: {o['district']}\n"
        f"Manzil/Adres: {o['address']}\n"
        f"Og‘irlik/Kg: {kg_val}\n"
        f"Hisob/Calc: {line}\n"
        f"Jami/Total: {amount}\n\n"
        f"{t('pay_choose', lang)}"
    )

    await state.set_state(OrderStates.payment_choose)
    await m.answer(text, reply_markup=payment_kb(t("cash", lang), t("card", lang)))


@router.message(OrderStates.contact)
async def contact_wrong(m: Message, db: DB):
    lang = await db.get_lang(m.from_user.id)
    await m.answer(t("ask_contact", lang), reply_markup=contact_kb(t("btn_contact", lang)))