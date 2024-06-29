from flask import Flask, request, jsonify, render_template
import os
from langchain_huggingface import HuggingFaceEndpoint
from datetime import datetime
import json

app = Flask(__name__)

# Set your Hugging Face API token using environment variable for security
sec_key = "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"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = sec_key

# Repository ID for the model
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

# Initialize the HuggingFaceEndpoint
llm = HuggingFaceEndpoint(repo_id=repo_id, temperature=0.7)

# Common phrases dictionary with emojis
common_phrases = {
    "hi": "Hello! How can I assist you today? 👋",
    "name":"Hi! My name is Artificial Intelligence? 👋",
    "who are you?": "I am just your school bot",
    "what is your name": "Hi! My name is Artificial Intelligence? 👋",
    "fine": "Great to hear!",
    "hello": "Hi there! How can I help you? 👋",
    "hey": "Hey! What's up? 👋",
    "how are you": "Thank you for asking, I'm good. How about you? 😊",
    "howdy": "Howdy! What can I do for you? 🤠",
    "greetings": "Greetings! How can I assist? 🙌",
    "what's up": "Not much, just here to assist you! What can I help you with? 😊",
    "help me": "Sure, I'm here to help! What do you need assistance with? 🤔",
    "thank you": "You're welcome! If you have any other questions, feel free to ask. 😊",
    "thanks": "You're welcome! Let me know if there's anything else I can do for you. 😊",
    "bye": "Bye! Let me know if there's anything else I can do for you. 😊",
    "good bye": "Bye! Let me know if there's anything else I can do for you. 😊",
    "joke": "Why did the scarecrow win an award?\nBecause he was outstanding in his field!",
    "i got a good mark": "WOW! All the best 😊",
}

# File path to store conversation history
conversation_file = "conversation_history.json"

# Function to load conversation history from the JSON file
def load_conversation_history():
    try:
        with open(conversation_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save conversation history to the JSON file
def save_conversation_history(history):
    with open(conversation_file, "w") as file:
        json.dump(history, file, indent=4)

# Load conversation history
conversation_history = load_conversation_history()

# Function to handle time-related queries
def handle_time_query():
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"The current time is {current_time}"

# Function to ask questions to the LLM
def ask_question(question: str):
    try:
        response = llm.invoke(question, max_length=128)  # Set max_length here
        if any(keyword in question.lower() for keyword in ["program", "code", "script"]):
            # Extract and return only the code block from the response
            start = response.find("```")
            end = response.rfind("```")
            if start != -1 and end != -1:
                code_block = response[start+3:end].strip()
                return code_block
        return response
    except Exception as e:
        return str(e)

# Function to log conversation to a text file with UTF-8 encoding
def log_conversation(user_message, bot_response):
    with open("conversation_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"User: {user_message}\n")
        log_file.write(f"Bot: {bot_response}\n\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '').lower()
    
    if not question:
        return jsonify({"response": "Please provide a question."}), 400
    
    if question in common_phrases:
        response = common_phrases[question]
        log_conversation(question, response)
        return jsonify({"response": response})
    
    if question == 'bye':
        response = "Thank you! Have a great day. Goodbye! 👋"
        log_conversation(question, response)
        return jsonify({"response": response})
    
    elif question.startswith('sum'):
        try:
            _, a, b = question.split()
            a, b = int(a), int(b)
            sum_result = a + b
            response = f"Sum of {a} and {b} is: {sum_result}"
            log_conversation(question, response)
            return jsonify({"response": response})
        except ValueError:
            response = "Invalid input for sum. Please provide two integers."
            log_conversation(question, response)
            return jsonify({"response": response}), 400
    else:
        # Check if the question exists in conversation history
        if question in conversation_history:
            response = conversation_history[question]
            log_conversation(question, response)
            return jsonify({"response": response})
        else:
            try:
                response = ask_question(question)
                # Save new conversation to history
                conversation_history[question] = response
                save_conversation_history(conversation_history)
                log_conversation(question, response)
                return jsonify({"response": response})
            except Exception as e:
                response = f"Error: {str(e)}"
                log_conversation(question, response)
                return jsonify({"response": response}), 500

if __name__ == '__main__':
    app.run(debug=True)
