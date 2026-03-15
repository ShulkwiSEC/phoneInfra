#!/usr/bin/env python3
import os
import json
import phonenumbers
from phonenumbers import geocoder
from dotenv import load_dotenv
import telebot
from api import HelloCallersAPI  # your existing API wrapper

load_dotenv()
COOKIES_RAW = os.getenv("COOKIES_RAW")
XSRF_TOKEN = os.getenv("XSRF_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

api = HelloCallersAPI("https://hellocallers.com", COOKIES_RAW, XSRF_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)


def format_data(data):
    if not data.get("status"):
        return "❌ لم يتم العثور على بيانات"
    names = data.get("data", {}).get("names", [])
    if not names:
        return "ℹ️ لا توجد أسماء مسجلة لهذا الرقم"
    msg = "📌 أسماء مرتبطة بالرقم:\n"
    for n in names:
        msg += f"- {n.get('name')} (مرات الاستخدام: {n.get('count')})\n"
    return msg


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "مرحبًا! أرسل رقم الهاتف مع كود الدولة للبحث عنه.")


@bot.message_handler(func=lambda m: True)
def lookup_phone(message):
    phone = message.text.strip()
    if not any(c.isdigit() for c in phone):
        bot.reply_to(message, "ℹ️ أرسل رقم هاتف صالح مع رمز الدولة. مثال: +201234567890")
        return
    try:
        num = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(num):
            bot.reply_to(message, "❌ رقم الهاتف غير صحيح")
            return
        iso = geocoder.region_code_for_number(num)
        number_e164 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        bot.reply_to(message, "❌ لم يتم التعرف على الرقم. استخدم صيغة صحيحة مثل +201234567890")
        return
    try:
        search_data = api.search_contact(number_e164, iso.lower())
        contacts = search_data.get("data", {}).get("contacts", {}).get("data", [])
        if not contacts:
            bot.reply_to(message, "ℹ️ لم يتم العثور على أي بيانات للرقم")
            return
        contact_id = contacts[0]["id"]
        names_data = api.contact_names(contact_id)
        bot.reply_to(message, format_data(names_data))
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء الاستعلام: {e}")
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()