from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import hashlib
import os

# Database setup
conn = sqlite3.connect('movies.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS movies
             (id INTEGER PRIMARY KEY,
             title TEXT,
             fastupload_url TEXT,
             linkvertise_id TEXT UNIQUE)''')
conn.commit()

TOKEN = os.getenv('7511109980:AAFNNoKxyp7VOFt6iDulRIiAThjsg_uTOww')
BASE_LINK = "https://link-hub.net/1296252/"  # Your Linkvertise main URL

def generate_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:8]

# 1. Admin Command to Add Movies
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        await update.message.reply_text(f"✅ Added!\n"
                                        f"Title: {title}\n"
                                        f"Linkvertise: {linkvertise_url}\n"
                                        f"Direct: {fastupload_url}")
    except:
        await update.message.reply_text("❌ Usage: /add \"Movie Title\" \"FastUpload URL\"")

# 2. Handle Telegram Bot Redirects
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        movie_slug = context.args[0]
        c.execute("SELECT fastupload_url FROM movies WHERE linkvertise_id=?", (movie_slug,))
        result = c.fetchone()
        
        if result:
            await update.message.reply_document(result[0])
        else:
            await update.message.reply_text("❌ Invalid download link")
    else:
        await update.message.reply_text("👋 Send /add to contribute movies")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("add", add_movie))
    application.add_handler(CommandHandler("start", start))
    
    application.run_polling()

if __name__ == '__main__':
    main()
