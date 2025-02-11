import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Vercel URL

# Initialize Flask app
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Configure Google Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Dictionary to store user memory
user_memory = {}

def set_webhook():
    """Set the Telegram bot webhook to Vercel URL"""
    webhook_url = f"{WEBHOOK_URL}/webhook"
    response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")
    print("Webhook Set Response:", response.json())

def process_message(update: Update):
    """Process user messages and generate responses using Google Gemini"""
    user_id = update.message.chat_id
    user_message = update.message.text

    # Initialize memory for new users
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Append user message to memory
    user_memory[user_id].append(f"You: {user_message}")

    # Prepare conversation history
    conversation_history = "\n".join(user_memory[user_id][-5:])  # Keep last 5 messages

    # Generate AI response
    response = model.generate_content(conversation_history)
    bot_reply = response.text if response.text else "Sorry, I couldn't process that."

    # Append bot response to memory
    user_memory[user_id].append(f"Bot: {bot_reply}")

    bot.send_message(chat_id=user_id, text=bot_reply)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram messages via webhook"""
    update = Update.de_json(request.get_json(), bot)
    process_message(update)
    return jsonify({"status": "ok"}), 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook_route():
    """Endpoint to manually set the webhook"""
    set_webhook()
    return jsonify({"message": "Webhook set successfully!"}), 200

@app.route("/", methods=["GET"])
def home():
    """Root endpoint for Vercel health check"""
    return "✅ Telegram Bot is Running on Vercel!", 200

if __name__ == "__main__":
    set_webhook()
