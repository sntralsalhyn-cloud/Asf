import os
import telebot
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
LLM_MODE = os.environ.get('LLM_MODE', 'gemini').strip().lower()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_gemini(message):
    if not GEMINI_API_KEY:
        return "خطأ: لم يتم توفير مفتاح Gemini في متغير البيئة."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        result = r.json()
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0].get("text", "لا يوجد رد من الذكاء الصناعي.")
        else:
            return f"خطأ في استجابة Gemini: {result}"
    except Exception as e:
        return f"خطأ في API Gemini: {e}"

def ask_groq(message):
    if not GROQ_API_KEY:
        return "خطأ: لم يتم توفير مفتاح Groq في متغير البيئة."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "أنت مساع�� ذكاء صناعي."},
            {"role": "user", "content": message}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        result = r.json()
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return f"خطأ في استجابة Groq: {result}"
    except Exception as e:
        return f"خطأ في API Groq: {e}"

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    try:
        if LLM_MODE == "groq":
            answer = ask_groq(message.text)
        else:
            answer = ask_gemini(message.text)
        if not (answer and isinstance(answer, str) and answer.strip()):
            answer = "⚠️ لم يتمكن الذكاء الصناعي من تقديم إجابة، حاول لاحقاً أو تحقق من المفاتيح."
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"خطأ نهائي غير متوقع: {e}")

if __name__ == "__main__":
    print("تم تشغيل البوت على الوضع:", LLM_MODE)
    print("هل مفتاح Gemini موجود؟", bool(GEMINI_API_KEY))
    print("هل مفتاح Groq موجود؟", bool(GROQ_API_KEY))
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("فشل تشغيل البوت:", e)