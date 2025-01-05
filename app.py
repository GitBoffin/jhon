import os
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Default route (home) which redirects to the welcome page
@app.route('/')
def home():
    # If user has already seen the welcome page, redirect to the market page
    if session.get('welcome_visited', False):
        return redirect(url_for('market'))  # Redirect to the market page
    return redirect(url_for('welcome'))  # Otherwise, show welcome page

# Welcome page route
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Market page route
@app.route('/market')
def market():
    return render_template('market.html')

# Other pages
@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/swap')
def swap():
    return render_template('swap.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

# Simulate wallet creation and session management
@app.route('/create_wallet')
def create_wallet():
    # Mark the user as having visited the welcome page
    session['welcome_visited'] = True
    return redirect(url_for('market'))  # Redirect to the market page after wallet creation

# Start Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT from Heroku or default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)  # Disable debug mode in production
