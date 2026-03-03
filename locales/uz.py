MESSAGES = {
    "menu_order": "📦 Buyurtma berish",
    "menu_help": "🆘 Yordam",

    "legal": "⚠️ Ogohlantirish: Noto‘g‘ri ma’lumot kiritgan shaxs javobgar hisoblanadi.",

    "sub_need": "Buyurtma berishdan oldin iltimos rasmiy kanal(lar)imizga a’zo bo‘ling.",
    "sub_ok": "✅ Rahmat! Davom etishingiz mumkin.",
    "btn_join": "👉 Kanalga o‘tish",
    "btn_check": "✅ Tekshirish",

    "choose_district": "Qaysi viloyatdansiz?",
    "ask_address": "🏠 Manzilingizni kiriting (matn):\nMisol: Chilonzor, 12-mavze, 34-uy",
    "ask_kg": "📦 Yukingiz nechi kg? (faqat butun son)\n❗ Minimum: 10 kg",
    "ask_location": "📍 Iltimos, uyingiz lokatsiyasini yuboring (Location).",
    "btn_loc": "📍 Lokatsiya yuborish",

    "ask_rec_name": "👤 O‘zbekistondagi qabul qiluvchi F.I.O ni kiriting:",
    "ask_rec_phone": "📞 Qabul qiluvchining telefon raqamini kiriting:\nMisol: +998901234567 yoki 901234567",
    "ask_pass_front": "🪪 Pasportning OLD tomoni rasmini yuboring (faqat rasm).",
    "ask_pass_back": "🪪 Pasportning ORQA tomoni rasmini yuboring (faqat rasm).",

    "ask_banned": "🚫 Yuk ichida taqiqlangan buyum yo‘qligiga ishonchingiz komilmi?",
    "yes": "✅ Ha",
    "no": "❌ Yo‘q",
    "banned_no": "❌ Buyurtma bekor qilindi. Taqiqlangan buyum bo‘lsa admin bilan bog‘laning.",

    "ask_items": "🧾 Yuk ichidagi mahsulotlar ro‘yxatini rasmga olib yuboring (faqat rasm).",

    "ask_contact": "📱 Siz bilan bog‘lanish uchun telefon yuboring yoki Telegram username yozing:",
    "btn_contact": "📱 Telefon yuborish",

    "receipt_title": "📄 BUYURTMA MA’LUMOTI",
    "pay_choose": "To‘lov turini tanlang:",
    "cash": "💵 Naqd",
    "card": "💳 Karta",

    "cash_text": "✅ Buyurtmangiz qabul qilindi.\nErtaga kargo xodimimiz olib ketadi.\nTo‘lovni naqd topshirasiz.",

    # owner, iban, amount format bilan to'ldiriladi
    "card_text": "💳 To‘lov uchun ma’lumot:\n\nIsm: {owner}\nIBAN: {iban}\n\n💰 To‘lanadigan summa: {amount}\n\n📸 To‘lov qilgach chek screenshot yuboring.",
    "card_got": "✅ Chek qabul qilindi. Admin tekshirgandan so‘ng tasdiqlanadi.",

    "cancelled": "❌ Bekor qilindi.",
}
def t(key: str, lang: str = "uz") -> str:
    return MESSAGES.get(key, key)