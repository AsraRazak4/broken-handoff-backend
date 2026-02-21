from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
from openai import OpenAI
import os
import re

app = Flask(__name__)
CORS(app)  # Allow mobile app requests
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# Your OpenAI key (get free at openai.com)

# Existing /api/analyze endpoint
@app.route('/api/analyze', methods=['POST'])
def analyze_handoff():
    data = request.json
    anchors1 = data.get('anchors1', '').lower().split(',')
    anchors2 = data.get('anchors2', '').lower().split(',')
    
    critical = ['bp q4h', 'sepsis protocol', 'chest pain', 'urine output']
    missing = [a for a in anchors1 if a.strip() and a.strip() not in anchors2]
    
    risk_score = min(100, 50 + len(missing) * 20)
    status = 'BROKEN' if risk_score > 70 else 'SAFE'
    
    return jsonify({
        'risk_score': risk_score,
        'status': status,
        'missing': missing,
        'reasoning': f"Nurse2 missed {len(missing)} critical anchors"
    })

# ✅ NEW: Real PDF Summarizer
@app.route('/api/pdf', methods=['POST'])
def pdf_analyze():
    try:
        file = request.files['pdf']
        text = ""
        
        # Extract text from PDF
        with pdfplumber.open(file.stream) as pdf:
            for page in pdf.pages[:3]:  # First 3 pages
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if len(text) < 100:
            return jsonify({'error': 'No text found in PDF'})
        
        # AI summarize medical risks
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Extract handoff risks from this medical document. 
                Return ONLY comma-separated risks like: "BP q4h, sepsis protocol, chest pain".
                Document: {text[:8000]}"""
            }
        ],
        max_tokens=100
    )   

        risks = response.choices[0].message.content.strip().lower()
        
        return jsonify({
            'risks': risks,
            'extracted_text': text[:300] + '...' if len(text) > 300 else text,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
