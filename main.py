import os
import telebot
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')

print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")
print(f"HUGGINGFACE_TOKEN: {HUGGINGFACE_TOKEN}")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_llm(message):
    url = "https://api-inference.huggingface.co/models/openchat/openchat-3.5-0106"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": message}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and result and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            return f"خطأ من API: {result['error']}"
        return str(result)
    except Exception as e:
        return f"خطأ: {e} (huggingface)"

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    try:
        answer = ask_llm(message.text)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"خطأ نهائي: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)