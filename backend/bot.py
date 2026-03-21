import telebot
from telebot import types
import threading
import time

BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"
WEBAPP_URL = "https://insiderad.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    ref_code = args[1] if len(args) > 1 else ''

    if ref_code:
        web_url = WEBAPP_URL + "?ref=" + ref_code
    else:
        web_url = WEBAPP_URL

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="💎 Открыть Mytonads",
        web_app=types.WebAppInfo(url=web_url)
    ))

    bot.send_message(
        message.chat.id,
        "💎 <b>Mytonads</b> — рекламная биржа в Telegram!\n\n"
        "👁 Смотри рекламу — зарабатывай TON\n"
        "📢 Размещай рекламу — продвигай проекты\n\n"
        "Нажми кнопку чтобы начать 👇",
        parse_mode="HTML",
        reply_markup=markup
    )

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

def start_bot_thread():
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    print("Bot thread started!")
