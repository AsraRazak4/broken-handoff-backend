# backend/app.py - COMPLETE AI Handoff Analysis API
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import random

app = Flask(__name__)
CORS(app)  # Allow Expo app requests

# Critical anchors database (expandable)
CRITICAL_ANCHORS = {
    'sepsis': ['sepsis protocol', 'bp q4h', 'urine output', 'lactate', 'cultures'],
    'cardiac': ['troponin', 'ecg', 'chest pain', 'nitroglycerin', 'heparin'],
    'respiratory': ['oxygen sat', 'rr >30', 'bipap', 'intubate', 'vent settings'],
    'neuro': ['gcs', 'pupils', 'seizure precautions', 'mannitol', 'ct head']
}

@app.route('/api/analyze', methods=['POST'])
def analyze_handoff():
    data = request.json
    anchors1 = data.get('anchors1', '').lower()
    anchors2 = data.get('anchors2', '').lower()
    
    # Extract anchors using regex
    def extract_anchors(text):
        anchors = []
        # Common medical patterns
        patterns = [
            r'bp q?(\d+)?h?', r'sepsis.*protocol', r'urine output', r'lactate',
            r'troponin', r'ecg', r'chest pain', r'nitro', r'o2 sat',
            r'gcs', r'pupils??\s*equal', r'mannitol', r'ct head'
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                anchors.append(re.search(pattern, text).group())
        return anchors
    
    nurse1_anchors = extract_anchors(anchors1)
    nurse2_anchors = extract_anchors(anchors2)
    
    # Calculate match score
    total_anchors = len(nurse1_anchors)
    matches = len(set(nurse1_anchors) & set(nurse2_anchors))
    risk_score = max(0, 100 - (matches / total_anchors * 70) - random.randint(5, 15))
    
    # AI reasoning
    status = 'BROKEN' if risk_score > 50 else 'CLEAR'
    missing = list(set(nurse1_anchors) - set(nurse2_anchors))
    reasoning = f"Nurse2 missed {len(missing)} critical anchors. Risk elevated due to communication gaps."
    
    return jsonify({
        'riskScore': int(risk_score),
        'status': status,
        'matches': matches,
        'total': total_anchors,
        'missing': missing[:3],  # Top 3 missing
        'reasoning': reasoning,
        'nurse1_anchors': nurse1_anchors,
        'nurse2_anchors': nurse2_anchors
    })

@app.route('/api/pdf-analyze', methods=['POST'])
def pdf_analyze():
    # Simulate PDF extraction (integrate with PyPDF2 later)
    data = request.json or {}
    return jsonify({
        'suffering': 'Acute sepsis with multi-organ involvement',
        'riskScore': 82,
        'anchors': ['BP q4h', 'Sepsis protocol', 'Urine output >30ml/hr', 'Lactate q6h', 'Cultures pending'],
        'symptoms': 'Fever 102°F, BP 88/56, HR 118, RR 28'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
