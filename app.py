from flask import Flask, request, jsonify, render_template, session
import google.generativeai as genai
import os
import re

# API Key Configuration
genai.configure(api_key="AIzaSyAy7C6aPlHFQFAKJ-fMmO2Ol3MGa98NGQ4")

# Restaurant Data & Bot Instructions
restaurant_menu = {
    "Starters": {
        "Chicken Seekh Kebab": {"price": "Rs. 600"},
        "Samosa Chaat": {"price": "Rs. 350"}
    },
    "Main Courses": {
        "Chicken Biryani": {"price": "Rs. 450"},
        "Mutton Karahi": {"price": "Rs. 1800"},
        "Beef Pulao": {"price": "Rs. 700"}
    },
    "Side Dishes": {
        "Dal Mash": {"price": "Rs. 300"},
        "Naan": {"price": "Rs. 50"},
        "Raita": {"price": "Rs. 80"}
    },
    "Beverages": {
        "Cold Drink": {"price": "Rs. 120"},
        "Lassi": {"price": "Rs. 150"}
    }
}

system_prompt = f"""
You are a friendly and helpful food bot for a Pakistani restaurant named "Desi Bites". Your primary purpose is to assist customers with their food orders, answer questions about the menu, and provide information on prices.

### Menu
{restaurant_menu}

### Restaurant Information
- **Location:** Model Town, Gujranwala
- **Delivery Area:** Only within Gujranwala
- **Delivery Charges:** Rs. 200 (flat rate)
- **Delivery Time:** 40-50 minutes max

### Instructions for You:
1.  **Menu & Prices:** When a user asks about the menu, show them a clear, categorized list. When they ask for a price, provide the exact amount from the menu in PKR.
2.  **Delivery & Charges:** Politely confirm the delivery charges and the area.
3.  **Ordering Flow:** If a user wants to order, start by asking for their name, then their phone number, and finally their address. Only after all three details are provided should you confirm the order.
4.  **Delivery Time:** When confirming an order, state the delivery time as 40-50 minutes.
5.  **Out-of-Topic Questions:** If a user asks a question not related to food or the restaurant, answer their question politely and then gently guide the conversation back to the restaurant by asking, "Is there anything I can help you with from our delicious menu?"
6.  **Natural Language:** Respond in a conversational and natural tone, understanding the user's intent.
7.  **Address Confirmation:** If a user provides an address outside of Gujranwala, kindly inform them that delivery is not available in that area.
"""

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key_here'

@app.route("/")
def index():
    session['history'] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    
    try:
        model = genai.GenerativeModel(
            model_name="gemma-3-12b-it"
        )
        
        history_from_session = session.get('history', [])
        
        history_for_api = []
        if not history_from_session:
            history_for_api.append({'role': 'user', 'parts': [{'text': system_prompt}]})
            history_for_api.append({'role': 'model', 'parts': [{'text': "Welcome to Desi Bites! How can I help you today?"}]})
        else:
            history_for_api = history_from_session

        chat_session = model.start_chat(history=history_for_api)
        
        response = chat_session.send_message(user_message)

        new_history = [{'role': m.role, 'parts': [{'text': p.text} for p in m.parts]} for m in chat_session.history]
        session['history'] = new_history
        
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, a server error occurred. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True)