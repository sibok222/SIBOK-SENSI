import os
from flask import Flask, request
import telegram
import requests
from deep_translator import GoogleTranslator

# ඔයාගේ Credentials
BOT_TOKEN = "8621084667:AAGrNfeOwpl1H-6PYho3o6r2vICv2Mg4dLM"

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            text = update.message.text

            if text == "/start":
                welcome_text = (
                    "👋 Hello! I am your Multi-Language Link Bypasser Bot.\n"
                    "Send me any short link, and I will get the original link for you!\n\n"
                    "👋 ආයුබෝවන්! මම ඕනෑම භාෂාවකින් වැඩ කරන Link Bypasser Bot කෙනෙක්.\n"
                    "ඔයාගේ Short Link එක මට එවන්න!"
                )
                bot.send_message(chat_id=chat_id, text=welcome_text)
            
            elif "http" in text:
                try:
                    detected_lang = GoogleTranslator(source='auto', target='en').detect(text)
                except:
                    detected_lang = 'en'

                sent_msg = bot.send_message(chat_id=chat_id, text="⏳ Bypassing link... Please wait / පොඩ්ඩක් ඉන්න...")
                
                try:
                    api_url = f"https://api.bypass.vip/bypass?url={text}"
                    res = requests.get(api_url).json()
                    
                    if res.get("status") == "success":
                        dest = res.get("destination")
                        reply_text = f"✅ **Original Link:**\n{dest}"
                        bot.send_message(chat_id=chat_id, text=reply_text, parse_mode="Markdown")
                    else:
                        error_msg = "❌ Failed to bypass this link."
                        if detected_lang == 'si':
                            error_msg = "❌ මේ Link එක Bypass කරන්න බැරි වුණා."
                        bot.send_message(chat_id=chat_id, text=error_msg)
                except Exception as e:
                    bot.send_message(chat_id=chat_id, text="❌ Error occurred! Try again later.")
            else:
                bot.send_message(chat_id=chat_id, text="⚠️ Please send a valid URL / කරුණාකර නිවැරදි Link එකක් එවන්න.")

    return "ok", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is live on Vercel!"

if __name__ == "__main__":
    app.run()
