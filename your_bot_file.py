from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
import hashlib

# Database setup
conn = sqlite3.connect('movies.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS movies
             (id INTEGER PRIMARY KEY,
             title TEXT,
             fastupload_url TEXT,
             linkvertise_id TEXT UNIQUE)''')
conn.commit()

TOKEN = '7511109980:AAFNNoKxyp7VOFt6iDulRIiAThjsg_uTOww'
BASE_LINK = "https://link-hub.net/1296252/"  # Your Linkvertise main URL

def generate_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:8]

# 1. Admin Command to Add Movies
def add_movie(update: Update, context: CallbackContext):
    try:
        title = context.args[0]
        fastupload_url = context.args[1]
        
        # Generate unique ID for Linkvertise
        slug = generate_slug(fastupload_url)
        
        # Create Linkvertise URL
        linkvertise_url = f"{BASE_LINK}{slug}"
        
        # Store in database
        c.execute("INSERT INTO movies (title, fastupload_url, linkvertise_id) VALUES (?, ?, ?)",
                 (title, fastupload_url, slug))
        conn.commit()
        
        update.message.reply_text(f"✅ Added!\n"
                                 f"Title: {title}\n"
                                 f"Linkvertise: {linkvertise_url}\n"
                                 f"Direct: {fastupload_url}")
    except:
        update.message.reply_text("❌ Usage: /add \"Movie Title\" \"FastUpload URL\"")

# 2. Handle Telegram Bot Redirects
def start(update: Update, context: CallbackContext):
    if context.args:
        movie_slug = context.args[0]
        c.execute("SELECT fastupload_url FROM movies WHERE linkvertise_id=?", (movie_slug,))
        result = c.fetchone()
        
        if result:
            update.message.reply_document(result[0])
        else:
            update.message.reply_text("❌ Invalid download link")
    else:
        update.message.reply_text("👋 Send /add to contribute movies")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("add", add_movie))
    dp.add_handler(CommandHandler("start", start))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
