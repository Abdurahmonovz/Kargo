from aiogram.exceptions import TelegramBadRequest

def normalize_chat(chat: str) -> str:
    chat = (chat or "").strip()
    if chat.startswith("https://t.me/"):
        chat = "@" + chat.split("/")[-1]
    if chat and not chat.startswith("@") and not chat.startswith("-100"):
        chat = "@" + chat
    return chat

async def is_member(bot, user_id: int, chat: str) -> bool:
    chat = normalize_chat(chat)
    try:
        member = await bot.get_chat_member(chat, user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramBadRequest:
        # bot kanalni ko‘ra olmayapti (admin emas / kanal private / username noto‘g‘ri)
        return False
    except Exception:
        return False