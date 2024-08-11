import os
import csv
from flask import Flask, request, render_template
import google.generativeai as genai

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

@app.route("/nl_query_ui", methods=["GET", "POST"])
def nl_query_ui():
    response_text = ""
    
    if request.method == "POST":
        try:
            query = request.form["query"]
            csv_file = request.files["csv_file"]

            if csv_file:
                # Save the uploaded file
                filepath = os.path.join("uploads", csv_file.filename)
                csv_file.save(filepath)
                
                # Optionally, process the CSV data here
                # with open(filepath, newline='') as f:
                #     reader = csv.reader(f)
                #     for row in reader:
                #         # process the rows

            # Sending the query to the Gemini API
            history = [
                {
                    "role": "user",
                    "parts": [
                        "You are a financial assistant. The user will ask questions about their spending habits. Your job is to analyze the user's data and provide concise, accurate answers."
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Okay, I'm ready to assist you with your spending analysis!"
                    ],
                },
            ]

            chat_session = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            ).start_chat(history=history)

            response = chat_session.send_message(query)
            response_text = response.text
        except Exception as e:
            response_text = f"Error processing request: {e}"
    
    return render_template("index.html", response=response_text)

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
