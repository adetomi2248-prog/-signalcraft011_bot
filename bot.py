 import asyncio
import logging
import os
import random
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Configuration ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Data ---

QUOTES = [
    "💡 The only way to do great work is to love what you do. - Steve Jobs",
    "🚀 Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "💰 The stock market is filled with individuals who know the price of everything, but the value of nothing. - Peter Lynch",
    "📈 In investing, what is comfortable is rarely profitable. - Robert Arnott",
    "✨ Be fearful when others are greedy, and greedy when others are fearful. - Warren Buffett",
]

MEME_URLS = [
    "https://i.imgflip.com/1bij.jpg",
    "https://i.imgflip.com/30b1gx.jpg",
    "https://i.imgflip.com/26am.jpg",
    "https://i.imgflip.com/2kbn1e.jpg",
]

def get_crypto_prices():
    """Fetch crypto prices from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana,cardano",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        btc = data.get("bitcoin", {})
        eth = data.get("ethereum", {})
        sol = data.get("solana", {})
        ada = data.get("cardano", {})
        
        msg = f"📊 **Crypto Prices**\n"
        msg += f"🟠 BTC: ${btc.get('usd', 'N/A'):,.2f} ({btc.get('usd_24h_change', 0):.2f}%)\n"
        msg += f"🔷 ETH: ${eth.get('usd', 'N/A'):,.2f} ({eth.get('usd_24h_change', 0):.2f}%)\n"
        msg += f"🟣 SOL: ${sol.get('usd', 'N/A'):,.2f} ({sol.get('usd_24h_change', 0):.2f}%)\n"
        msg += f"🔴 ADA: ${ada.get('usd', 'N/A'):,.2f} ({ada.get('usd_24h_change', 0):.2f}%)\n"
        msg += f"\n🕐 {datetime.now().strftime('%H:%M:%S')}"
        return msg
    except Exception as e:
        logger.error(f"Crypto error: {e}")
        return "⚠️ Crypto prices unavailable"

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🤖 **SignalCraft Bot**
    
Commands:
/crypto - Crypto prices
/quote - Daily quote
/meme - Random meme
/help - Help"""
    await update.message.reply_text(msg, parse_mode='Markdown')

async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto_prices(), parse_mode='Markdown')

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(QUOTES))

async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(random.choice(MEME_URLS))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# --- Auto-posting ---

async def auto_crypto(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        try:
            await context.bot.send_message(chat_id=CHAT_ID, text=get_crypto_prices(), parse_mode='Markdown')
            logger.info("Auto crypto sent")
        except Exception as e:
            logger.error(f"Auto error: {e}")

async def auto_quote(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        try:
            await context.bot.send_message(chat_id=CHAT_ID, text=f"💡 **Daily Quote**\n\n{random.choice(QUOTES)}")
            logger.info("Auto quote sent")
        except Exception as e:
            logger.error(f"Auto error: {e}")

async def auto_meme(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        try:
            await context.bot.send_photo(chat_id=CHAT_ID, photo=random.choice(MEME_URLS), caption="😂 **Meme Time**")
            logger.info("Auto meme sent")
        except Exception as e:
            logger.error(f"Auto error: {e}")

# --- Main ---

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("crypto", crypto_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("meme", meme_command))
    
    # Schedule auto-posts
    app.job_queue.run_repeating(auto_crypto, interval=3600, first=30)    # Every hour
    app.job_queue.run_repeating(auto_quote, interval=7200, first=60)     # Every 2 hours
    app.job_queue.run_repeating(auto_meme, interval=14400, first=90)     # Every 4 hours
    
    logger.info("🚀 Bot started!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
