from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
import pandas as pd

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database
db = SQLAlchemy(app)

# Define the Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_query = request.form['query']
        gemini_response = query_gemini_api(user_query)
        processed_response = process_gemini_response(user_query, gemini_response)
        return render_template('index.html', response=processed_response)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('home'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        process_uploaded_file(filepath)
        return redirect(url_for('home'))

def process_uploaded_file(filepath):
    # Assuming the uploaded file is a CSV with the following columns:
    # user_id, date, amount, category, description
    data = pd.read_csv(filepath)
    for _, row in data.iterrows():
        transaction = Transaction(
            user_id=row['user_id'],
            date=datetime.strptime(row['date'], '%Y-%m-%d'),
            amount=row['amount'],
            category=row['category'],
            description=row['description']
        )
        db.session.add(transaction)
    db.session.commit()

@app.route('/nl_query', methods=['POST'])
def handle_nl_query():
    try:
        user_query = request.json['query']
        gemini_response = query_gemini_api(user_query)
        processed_response = process_gemini_response(user_query, gemini_response)
        return jsonify(processed_response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def query_gemini_api(query):
    api_key = 'AIzaSyDMFDN6hqtDN9z8cLFGM7PzC6Z1Rx8Hn3Q'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    # Assuming Gemini API has an endpoint like this, update URL if needed
    response = requests.post('https://api.gemini.com/v1/query', json={'query': query}, headers=headers)
    return response.json()

def process_gemini_response(user_query, gemini_response):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    user_id = 1  # Using a fixed user_id for dummy data

    if gemini_response.get('intent') == 'spending_habits':
        summary = summarize_spending(user_id, start_date, end_date)
        return summary
    elif gemini_response.get('intent') == 'total_spent_on_food':
        last_week_start = datetime(2023, 8, 1)
        last_week_end = datetime(2023, 8, 7)
        total_spent = total_spent_on_category(user_id, 'Food Delivery', last_week_start, last_week_end)
        return {'total_spent': total_spent}
    elif gemini_response.get('intent') == 'total_savings':
        total_savings_amount = total_savings(user_id, start_date, end_date)
        return {'total_savings': total_savings_amount}
    elif gemini_response.get('intent') == 'total_spent_on_football_tickets':
        total_spent = total_spent_on_description(user_id, 'football', start_date, end_date)
        return {'total_spent': total_spent}
    else:
        return {"response": "No matching query type for: " + user_query}

def summarize_spending(user_id, start_date, end_date):
    transactions = Transaction.query.filter_by(user_id=user_id).filter(Transaction.date.between(start_date, end_date)).all()
    summary = {}
    for transaction in transactions:
        if transaction.category not in summary:
            summary[transaction.category] = 0
        summary[transaction.category] += transaction.amount
    return summary

def total_spent_on_category(user_id, category, start_date, end_date):
    transactions = Transaction.query.filter_by(user_id=user_id, category=category).filter(Transaction.date.between(start_date, end_date)).all()
    total_spent = sum(transaction.amount for transaction in transactions)
    return total_spent

def total_savings(user_id, start_date, end_date):
    transactions = Transaction.query.filter_by(user_id=user_id).filter(Transaction.date.between(start_date, end_date)).all()
    total_income = sum(transaction.amount for transaction in transactions if transaction.amount > 0)
    total_expense = sum(transaction.amount for transaction in transactions if transaction.amount < 0)
    total_savings_amount = total_income + total_expense
    return total_savings_amount

def total_spent_on_description(user_id, description_keyword, start_date, end_date):
    transactions = Transaction.query.filter_by(user_id=user_id).filter(Transaction.description.ilike(f'%{description_keyword}%')).filter(Transaction.date.between(start_date, end_date)).all()
    total_spent = sum(transaction.amount for transaction in transactions)
    return total_spent

if __name__ == '__main__':
    app.run(debug=True, port=5001)

