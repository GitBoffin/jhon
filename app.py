from flask import Flask, render_template

app = Flask(__name__)

# Define the default route (home)
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for the market page
@app.route('/market')
def market():
    return render_template('market.html')

# Define routes for other pages
@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/swap')
def swap():
    return render_template('swap.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
