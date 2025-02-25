from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
import time
import os

# ✅ Telegram Bot Setup
TOKEN = "7774398370:AAE1jf7ALbf90s1HKijVoAsoJeO5Jtb7_b4"
bot = telebot.TeleBot(TOKEN)

# ✅ Store subscribers (users who start the bot)
SUBSCRIBERS_FILE = "subscribers.txt"
LAST_RESULT_FILE = "last_result.txt"  # Stores the last fetched result

# ✅ GTU Result Page URL
GTU_URL = "https://www.gtu.ac.in/result.aspx"

# ✅ Correct ChromeDriver Path (LOCAL SYSTEM)
CHROMEDRIVER_PATH = r"C:\Users\lenov\OneDrive\Desktop\gtubot\chromedriver.exe"  # Update this!

# ✅ Setup ChromeDriver Options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background (no UI)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ✅ Setup ChromeDriver Service
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# ✅ Load Subscribers
def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

# ✅ Save Subscribers
def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        f.write("\n".join(subscribers))

# ✅ Load Last Result
def load_last_result():
    if os.path.exists(LAST_RESULT_FILE):
        with open(LAST_RESULT_FILE, "r") as f:
            return f.read().strip()
    return ""

# ✅ Save Last Result
def save_last_result(result_text):
    with open(LAST_RESULT_FILE, "w") as f:
        f.write(result_text)

# ✅ Start Command
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = str(message.chat.id)
    subscribers = load_subscribers()

    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers(subscribers)
        bot.send_message(chat_id, "✅ You have subscribed to GTU Result Notifications!")
    else:
        bot.send_message(chat_id, "ℹ️ You are already subscribed!")

# ✅ Stop Command
@bot.message_handler(commands=["stop"])
def stop(message):
    chat_id = str(message.chat.id)
    subscribers = load_subscribers()

    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)
        bot.send_message(chat_id, "❌ You have unsubscribed from GTU Result Notifications.")
    else:
        bot.send_message(chat_id, "ℹ️ You are not subscribed.")

# ✅ Check GTU Results and Notify Users
def check_result():
    driver.get(GTU_URL)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "resultDiv")))
        result_text = driver.find_element(By.ID, "resultDiv").text.strip()

        if result_text:
            last_result = load_last_result()

            if result_text != last_result:  # ✅ New result detected!
                save_last_result(result_text)  # ✅ Save new result
                subscribers = load_subscribers()
                
                for chat_id in subscribers:
                    bot.send_message(chat_id, f"🎉 GTU Result Update:\n{result_text}\nCheck here: {GTU_URL}")
                
                print("✅ New result found and sent to all subscribers.")
            else:
                print("⚠️ No new results. Last result is still the same.")

    except Exception as e:
        print(f"❌ Error fetching result: {str(e)}")

# 🔄 Keep Checking for Results
def run_bot():
    while True:
        check_result()
        time.sleep(60)  # ✅ Check for new results **EVERY MINUTE**

import threading
threading.Thread(target=run_bot, daemon=True).start()

bot.polling()
