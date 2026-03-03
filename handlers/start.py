from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db import DB
from states import StartStates
from locales import t
from keyboards.user import lang_kb, main_menu, sub_kb
from utils.subs import is_member, normalize_chat

router = Router()

@router.message(Command("start"))
async def start(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StartStates.choose_lang)
    await m.answer("Til / Dil tanlang:", reply_markup=lang_kb())

@router.message(StartStates.choose_lang)
async def choose_lang(m: Message, state: FSMContext, db: DB):
    txt = (m.text or "").strip()
    if "Türk" in txt or "🇹🇷" in txt:
        lang = "tr"
    else:
        lang = "uz"

    await db.set_lang(m.from_user.id, lang)
    await m.answer(t("legal", lang))

    channels = await db.list_channels()
    channels = [normalize_chat(c) for c in channels]

    if not channels:
        await state.clear()
        await m.answer("✅", reply_markup=main_menu(t("menu_order", lang), t("menu_help", lang)))
        return

    await state.set_state(StartStates.sub_check)
    await m.answer(t("sub_need", lang), reply_markup=sub_kb(t("btn_join", lang), t("btn_check", lang), channels))

@router.callback_query(F.data == "sub_check")
async def sub_check(c: CallbackQuery, state: FSMContext, db: DB):
    lang = await db.get_lang(c.from_user.id)
    channels = [normalize_chat(x) for x in await db.list_channels()]

    ok = True
    for ch in channels:
        if not await is_member(c.bot, c.from_user.id, ch):
            ok = False
            break

    if not ok:
        await c.answer("❌")
        await c.message.edit_text(
            t("sub_need", lang) +
            "\n\n⚠️ Agar siz a’zo bo‘lsangiz ham chiqmayotgan bo‘lsa:\n"
            "— Kanal PUBLIC bo‘lsin (@username)\n"
            "— Botni kanalga ADMIN qilib qo‘ying.",
            reply_markup=sub_kb(t("btn_join", lang), t("btn_check", lang), channels)
        )
        return

    await c.answer("OK")
    await c.message.answer(t("sub_ok", lang), reply_markup=main_menu(t("menu_order", lang), t("menu_help", lang)))
    await state.clear()