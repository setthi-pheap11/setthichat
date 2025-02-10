import os
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler

# Load API keys from .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Dictionary to store user memory
user_memory = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the user starts the bot."""
    user_id = update.message.chat_id
    user_memory[user_id] = []  # Initialize memory for the new user
    welcome_message = (
        "👋 Welcome to the Setthi Chatbot!\n\n"
        "I can assist you with various topics. Just send me a message and I'll respond.\n"
        "Let's chat! 😊"
    )
    await update.message.reply_text(welcome_message)

async def chat(update: Update, context: CallbackContext) -> None:
    """Handle user messages and remember context."""
    user_id = update.message.chat_id
    user_message = update.message.text

    # Initialize memory for new users
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Append user message to memory
    user_memory[user_id].append(f"You: {user_message}")

    # Prepare conversation history
    conversation_history = "\n".join(user_memory[user_id][-5:])  # Keep last 5 exchanges

    # Generate AI response
    response = model.generate_content(conversation_history)
    bot_reply = response.text if response.text else "Sorry, I couldn't process that."

    # Append bot response to memory
    user_memory[user_id].append(f"Bot: {bot_reply}")

    await update.message.reply_text(bot_reply)

def main():
    """Run the Telegram bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))  # Handle /start command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))  # Handle messages

    # Start polling
    print("Gemini Telegram bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
