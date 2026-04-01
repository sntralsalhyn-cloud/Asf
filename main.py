import os
import telebot
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
OPENROUTER_TOKEN = os.environ.get('OPENROUTER_TOKEN')
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', '').lower()

# طباعة العقود والقيم لتشخيص الأخطاء (يمكن حذفها لاحقًا)
print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")
print(f"HUGGINGFACE_TOKEN: {HUGGINGFACE_TOKEN}")
print(f"OPENROUTER_TOKEN: {OPENROUTER_TOKEN}")
print(f"LLM_PROVIDER: {LLM_PROVIDER}")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_llm(message):
    # نجعل HuggingFace هو الافتراضي دائماً
    if LLM_PROVIDER == 'openrouter':
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "dolphin-mixtral-8x7b",
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
            return f"خطأ: {e} (openrouter)"
    else:  # الإفتراضي HuggingFace
        url = "https://api-inference.huggingface.co/models/cognitivecomputations/dolphin-2.5-mixtral-8x7b"
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