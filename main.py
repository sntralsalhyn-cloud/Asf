import os
import telebot
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
LLM_MODE = os.environ.get('LLM_MODE', 'gemini')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_gemini(message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"خطأ في API Gemini: {e}"

def ask_groq(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكاء صناعي."},
            {"role": "user", "content": message}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطأ في API Groq: {e}"

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    try:
        if LLM_MODE == 'groq':
            answer = ask_groq(message.text)
        else:
            answer = ask_gemini(message.text)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"خطأ نهائي: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)