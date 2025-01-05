from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize Flask app
app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///bot_database.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class UserWallet(Base):
    __tablename__ = 'user_wallets'
    user_id = Column(Integer, primary_key=True)
    wallet_address = Column(String)
    meme_coins = Column(JSON)

Base.metadata.create_all(engine)

# Helper function to get user wallet
def get_user_wallet(user_id):
    session = Session()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()
    session.close()
    return wallet

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/wallet/<int:user_id>")
def wallet(user_id):
    wallet = get_user_wallet(user_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    return jsonify({
        "user_id": wallet.user_id,
        "wallet_address": wallet.wallet_address,
        "meme_coins": wallet.meme_coins
    })

@app.route("/trade", methods=["POST"])
def trade():
    data = request.json
    user_id = data.get("user_id")
    action = data.get("action")  # "buy" or "sell"
    token = data.get("token")
    amount = data.get("amount")

    session = Session()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()

    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    if action == "buy":
        wallet.meme_coins[token] = wallet.meme_coins.get(token, 0) + amount
    elif action == "sell":
        if wallet.meme_coins.get(token, 0) < amount:
            return jsonify({"error": "Insufficient balance"}), 400
        wallet.meme_coins[token] -= amount
    else:
        return jsonify({"error": "Invalid action"}), 400

    session.commit()
    session.close()

    return jsonify({"message": "Trade completed successfully"})

@app.route("/market")
def market():
    # Example static data for market information (replace with real API calls)
    market_data = [
        {"pair": "SHIBA/USDT", "price": "0.00001234"},
        {"pair": "DOGE/USDT", "price": "0.12"},
        {"pair": "SOL/USDT", "price": "22.34"},
    ]
    return jsonify(market_data)

@app.route("/swap", methods=["POST"])
def swap():
    data = request.json
    user_id = data.get("user_id")
    sol_amount = data.get("sol_amount")
    token = data.get("token")

    session = Session()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()

    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    wallet.meme_coins[token] = wallet.meme_coins.get(token, 0) + sol_amount * 10
    session.commit()
    session.close()

    return jsonify({"message": f"Successfully swapped {sol_amount} SOL to {token}"})

if __name__ == "__main__":
    app.run(debug=True)
