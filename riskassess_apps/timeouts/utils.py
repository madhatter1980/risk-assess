from .models import TimeoutQuestion

def create_default_questions(questionnaire):
    default_questions = [
        # Preparation & Readiness
        {
            "order": 1,
            "question_text": "Am I physically and mentally fit to perform this task safely?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
        {
            "order": 2,
            "question_text": "Am I qualified and competent to perform this task?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
        # Work Area & Environmental Conditions
        {
            "order": 3,
            "question_text": "Have I inspected the work area, is it clean and free of trip hazards?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },

        # Tools, Equipment & PPE
        {
            "order": 4,
            "question_text": "Have I inspected the necessary tools and equipment, and are they in good working order?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
        {
            "order": 5,
            "question_text": "Have all energy sources been properly identified and isolated?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
        {
            "order": 6,
            "question_text": "Do I have the correct PPE for the task?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },

        # Hazard Identification & Risk Control
        {
            "order": 7,
            "question_text": "Could this task expose me to line-of-fire hazards?",
            "question_type": "YN",
            "preferred_answer": "NO",
        },
        {
            "order": 8,
            "question_text": "Could I experience strains or sprains injury from lifting, pulling, pushing, or poor posture?",
            "question_type": "YN",
            "preferred_answer": "NO",
        },
        {
            "order": 9,
            "question_text": "Is there a risk of falling from heights?",
            "question_type": "YN",
            "preferred_answer": "NO",
        },
        {
            "order": 10,
            "question_text": "Am I at risk of exposure to hazardous substances, chemicals?",
            "question_type": "YN",
            "preferred_answer": "NO",
        },

        # Control Measures
        {
            "order": 11,
            "question_text": "Have I established all the necessary controls and do I have a clear plan in mind?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
        {
            "order": 12,
            "question_text": "Does this feel right?",
            "question_type": "YN",
            "preferred_answer": "YES",
        },
    ]

    for question in default_questions:
        TimeoutQuestion.objects.create(questionnaire=questionnaire, **question)
