from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class AdmCb(CallbackData, prefix="adm"):
    action: str      # status | pay_ok | pay_no
    order_id: int
    value: str | None = None


def admin_menu() -> ReplyKeyboardMarkup:
    """
    handlers/admin.py dagi menyular bilan mos bo‘lsin.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Yangi buyurtmalar"), KeyboardButton(text="🗓 Bugungi buyurtmalar")],
            [KeyboardButton(text="🏙 Tuman bo‘yicha filter"), KeyboardButton(text="💳 To‘lov bo‘yicha filter")],
            [KeyboardButton(text="📤 Excel export"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="⚙️ Kurslar"), KeyboardButton(text="📢 Kanallar")],
        ],
        resize_keyboard=True
    )


def district_filter_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Hammasi", callback_data="f:dist:ALL")

    # UZ variantlari
    kb.button(text="Toshkent", callback_data="f:dist:Toshkent")
    kb.button(text="Samarqand", callback_data="f:dist:Samarqand")
    kb.button(text="Jizzax", callback_data="f:dist:Jizzax")

    # TR variantlari
    kb.button(text="Selçuklu", callback_data="f:dist:Selçuklu")
    kb.button(text="Meram", callback_data="f:dist:Meram")
    kb.button(text="Karatay", callback_data="f:dist:Karatay")

    kb.adjust(1)
    return kb.as_markup()


def payment_filter_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Hammasi", callback_data="f:pay:ALL")
    kb.button(text="Naqd (CASH)", callback_data="f:pay:CASH")
    kb.button(text="Karta (CARD)", callback_data="f:pay:CARD")
    kb.button(text="Karta: admin kutilmoqda", callback_data="f:pay:WAITING_ADMIN")
    kb.adjust(1)
    return kb.as_markup()


def export_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Bugun", callback_data="exp:today")
    kb.button(text="🗓 Oxirgi 7 kun", callback_data="exp:7")
    kb.button(text="📦 Oxirgi 50 ta", callback_data="exp:last")
    kb.adjust(1)
    return kb.as_markup()


def order_actions_kb(order_id: int, payment_status: str | None, payment_type: str | None) -> InlineKeyboardMarkup:
    """
    Har bir buyurtma ichida:
    - Statuslarni o‘zgartirish
    - Karta bo‘lsa pay ok/no
    """
    kb = InlineKeyboardBuilder()

    # Statuslar
    kb.button(text="✅ Qabul qilindi", callback_data=AdmCb(action="status", order_id=order_id, value="ACCEPTED").pack())
    kb.button(text="📦 Olib ketildi", callback_data=AdmCb(action="status", order_id=order_id, value="PICKED_UP").pack())
    kb.button(text="🚚 Yo‘lda", callback_data=AdmCb(action="status", order_id=order_id, value="ON_THE_WAY").pack())
    kb.button(text="📬 Yetkazildi", callback_data=AdmCb(action="status", order_id=order_id, value="DELIVERED").pack())
    kb.adjust(2, 2)

    # Karta bo‘lsa: admin tasdiqlash / rad etish
    if (payment_type == "CARD") and (payment_status in ("WAITING_CONFIRMATION", "WAITING_ADMIN")):
        kb.button(text="✅ To‘lov tasdiqlash", callback_data=AdmCb(action="pay_ok", order_id=order_id).pack())
        kb.button(text="❌ To‘lov rad etish", callback_data=AdmCb(action="pay_no", order_id=order_id).pack())
        kb.adjust(2, 2, 2)

    return kb.as_markup()