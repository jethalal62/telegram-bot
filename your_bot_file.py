import os
import sqlite3
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Database setup
conn = sqlite3.connect('movies.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS movies
             (id INTEGER PRIMARY KEY,
             title TEXT,
             fastupload_url TEXT,
             linkvertise_id TEXT UNIQUE)''')
conn.commit()

# Load Bot Token Securely
TOKEN = os.getenv('7511109980:AAFNNoKxyp7VOFt6iDulRIiAThjsg_uTOww')  # Use environment variable
BASE_LINK = "https://linkvertise.com/1296252/"  # Your Linkvertise main URL

# Function to Generate Unique Slug
def generate_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:8]

# 1. Admin Command to Add Movies
def add_movie(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("❌ Usage: /add \"Movie Title\" \"FastUpload URL\"")
            return
        
        title = args[0]
        fastupload_url = args[1]
        
        # Generate unique ID for Linkvertise
        slug = generate_slug(fastupload_url)
        
        # Create Linkvertise URL
        linkvertise_url = f"{BASE_LINK}{slug}"
        
        # Store in database
        c.execute("INSERT OR IGNORE INTO movies (title, fastupload_url, linkvertise_id) VALUES (?, ?, ?)",
                  (title, fastupload_url, slug))
        conn.commit()
        
        update.message.reply_text(f"✅ Movie Added!\n"
                                  f"🎬 Title: {title}\n"
                                  f"🔗 Linkvertise: {linkvertise_url}\n"
                                  f"📥 Direct: {fastupload_url}")
    except Exception as e:
        update.message.reply_text("❌ An error occurred.")
        print(e)  # Log the error for debugging

# 2. Handle Telegram Bot Redirects
def start(update: Update, context: CallbackContext):
    if context.args:
        movie_slug = context.args[0]
        c.execute("SELECT fastupload_url FROM movies WHERE linkvertise_id=?", (movie_slug,))
        result = c.fetchone()
        
        if result:
            fastupload_url = result[0]
            update.message.reply_text(f"✅ Here is your download link:\n{fastupload_url}")
        else:
            update.message.reply_text("❌ Invalid download link")
    else:
        # Show Welcome Message with Buttons
        keyboard = [[InlineKeyboardButton("Visit Linkvertise", url=BASE_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("👋 Welcome to the Movie Bot! Click below to access downloads:", reply_markup=reply_markup)

# 3. Start the Bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("add", add_movie))
    dp.add_handler(CommandHandler("start", start))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
