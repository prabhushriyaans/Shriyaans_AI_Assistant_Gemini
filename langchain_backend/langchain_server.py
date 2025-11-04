from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

# Load environment variables
load_dotenv(override=True)

# Initialize Google Gemini client with web search
genai_api_key = os.getenv("GEMINI_API_KEY")
if not genai_api_key:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

try:
    generation_config = types.GenerationConfig(
        temperature=0.7,
        top_k=40,
        top_p=0.9,
        web_search_enabled=True,  # Enable web search
    )

    client = genai.Client(api_key=genai_api_key)
    chat = client.chats.create(
        model="gemini-pro",
        config=generation_config
    )
    print("✅ Chat model initialized successfully with web search")
except Exception as e:
    raise RuntimeError(f"Error initializing chat: {e}")

# Add keyword detection for search triggers
SEARCH_TRIGGERS = [
    "latest", "current", "recent", "new", "2024", "2025",
    "upcoming", "deadline", "announcement", "changes",
    "this year", "next year", "updates"
]

@app.route('/chat', methods=['POST'])
def unified_chat():
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Check if the query needs web search
        needs_search = any(trigger in user_input.lower() for trigger in SEARCH_TRIGGERS)
        
        if needs_search:
            # Add search instruction to the prompt
            enhanced_input = f"Please search for the most current information to answer: {user_input}"
        else:
            enhanced_input = user_input

        # Send message with potential search instruction
        response = chat.send_message(enhanced_input)

        # Extract search metadata
        search_metadata = {}
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata
                if hasattr(metadata, 'web_search_queries'):
                    search_metadata = {
                        "web_search_used": True,
                        "search_queries": metadata.web_search_queries,
                        "search_triggered_by": "keyword_match" if needs_search else "model_decision"
                    }

        return jsonify({
            "response": response.text,
            "metadata": search_metadata
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005)