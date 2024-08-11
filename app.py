import os
import csv
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import pandas as pd
import sqlite3

app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key="YOUR_API_KEY")

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

# Process CSV file and summarize data
def process_csv(filepath, query):
    df = pd.read_csv(filepath)

    if "spending" in query.lower() or "expenses" in query.lower():
        summary = df.groupby("Category")["Amount"].sum().reset_index()
        summary_text = "Summary of your spending:\n"
        for index, row in summary.iterrows():
            summary_text += f"- {row['Category']}: ${row['Amount']:.2f}\n"
        return summary_text

    return "No relevant data found."

# Save query and response to database
def save_response(query, response):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO queries (query, response) VALUES (?, ?)", (query, response))
    conn.commit()
    conn.close()

# Route to handle the financial query
@app.route("/nl_query_ui", methods=["GET", "POST"])
def nl_query_ui():
    response_text = ""

    if request.method == "POST":
        try:
            query = request.form["query"]
            csv_file = request.files["csv_file"]

            if csv_file:
                filepath = os.path.join("uploads", csv_file.filename)
                csv_file.save(filepath)

                csv_summary = process_csv(filepath, query)
                enhanced_query = f"The user uploaded financial data. {csv_summary} Based on this, the user asks: '{query}'. Please provide insights."

                history = [
                    {
                        "role": "user",
                        "parts": [
                            "You are a financial assistant. The user will ask questions about their spending habits based on the data provided. Analyze the data and provide accurate answers."
                        ],
                    },
                    {
                        "role": "model",
                        "parts": [
                            "I'm ready to assist with your financial analysis!"
                        ],
                    },
                ]

                chat_session = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                ).start_chat(history=history)

                response = chat_session.send_message(enhanced_query)
                response_text = response.text

                save_response(query, response_text)
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
