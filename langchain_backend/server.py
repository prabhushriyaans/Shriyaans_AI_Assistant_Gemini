from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Load and validate API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment variables")

# Simple model initialization
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

print("✅ Gemini initialized successfully")

# Enhanced educational context
EDUCATION_PROMPT = """
You are ScholarBot, an AI assistant dedicated to providing guidance on scholarships, study abroad programs, and educational news.
Your primary function is to help students and counselors with academic and career-related queries.

Areas of expertise:
1. Scholarships and Financial Aid
   - Application processes
   - Eligibility requirements
   - Deadlines and documentation

2. Study Abroad Programs
   - University selection
   - Application requirements
   - Visa procedures
   - Cost of living
   - Part-time work regulations

3. Career Guidance
   - Course selection
   - Career pathways
   - Job prospects
   - Resume building
   - Interview preparation

4. Latest Educational Updates
   - Policy changes
   - Application deadlines
   - New programs
   - Industry trends

Format your responses using markdown for better readability.
For any non-educational queries, politely redirect to relevant educational topics.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Simple direct generation
        prompt = f"{EDUCATION_PROMPT}\n\nUser: {message}\nScholarBot:"
        response = model.generate_content(prompt)
        
        return jsonify({
            "choices": [{
                "message": {
                    "content": response.text if response else "No response generated"
                }
            }]
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to get response"}), 500

def scrape_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)[:8000]
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

# Add endpoint for chat title generation
@app.route('/api/generate-title', methods=['POST'])
def generate_title():
    try:
        message = request.json.get('message', '')
        response = model.generate_content(f"Title (4 words max): {message}")
        return jsonify({"title": response.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005)