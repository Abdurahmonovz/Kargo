from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# -----------------------------
# Language choose keyboard
# -----------------------------
def lang_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O‘zbek"), KeyboardButton(text="🇹🇷 Türk")]
        ],
        resize_keyboard=True
    )


# -----------------------------
# Main menu (user)
# -----------------------------
def main_menu(order_text: str, help_text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=order_text)],
            [KeyboardButton(text=help_text)],
        ],
        resize_keyboard=True
    )


# -----------------------------
# Subscription inline keyboard
# channels: ["@channel1", "@channel2", ...]
# -----------------------------
def sub_kb(btn_join: str, btn_check: str, channels: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # Kanalga o‘tish tugmasi (har kanal uchun)
    for ch in channels:
        username = (ch or "").replace("@", "").strip()
        if not username:
            continue
        kb.button(text=btn_join, url=f"https://t.me/{username}")

    # Tekshirish tugmasi
    kb.button(text=btn_check, callback_data="sub_check")

    kb.adjust(1)
    return kb.as_markup()


# -----------------------------
# District/Viloyat (Inline)
# UZ: Toshkent/Samarqand/Jizzax
# TR: Selçuklu/Meram/Karatay
# -----------------------------
def district_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if lang == "uz":
        kb.button(text="Toshkent", callback_data="dist:Toshkent")
        kb.button(text="Samarqand", callback_data="dist:Samarqand")
        kb.button(text="Jizzax", callback_data="dist:Jizzax")
    else:
        kb.button(text="Selçuklu", callback_data="dist:Selçuklu")
        kb.button(text="Meram", callback_data="dist:Meram")
        kb.button(text="Karatay", callback_data="dist:Karatay")

    kb.adjust(1)
    return kb.as_markup()


# -----------------------------
# Location request (Reply)
# -----------------------------
def location_kb(btn_text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn_text, request_location=True)]],
        resize_keyboard=True
    )


# -----------------------------
# Yes/No (Inline)
# callback: yn:yes / yn:no
# -----------------------------
def yes_no_kb(yes_text: str, no_text: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=yes_text, callback_data="yn:yes")
    kb.button(text=no_text, callback_data="yn:no")
    kb.adjust(2)
    return kb.as_markup()


# -----------------------------
# Contact request (Reply)
# -----------------------------
def contact_kb(btn_text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn_text, request_contact=True)]],
        resize_keyboard=True
    )


# -----------------------------
# Payment choose (Inline)
# callback: pay:CASH / pay:CARD
# -----------------------------
def payment_kb(cash_text: str, card_text: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=cash_text, callback_data="pay:CASH")
    kb.button(text=card_text, callback_data="pay:CARD")
    kb.adjust(2)
    return kb.as_markup()