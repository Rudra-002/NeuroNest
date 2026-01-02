def analyze_screening(data):
    score = 0
    observations = []

    # Neutral, observational rationale (NO diagnosis, NO emotional framing)
    rationale = {
        "q1": "Inconsistent response to name can influence shared attention and early social engagement.",
        "q2": "Reduced eye contact may affect non-verbal communication cues during interaction.",
        "q3": "Limited use of gestures can impact early communication and expression of needs.",
        "q4": "Repetitive behaviors are often monitored as part of developmental observation.",
        "q5": "Strong sensory reactions may influence comfort and interaction with the environment.",
        "q6": "Limited imaginative play can affect social role exploration and flexible thinking."
    }

    # Score calculation + observation collection
    for key, reason in rationale.items():
        if data.get(key) == 2:
            score += 2
            observations.append(reason)

    # Risk categorization (screening-level, not diagnostic)
    if score <= 3:
        risk = "Low"
    elif score <= 7:
        risk = "Moderate"
    else:
        risk = "High"

    # Calm, non-directive next steps
    next_steps = {
        "Low": [
            "Continue observing your child’s development during everyday activities.",
            "Encourage communication, play, and social interaction at a comfortable pace.",
            "If questions arise, discussing them with a pediatric professional can be helpful."
        ],
        "Moderate": [
            "Consider noting patterns or behaviors you observe over time.",
            "You may find it helpful to discuss these observations with a pediatric professional.",
            "Early conversations can provide clarity and reassurance."
        ],
        "High": [
            "Consider sharing these observations with a qualified healthcare or developmental professional.",
            "Early guidance can help families better understand and support their child’s needs.",
            "Seeking professional input does not imply a diagnosis, but can offer valuable insight."
        ]
    }

    return {
        "score": score,
        "riskLevel": risk,
        "observations": observations,
        "nextSteps": next_steps[risk],
        "disclaimer": (
            "This screening highlights patterns commonly monitored in early development. "
            "It does not provide a medical diagnosis."
        )
    }

