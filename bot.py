import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token (replace with your Telegram bot token)
API_TOKEN = 'YOUR_BOT_API_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Set up SQLAlchemy for database storage
engine = create_engine('sqlite:///bot_database.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class UserWallet(Base):
    __tablename__ = 'user_wallets'
    user_id = Column(Integer, primary_key=True)
    wallet_address = Column(String)
    meme_coins = Column(JSON)

Base.metadata.create_all(engine)

# Function to get user wallet from DB
def get_user_wallet(user_id):
    session = Session()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()
    session.close()
    return wallet

# Function to save user wallet to DB
def save_user_wallet(user_id, wallet_address, meme_coins):
    session = Session()
    wallet = UserWallet(user_id=user_id, wallet_address=wallet_address, meme_coins=meme_coins)
    session.add(wallet)
    session.commit()
    session.close()

# Welcome message
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    welcome_text = (
        "Welcome to the Telegram Mini-App!\n\n"
        "Please create your Solana wallet to proceed.\n"
        "Click the button below to create your wallet."
    )
    create_wallet_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Create Wallet", callback_data="create_wallet")
    )
    await message.answer(welcome_text, reply_markup=create_wallet_button)

@dp.callback_query_handler(lambda c: c.data == 'create_wallet')
async def create_wallet(callback_query: types.CallbackQuery):
    wallet_address = "solana_" + callback_query.from_user.username
    meme_coins = {}  # Empty wallet to start with
    save_user_wallet(callback_query.from_user.id, wallet_address, meme_coins)
    await bot.answer_callback_query(callback_query.id, "Wallet created successfully!")
    await bot.send_message(
        callback_query.from_user.id,
        f"Your Solana wallet has been created: {wallet_address}\n\n"
        "Navigate to the main menu to explore the features.",
        reply_markup=main_menu_buttons()
    )

def main_menu_buttons():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("🛒 Trade Meme Coins"))
    menu.add(KeyboardButton("🔄 Swap Coins"))
    menu.add(KeyboardButton("📈 Market Data"))
    menu.add(KeyboardButton("💼 My Wallet"))
    return menu

@dp.message_handler(lambda message: message.text == "🛒 Trade Meme Coins")
async def trade_page(message: types.Message):
    trade_text = (
        "Welcome to the Meme Coin Trading Page!\n\n"
        "1. Buy SHIBA - $10 per 1,000 tokens\n"
        "2. Sell SHIBA - $8 per 1,000 tokens\n\n"
        "Use the buttons below to trade."
    )
    trade_buttons = InlineKeyboardMarkup()
    trade_buttons.add(InlineKeyboardButton("Buy SHIBA", callback_data="buy_shiba"))
    trade_buttons.add(InlineKeyboardButton("Sell SHIBA", callback_data="sell_shiba"))
    await message.answer(trade_text, reply_markup=trade_buttons)

@dp.callback_query_handler(lambda c: c.data in ["buy_shiba", "sell_shiba"])
async def trade_action(callback_query: types.CallbackQuery):
    action = "buy" if "buy" in callback_query.data else "sell"
    if action == "buy":
        await bot.send_message(
            callback_query.from_user.id,
            "Please send payment via CashApp ($YourCashAppID) or PayPal (paypal.me/YourPayPalID)."
        )
    else:
        await bot.send_message(
            callback_query.from_user.id,
            "Enter the amount of SHIBA you want to sell. Example: SELL 1000"
        )

@dp.message_handler(lambda message: message.text.startswith("SELL"))
async def sell_shiba(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        wallet = get_user_wallet(message.from_user.id)
        if wallet and wallet.meme_coins.get("SHIBA", 0) >= amount:
            wallet.meme_coins["SHIBA"] -= amount
            save_user_wallet(wallet.user_id, wallet.wallet_address, wallet.meme_coins)
            await message.answer(f"You sold {amount} SHIBA for ${(amount / 1000) * 8}.")
        else:
            await message.answer("Insufficient SHIBA balance.")
    except Exception as e:
        logger.error(f"Error processing sell_shiba: {e}")
        await message.answer("Invalid sell command. Please try again.")

@dp.message_handler(lambda message: message.text == "🔄 Swap Coins")
async def swap_coins(message: types.Message):
    swap_text = (
        "Welcome to the Swap Page!\n\n"
        "You can swap Solana for meme coins. Enter the amount and the token name, e.g.,:\n"
        "`SWAP 1 SOL to SHIBA`"
    )
    await message.answer(swap_text)

@dp.message_handler(lambda message: message.text.startswith("SWAP"))
async def process_swap(message: types.Message):
    try:
        _, amount, _, token = message.text.split()
        sol_amount = float(amount)
        wallet = get_user_wallet(message.from_user.id)
        if wallet:
            wallet.meme_coins[token] = wallet.meme_coins.get(token, 0) + sol_amount * 10
            save_user_wallet(wallet.user_id, wallet.wallet_address, wallet.meme_coins)
            await message.answer(f"Successfully swapped {sol_amount} SOL to {token}.")
    except Exception as e:
        logger.error(f"Error processing swap: {e}")
        await message.answer("Invalid swap command. Please try again.")

@dp.message_handler(lambda message: message.text == "📈 Market Data")
async def market_data(message: types.Message):
    dex_url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        response = requests.get(dex_url)
        if response.status_code == 200:
            market_info = response.json()["pairs"][:5]
            text = "Top 5 Market Data:\n\n"
            for pair in market_info:
                text += f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}: ${pair['priceUsd']}\n"
            await message.answer(text)
        else:
            await message.answer("Unable to fetch market data.")
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        await message.answer("Error fetching market data. Please try again later.")

@dp.message_handler(lambda message: message.text == "💼 My Wallet")
async def my_wallet(message: types.Message):
    try:
        wallet = get_user_wallet(message.from_user.id)
        if not wallet:
            await message.answer("No wallet found. Please create one first.")
        else:
            coins = wallet.meme_coins
            text = f"Your Wallet Address: {wallet.wallet_address}\n\n"
            text += "Meme Coins:\n"
            for coin, amount in coins.items():
                text += f"- {coin}: {amount} coins\n"
            await message.answer(text)
    except Exception as e:
        logger.error(f"Error fetching wallet data: {e}")
        await message.answer("Error fetching wallet. Please try again later.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
