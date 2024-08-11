from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os
import requests

app = Flask(__name__)
DATABASE = 'database.db'
UPLOAD_FOLDER = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        response = process_query(query)
        return render_template('index.html', response=response)
    return render_template('index.html', response='')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    process_csv(filepath)
    return redirect(url_for('home'))

def process_csv(filepath):
    df = pd.read_csv(filepath)
    engine = create_engine(f'sqlite:///{DATABASE}')
    df.to_sql('transaction', con=engine, if_exists='replace', index=False)

def process_query(query):
    # Interact with the Gemini API
    api_key = "AIzaSyDMFDN6hqtDN9z8cLFGM7PzC6Z1Rx8Hn3Q"
    url = f"https://gemini.googleapis.com/v1/queries:analyze?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "query": query
    }
    
    # Make a request to the Gemini API
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        gemini_response = response.json()
        # Parse the response to find relevant data and return it
        transactions = get_relevant_transactions(gemini_response)
        total_spent = sum([t['amount'] for t in transactions])
        return {"total_spent": total_spent}
    else:
        return {"error": response.json()}

def get_relevant_transactions(gemini_response):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    
    # This assumes that the Gemini API gives some kind of tags or keywords
    # you can use to query the database. Here we're just demonstrating with
    # a hypothetical example:
    keyword = gemini_response.get('keyword', '')
    
    query = f"""
    SELECT amount FROM transaction
    WHERE description LIKE '%{keyword}%'
    """
    
    cur.execute(query)
    transactions = [{"amount": row[0]} for row in cur.fetchall()]
    conn.close()
    
    return transactions

if __name__ == '__main__':
    app.run(debug=True, port=5001)
