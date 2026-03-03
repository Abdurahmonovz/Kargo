from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.context import FSMContext
from db import DB
from config import Config
from states import OrderStates
from locales import t
from utils.calc import fmt_try, fmt_uzs
from keyboards.admin import order_actions_kb

router = Router()


def order_text(order: dict) -> str:
    return (
        f"🔔 Yangi buyurtma: <b>{order.get('order_code')}</b>\n"
        f"Ilçe: <b>{order.get('district')}</b>\n"
        f"Adres: {order.get('address')}\n"
        f"Kg: <b>{order.get('kg')}</b>\n"
        f"Maps: {order.get('maps_link')}\n"
        f"Pay: <b>{order.get('payment_type')}</b> | <b>{order.get('payment_status')}</b>\n"
        f"Status: <b>{order.get('status')}</b>\n"
    )


async def notify_admins(bot, config: Config, order: dict):
    targets = list(config.admin_ids)
    if config.admin_group_id:
        targets.append(config.admin_group_id)

    markup = order_actions_kb(int(order["id"]), order.get("payment_status"), order.get("payment_type"))

    for chat_id in targets:
        try:
            await bot.send_message(chat_id, order_text(order), disable_web_page_preview=True, reply_markup=markup)

            if order.get("passport_front_file_id"):
                await bot.send_photo(chat_id, order["passport_front_file_id"], caption="Pasport FRONT")
            if order.get("passport_back_file_id"):
                await bot.send_photo(chat_id, order["passport_back_file_id"], caption="Pasport BACK")
            if order.get("items_list_file_id"):
                await bot.send_photo(chat_id, order["items_list_file_id"], caption="Items list")
            if order.get("payment_screenshot_file_id"):
                await bot.send_photo(chat_id, order["payment_screenshot_file_id"], caption="Payment screenshot")
        except Exception:
            pass


@router.callback_query(OrderStates.payment_choose, F.data.startswith("pay:"))
async def choose_pay(c: CallbackQuery, state: FSMContext, db: DB, config: Config):
    lang = await db.get_lang(c.from_user.id)
    data = await state.get_data()
    order_id = int(data["order_id"])
    pay = c.data.split(":", 1)[1]

    o = await db.get_order(order_id)
    if not o.get("order_code"):
        code = await db.next_order_code()
        await db.update_order(order_id, order_code=code)
        o = await db.get_order(order_id)

    if pay == "CASH":
        await db.update_order(order_id, payment_type="CASH", payment_status="PAID_CASH", status="NEW")
        await c.message.answer(t("cash_text", lang))
        await state.clear()

        o2 = await db.get_order(order_id)
        await notify_admins(c.bot, config, o2)
        await c.answer()
        return

    if pay == "CARD":
        await db.update_order(order_id, payment_type="CARD", payment_status="WAITING_SCREENSHOT", status="NEW")
        o2 = await db.get_order(order_id)

        amount = fmt_try(o2["total_try"]) if lang == "tr" else fmt_uzs(o2["total_uzs"])
        msg = t("card_text", lang).format(owner=config.iban_owner, iban=config.iban_number, amount=amount)

        await state.set_state(OrderStates.payment_screenshot)
        await c.message.answer(msg)
        await c.answer()
        return


@router.message(OrderStates.payment_screenshot, F.photo)
async def screenshot(m: Message, state: FSMContext, db: DB, config: Config):
    lang = await db.get_lang(m.from_user.id)
    data = await state.get_data()
    if "order_id" not in data:
        await state.clear()
        await m.answer("Xatolik. /start ni bosing")
        return

    order_id = int(data["order_id"])

    await db.update_order(
        order_id,
        payment_screenshot_file_id=m.photo[-1].file_id,
        payment_status="WAITING_ADMIN",
    )

    await m.answer("✅ Chek qabul qilindi. Admin tekshirgandan so‘ng tasdiqlanadi.")
    await state.clear()

    o = await db.get_order(order_id)
    await notify_admins(m.bot, config, o)


@router.message(OrderStates.payment_screenshot)
async def screenshot_wrong(m: Message):
    await m.answer("📸 Iltimos, chek screenshotni rasm ko‘rinishida yuboring.")