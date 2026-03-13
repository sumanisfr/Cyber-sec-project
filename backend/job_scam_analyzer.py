import re


RED_FLAGS = [
    (
        'Requests money or upfront payment',
        'Scammers often ask for training fees, equipment deposits, or processing charges before hiring.',
        30,
        re.compile(r'\b(training fee|registration fee|security deposit|pay upfront|send money|processing fee)\b', re.I),
    ),
    (
        'Suspicious payment or banking request',
        'Legitimate employers do not ask for your bank login, OTP, or cryptocurrency transfers during hiring.',
        25,
        re.compile(r'\b(bank account|otp|wire transfer|crypto|bitcoin|gift card|upi)\b', re.I),
    ),
    (
        'Too-good-to-be-true compensation',
        'Extremely high pay for little experience is a common bait tactic.',
        15,
        re.compile(r'\b(earn \$?\d{3,} per day|no experience required|guaranteed income|easy money|instant joining)\b', re.I),
    ),
    (
        'Pressure tactics or urgency',
        'Scam posts often pressure candidates to act immediately without normal screening.',
        10,
        re.compile(r'\b(urgent response|reply immediately|limited seats|immediate payment|today only)\b', re.I),
    ),
    (
        'Unprofessional recruiter contact',
        'Vague recruiter identity, personal messaging apps, or unclear company details increase risk.',
        10,
        re.compile(r'\b(whatsapp only|telegram only|gmail\.com|yahoo\.com|no interview|direct selection)\b', re.I),
    ),
]

SAFE_SIGNALS = [
    ('Clear company identification', 8, re.compile(r'\b(company website|headquarters|official career page|linkedin company)\b', re.I)),
    ('Normal interview process', 8, re.compile(r'\b(screening call|technical interview|panel interview|background check)\b', re.I)),
    ('No payment mentioned', 4, re.compile(r'\b(no fee|never ask for payment|free application)\b', re.I)),
]


def analyze_job_text(content: str):
    text = (content or '').strip()
    if not text:
        return {
            'risk_level': 'Unknown',
            'score': 0,
            'red_flags': [],
            'safe_signals': [],
            'verdict': 'Add the job description or recruiter message to analyze it.',
            'recommendations': [],
        }

    score = 0
    red_flags = []
    safe_signals = []

    for label, explanation, weight, pattern in RED_FLAGS:
        if pattern.search(text):
            score += weight
            red_flags.append({'title': label, 'explanation': explanation, 'weight': weight})

    for label, weight, pattern in SAFE_SIGNALS:
        if pattern.search(text):
            score = max(0, score - weight)
            safe_signals.append({'title': label, 'weight': weight})

    score = min(score, 100)
    if score >= 55:
        risk_level = 'High'
        verdict = 'This job post shows multiple scam patterns. Verify independently before sharing details or money.'
    elif score >= 25:
        risk_level = 'Medium'
        verdict = 'This job post has warning signs. Treat it cautiously and verify the company outside the message.'
    else:
        risk_level = 'Low'
        verdict = 'No major scam patterns were detected, but you should still verify the employer and application channel.'

    recommendations = [
        'Verify the company on its official careers page or LinkedIn.',
        'Never pay for interviews, equipment, or onboarding.',
        'Do not share OTPs, bank credentials, or ID documents until the employer is verified.',
        'Ask for a written job description, company email domain, and interview schedule.',
    ]

    return {
        'risk_level': risk_level,
        'score': score,
        'red_flags': red_flags,
        'safe_signals': safe_signals,
        'verdict': verdict,
        'recommendations': recommendations,
    }
