from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import os
import re

app = Flask(__name__)
CORS(app)

# 🔥 Medical Risk Keywords Database (AI Simulation Layer)
MEDICAL_RISKS = {
    "bp": "BP monitoring",
    "blood pressure": "BP monitoring",
    "sepsis": "Sepsis protocol",
    "chest pain": "Chest pain monitoring",
    "urine output": "Urine output tracking",
    "oxygen": "Oxygen monitoring",
    "spo2": "Oxygen monitoring",
    "glucose": "Glucose monitoring",
    "fever": "Fever monitoring",
    "infection": "Infection risk",
    "tachycardia": "Heart rate monitoring",
    "bradycardia": "Heart rate monitoring"
}

# Existing Handoff Analysis
@app.route('/api/analyze', methods=['POST'])
def analyze_handoff():
    data = request.json
    anchors1 = data.get('anchors1', '').lower().split(',')
    anchors2 = data.get('anchors2', '').lower().split(',')

    missing = [a.strip() for a in anchors1 if a.strip() and a.strip() not in anchors2]
    risk_score = min(100, 50 + len(missing) * 15)
    status = 'BROKEN' if risk_score > 70 else 'SAFE'

    return jsonify({
        'risk_score': risk_score,
        'status': status,
        'missing': missing,
        'reasoning': f"Nurse2 missed {len(missing)} critical anchors"
    })

# ✅ FREE AI-STYLE PDF Risk Extraction
@app.route('/api/pdf', methods=['POST'])
def pdf_analyze():
    try:
        file = request.files['pdf']
        text = ""

        with pdfplumber.open(file.stream) as pdf:
            for page in pdf.pages[:3]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text.lower() + "\n"

        if len(text) < 50:
            return jsonify({'error': 'No text found in PDF'})

        # 🔥 Intelligent Risk Extraction
        detected_risks = set()
        for keyword, label in MEDICAL_RISKS.items():
            if re.search(rf"\b{keyword}\b", text):
                detected_risks.add(label)

        if not detected_risks:
            detected_risks.add("General patient monitoring")

        return jsonify({
            'risks': ", ".join(detected_risks),
            'summary': f"Detected {len(detected_risks)} clinical risks requiring attention.",
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    return "Broken Handoff AI Backend Running"


if __name__ == '__main__':
    app.run(debug=True)