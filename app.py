from flask import Flask, request, render_template
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure the API key for Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Set up the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "You are a financial assistant. The user will ask questions about their spending habits, such as 'How much did I spend on groceries last month?' or 'What was my largest expense this year?'. Your job is to analyze the user's data and provide concise, accurate answers.",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Okay, I'm ready to assist you with your spending analysis! Please tell me what you'd like to know.",
            ],
        },
    ]
)

# Route to handle user queries
@app.route('/nl_query_ui', methods=['POST'])
def nl_query_ui():
    user_query = request.form['query']
    try:
        response = chat_session.send_message(user_query)
        return render_template('index.html', response=response.text)
    except Exception as e:
        return render_template('index.html', response=f"Error from API: {str(e)}")

# Index route
@app.route('/')
def index():
    return render_template('index.html', response="")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
