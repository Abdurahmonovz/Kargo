MESSAGES = {
    "menu_order": "📦 Sipariş ver",
    "menu_help": "🆘 Yardım",

    "legal": "⚠️ Uyarı: Yanlış bilgi giren kişi sorumludur.",

    "sub_need": "Sipariş vermeden önce lütfen resmi kanal(lar)ımıza abone olun.",
    "sub_ok": "✅ Teşekkürler! Devam edebilirsiniz.",
    "btn_join": "👉 Kanala git",
    "btn_check": "✅ Kontrol et",

    "choose_district": "Hangi ilçedesiniz?",
    "ask_address": "🏠 Adresinizi yazın (metin):\nÖrn: Karatay / Fevzi Çakmak Mh. / 10420 Sk / No:1",
    "ask_kg": "📦 Kargonuz kaç kg? (sadece tam sayı)\n❗ Minimum: 10 kg",
    "ask_location": "📍 Lütfen konumunuzu gönderin (Location).",
    "btn_loc": "📍 Konum gönder",

    "ask_rec_name": "👤 Türkiye’deki alıcı Ad Soyad yazın:",
    "ask_rec_phone": "📞 Alıcının telefon numarasını yazın:\nÖrn: +90XXXXXXXXXX veya 05XXXXXXXXX",
    "ask_pass_front": "🪪 Pasaport ÖN yüz fotoğrafını gönderin (sadece foto).",
    "ask_pass_back": "🪪 Pasaport ARKA yüz fotoğrafını gönderin (sadece foto).",

    "ask_banned": "🚫 Yasaklı ürün olmadığından emin misiniz?",
    "yes": "✅ Evet",
    "no": "❌ Hayır",
    "banned_no": "❌ Sipariş iptal edildi. Yasaklı ürün varsa admin ile iletişime geçin.",

    "ask_items": "🧾 Kargo içindeki ürün listesinin fotoğrafını gönderin (sadece foto).",

    "ask_contact": "📱 İletişim için telefon gönderin veya Telegram username yazın:",
    "btn_contact": "📱 Telefon gönder",

    "receipt_title": "📄 SİPARİŞ BİLGİSİ",
    "pay_choose": "Ödeme türünü seçin:",
    "cash": "💵 Nakit",
    "card": "💳 Kart",

    "cash_text": "✅ Siparişiniz alındı.\nYarın kargo personeli alacaktır.\nÖdemeyi nakit vereceksiniz.",

    "card_text": "💳 Ödeme bilgileri:\n\nİsim: {owner}\nIBAN: {iban}\n\n💰 Ödenecek tutar: {amount}\n\n📸 Ödeme yaptıktan sonra dekont ekran görüntüsü gönderin.",
    "card_got": "✅ Dekont alındı. Admin kontrol edip onaylayacak.",

    "cancelled": "❌ İptal edildi.",
}
def t(key: str, lang: str = "tr") -> str:
    return MESSAGES.get(key, key)