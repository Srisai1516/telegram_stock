import logging
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you got from BotFather
TELEGRAM_BOT_TOKEN = '8115686485:AAEcF3J7xJCBUWOhaXi2NK4A_e3zUc29p-c'

# Enable logging to see errors and bot activity
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# =============================================================================
# === Bot Command Handlers ====================================================
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the Stock Price Bot.\n\n"
        "Just send me any stock symbol to get detailed price information.\n\n"
        "Use /help to see all available commands and examples."
    )
    await update.message.reply_html(welcome_message)

# --- STEP 2: REPLACE YOUR HELP_COMMAND FUNCTION ---

# --- REPLACE THIS FUNCTION IN YOUR SCRIPT ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message with all features, with corrected HTML parsing."""
    help_text = (
        "<b>How to use this bot:</b>\n\n"
        "➡️ Simply type a symbol to get the latest price data.\n\n"
        "<b><u>Main Commands:</u></b>\n"
        " • <code>/news SYMBOL</code> - Get the latest news.\n"
        "   (e.g., <code>/news GOOGL</code>)\n\n"
        "<b><u>Alert Commands:</u></b>\n"
        # The < and > are replaced with &lt; and &gt; to prevent HTML errors
        " • <code>/alert SYMBOL &gt; PRICE</code>\n"
        " • <code>/alert SYMBOL &lt; PRICE</code>\n"
        " • <code>/myalerts</code> - View your active alerts.\n"
        " • <code>/delalert INDEX</code> - Delete an alert.\n\n"
        "<b><u>Examples for Price Checks:</u></b>\n"
        " • <b>Stocks:</b> <code>AAPL</code>, <code>RELIANCE.NS</code>\n"
        " • <b>Forex:</b> <code>EURUSD=X</code>, <code>USDINR=X</code>\n"
        " • <b>Commodities:</b> <code>GC=F</code>, <code>CL=F</code>\n"
        " • <b>Crypto:</b> <code>BTC-USD</code>, <code>ETH-USD</code>"
    )
    await update.message.reply_html(help_text)
'''async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message with expanded examples."""
    help_text = (
        "<b>How to use this bot:</b>\n\n"
        "➡️ Simply type a symbol and send it to get the latest price data.\n\n"
        "<b><u>Examples:</u></b>\n"
        " • <b>US Stocks:</b> <code>AAPL</code>, <code>GOOGL</code>\n"
        " • <b>Indian Stocks:</b> <code>RELIANCE.NS</code>\n"
        " • <b>Commodities:</b> <code>GC=F</code> (Gold), <code>CL=F</code> (Oil)\n"
        " • <b>Crypto:</b> <code>BTC-USD</code>, <code>ETH-USD</code>\n\n"
        "<b><u>Alert Commands:</u></b>\n"
        " • <code>/alert SYMBOL > PRICE</code>\n"
        "   (e.g., <code>/alert TSLA > 300</code>)\n"
        " • <code>/alert SYMBOL < PRICE</code>\n"
        "   (e.g., <code>/alert MSFT < 400</code>)\n"
        " • <code>/myalerts</code> - View your active alerts.\n"
        " • <code>/delalert INDEX</code> - Delete an alert by its number."
    )
    await update.message.reply_html(help_text)'''

async def get_stock_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch rich asset data, including daily and 52-week ranges."""
    symbol = update.message.text.upper()
    chat_id = update.effective_chat.id
    
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="2d")
        
        if hist.empty or not info:
             raise ValueError("Data not available for this symbol.")

        price = hist['Close'].iloc[-1]
        volume = hist['Volume'].iloc[-1]
        
        asset_name = info.get('longName') or info.get('shortName', symbol)
        currency = info.get('currency', 'USD')
        open_price = info.get('open', 0)
        day_low = info.get('dayLow', 0)
        day_high = info.get('dayHigh', 0)
        wk_52_low = info.get('fiftyTwoWeekLow', 0)
        wk_52_high = info.get('fiftyTwoWeekHigh', 0)

        response = f"<b>{asset_name} ({symbol})</b>\n"
        response += f"---------------------------------------\n"
        response += f"<b>Price:</b>   <code>{price:,.2f} {currency}</code>\n"
        response += f"<b>Open:</b>    <code>{open_price:,.2f}</code>\n"
        response += f"<b>Day Range:</b> <code>{day_low:,.2f} - {day_high:,.2f}</code>\n"
        response += f"<b>52wk Range:</b> <code>{wk_52_low:,.2f} - {wk_52_high:,.2f}</code>\n"
        response += f"<b>Volume:</b>  <code>{volume:,}</code>\n"

        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            change = price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            change_symbol = "🟢" if change >= 0 else "🔴"
            response += f"<b>Change:</b>  <code>{change_symbol} {change:,.2f} ({change_percent:,.2f}%)</code>\n"
            
            prev_volume = hist['Volume'].iloc[-2]
            if prev_volume > 0:
                volume_change = volume - prev_volume
                volume_change_percent = (volume_change / prev_volume) * 100
                vol_change_symbol = "🟢" if volume_change >= 0 else "🔴"
                response += f"<b>Vol Change:</b> <code>{vol_change_symbol} {volume_change:,} ({volume_change_percent:,.2f}%)</code>"

        await update.message.reply_html(response)

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        await update.message.reply_text(
            f"Sorry, I couldn't find any data for the symbol '{symbol}'."
        )

# =============================================================================
# === Alert System Functions ==================================================
# =============================================================================

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets a price alert for a stock."""
    if 'alerts' not in context.bot_data:
        context.bot_data['alerts'] = []

    try:
        parts = context.args
        if len(parts) != 3:
            await update.message.reply_text("❌ <b>Invalid format.</b>\nPlease use: <code>/alert SYMBOL > PRICE</code> or <code>/alert SYMBOL < PRICE</code>\n<i>Example:</i> <code>/alert TSLA > 300</code>", parse_mode=ParseMode.HTML)
            return

        symbol = parts[0].upper()
        condition = parts[1]
        price = float(parts[2])

        if condition not in ['>', '<']:
            await update.message.reply_text("❌ <b>Invalid condition.</b> Please use <code>></code> (greater than) or <code><</code> (less than).", parse_mode=ParseMode.HTML)
            return

        context.bot_data['alerts'].append({
            'chat_id': update.effective_chat.id, 'user_id': update.effective_user.id,
            'symbol': symbol, 'condition': condition, 'price': price
        })
        
        await update.message.reply_text(f"✅ <b>Alert set!</b>\nI will notify you if <code>{symbol}</code> goes {'above' if condition == '>' else 'below'} <code>{price}</code>.", parse_mode=ParseMode.HTML)

    except (IndexError, ValueError):
        await update.message.reply_text("❌ <b>Invalid format.</b>\nPlease use: <code>/alert SYMBOL > PRICE</code>\n<i>Example:</i> <code>/alert RELIANCE.NS < 2800</code>", parse_mode=ParseMode.HTML)


async def my_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists the user's active alerts."""
    user_id = update.effective_user.id
    if 'alerts' not in context.bot_data or not any(a['user_id'] == user_id for a in context.bot_data['alerts']):
        await update.message.reply_text("You have no active alerts. Set one with <code>/alert</code>.", parse_mode=ParseMode.HTML)
        return

    response = "🔔 <b>Your Active Alerts:</b>\n\n"
    user_alerts_with_indices = [(i, alert) for i, alert in enumerate(context.bot_data['alerts']) if alert['user_id'] == user_id]

    for user_index, (original_index, alert) in enumerate(user_alerts_with_indices, 1):
        condition_text = "goes above" if alert['condition'] == '>' else "drops below"
        response += f" <code>{user_index}</code>: <code>{alert['symbol']}</code> {condition_text} <code>{alert['price']}</code>\n"

    response += "\nTo delete an alert, use <code>/delalert INDEX</code> (e.g., <code>/delalert 1</code>)"
    await update.message.reply_html(response)


async def delete_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes a specific alert for a user by its user-facing index."""
    user_id = update.effective_user.id
    try:
        alert_num_to_delete = int(context.args[0])
        user_alerts_indices = [i for i, alert in enumerate(context.bot_data.get('alerts', [])) if alert['user_id'] == user_id]

        if 1 <= alert_num_to_delete <= len(user_alerts_indices):
            original_index = user_alerts_indices[alert_num_to_delete - 1]
            deleted_alert = context.bot_data['alerts'].pop(original_index)
            await update.message.reply_html(f"✅ Alert for <code>{deleted_alert['symbol']}</code> has been deleted.")
        else:
            await update.message.reply_html("❌ Invalid alert number. Use <code>/myalerts</code> to see the correct numbers.")

    except (IndexError, ValueError):
        await update.message.reply_html("❌ Please provide the alert number to delete.\n<i>Example:</i> <code>/delalert 1</code>")

# =============================================================================
# === Background Job for Alerts ===============================================
# =============================================================================

async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    """The background job that periodically checks all active alerts."""
    if 'alerts' not in context.bot_data or not context.bot_data['alerts']:
        return

    alerts_to_check = context.bot_data['alerts'][:]
    triggered_indices = []

    for i, alert in enumerate(alerts_to_check):
        try:
            stock = yf.Ticker(alert['symbol'])
            current_price = stock.info.get('regularMarketPrice') or stock.history('1d')['Close'].iloc[-1]
            
            if not current_price: continue

            condition_met = (alert['condition'] == '>' and current_price > alert['price']) or \
                            (alert['condition'] == '<' and current_price < alert['price'])
            
            if condition_met:
                text = f"🚨 <b>Price Alert Triggered!</b> 🚨\n\n<code>{alert['symbol']}</code> has reached your target price of <code>{alert['price']}</code>.\n<i>Current Price:</i> <code>{current_price:,.2f}</code>"
                await context.bot.send_message(chat_id=alert['chat_id'], text=text, parse_mode=ParseMode.HTML)
                triggered_indices.append(i)

        except Exception as e:
            logger.error(f"Could not check alert for {alert['symbol']}: {e}")
    
    for i in sorted(triggered_indices, reverse=True):
        del context.bot_data['alerts'][i]

# --- STEP 1: ADD THIS NEW FUNCTION TO YOUR SCRIPT ---

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches the latest news for a given stock symbol."""
    try:
        # Check if the user provided a symbol
        if not context.args:
            await update.message.reply_html("Please provide a stock symbol. \n<i>Example:</i> <code>/news AAPL</code>")
            return

        symbol = context.args[0].upper()
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        stock = yf.Ticker(symbol)
        news = stock.news

        # Check if the news list is empty
        if not news:
            await update.message.reply_html(f"Couldn't find any recent news for <code>{symbol}</code>.")
            return

        # Get the company name for a nicer header
        asset_name = stock.info.get('longName') or stock.info.get('shortName', symbol)

        response = f"📰 <b>Latest News for {asset_name} ({symbol})</b>\n\n"
        
        # Format the top 5 articles
        for i, article in enumerate(news[:5]):
            title = article['title']
            publisher = article['publisher']
            link = article['link']
            # Create a hyperlink using Telegram's HTML formatting
            response += f"{i+1}. <a href='{link}'>{title}</a>\n     - <i>{publisher}</i>\n\n"
        
        # Send the message with link previews disabled for a cleaner look
        await update.message.reply_html(response, disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Error in /news for {context.args[0]}: {e}")
        await update.message.reply_html("Sorry, an error occurred. That symbol might not be valid.")

# =============================================================================
# === Main Function to Run the Bot ============================================
# =============================================================================

def main() -> None:
    """Start the bot and the alert-checking job."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(check_alerts, interval=300, first=10) # Checks every 5 minutes

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", get_news)) # <-- NEW LINE
    application.add_handler(CommandHandler("alert", set_alert))
    application.add_handler(CommandHandler("myalerts", my_alerts))
    application.add_handler(CommandHandler("delalert", delete_alert))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_stock_price))
    
    print("Bot is running with alert checking enabled...")
    application.run_polling()


if __name__ == '__main__':
    main()
