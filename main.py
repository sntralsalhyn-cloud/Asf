import os
import telebot
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_TOKEN = os.environ.get('OPENROUTER_TOKEN')
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openrouter')  # اختياري: 'huggingface'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_llm(message):
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    elif LLM_PROVIDER == 'huggingface':
        url = "https://api-inference.huggingface.co/models/cognitivecomputations/dolphin-2.5-mixtral-8x7b"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        payload = {"inputs": message}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return str(result)
    else:
        return "يرجى تعيين مزود الذكاء الصناعي الصحيح."

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    try:
        answer = ask_llm(message.text)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)