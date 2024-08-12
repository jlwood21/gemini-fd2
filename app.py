import os
import csv
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import pandas as pd
import sqlite3

app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key="AIzaSyDMFDN6hqtDN9z8cLFGM7PzC6Z1Rx8Hn3Q")

# Setup the generation config
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS queries
                      (id INTEGER PRIMARY KEY, query TEXT, response TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS uploads
                      (id INTEGER PRIMARY KEY, filename TEXT, data BLOB)''')
    conn.commit()
    conn.close()

init_db()

# Parse and structure the CSV data
def parse_csv(file):
    df = pd.read_csv(file)
    return df

# Generate the query with context
def generate_query_with_context(df, user_query):
    context_data = df.to_dict(orient='records')
    prompt = f"{user_query}\n\nHere is your financial data:\n{context_data}\n"
    return prompt

# Get a response from the Gemini API
def get_ai_response(api_key, prompt):
    genai.configure(api_key=api_key)
    response = genai.generate_content(prompt=prompt)
    return response['candidates'][0]['content']['parts'][0]['text']

# Save query and response to database
def save_response(query, response):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO queries (query, response) VALUES (?, ?)", (query, response))
    conn.commit()
    conn.close()

# Route to handle the root URL
@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""

    if request.method == "POST":
        try:
            user_query = request.form['question']
            csv_file = request.files['file']

            if csv_file:
                # Parse the CSV file
                df = parse_csv(csv_file)
                
                # Generate the prompt with context
                prompt = generate_query_with_context(df, user_query)
                
                # Get AI response
                api_key = "AIzaSyDMFDN6hqtDN9z8cLFGM7PzC6Z1Rx8Hn3Q"  # Use your actual API key
                response_text = get_ai_response(api_key, prompt)
                
                # Save the response to the database
                save_response(user_query, response_text)

        except Exception as e:
            response_text = f"Error processing request: {e}"

    return render_template("index.html", response=response_text)

# Route to display saved queries and responses
@app.route("/history", methods=["GET"])
def history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries")
    rows = cursor.fetchall()
    conn.close()
    return render_template("history.html", rows=rows)

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
