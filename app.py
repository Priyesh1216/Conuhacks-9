import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Initialize Language Model
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Question Templates and Constants
GOAL_CATEGORIES = {
    "1": "Budgeting & Expense Tracking",
    "2": "Debt Management",
    "3": "Retirement Planning",
    "4": "Insurance & Protection",
    "5": "Other Financial Goals"
}

GOAL_SPECIFIC_QUESTIONS = {
    "1": [  # Budgeting & Expense Tracking
        "What's your monthly income after tax?",
        "What are your major monthly expenses?",
        "Do you contribute to a TFSA or RRSP?",
        "How much do you typically save each month?",
        "Are you eligible for any government benefits?"
    ],
    "2": [  # Debt Management
        "What types of debt do you currently have?",
        "What are your total monthly debt payments?",
        "Have you considered debt consolidation?",
        "Are you aware of your credit score?",
        "Do you have any government student loans?"
    ],
    "3": [  # Retirement Planning
        "What do you plan to retire?",
        "Do you have a company pension plan?",
        "Are you maximizing your RRSP contributions?",
        "Are you aware of CPP and OAS benefits?",
        "Have you considered critical illness insurance?"
    ],
    "4": [  # Insurance
        "Do you have workplace benefits coverage?",
        "Do you have dependents to protect?",
        "Do you have mortgage insurance?",
        "What's your provincial health coverage?",
        "Have you considered long-term disability insurance?"
    ],
    "5": [  # Other
        "Please specify your financial goal:",
        "What's your timeline for this goal?",
        "What steps have you taken so far?",
        "Are you aware of any tax implications?",
        "Have you consulted a financial advisor?"
    ]
}

INITIAL_QUESTIONS = [
    "What is your current age and employment status? (e.g., '28, full-time employee in Ontario')",
    "What are your primary financial goals? Choose from:\n"
    "1. Budgeting & Expense Tracking\n2. Debt Management\n"
    "3. Retirement Planning\n4. Insurance & Protection\n5. Other (please specify)",
    "What is your risk tolerance for investments? Choose:\n"
    "🔵 Conservative (Focus on GICs, bonds)\n"
    "🟢 Moderate (Balanced mutual funds)\n"
    "🔴 Aggressive (Equity-focused investments)"
]

# Chain Prompts
profile_analysis_prompt = ChatPromptTemplate.from_template(
    """Analyze the following user financial profile and provide a summary:
    
    Age/Employment: {age_employment}
    Financial Goals: {financial_goals}
    Risk Tolerance: {risk_tolerance}
    Details: {goal_specific_details}
    
    Provide a concise profile summary focusing on key aspects of their financial situation.
    """
)

strategy_generation_prompt = ChatPromptTemplate.from_template(
    """Based on this profile summary, generate specific financial strategies:
    
    {profile_summary}
    
    Provide:
    1. Three key financial priorities with action items
    2. Investment strategy based on their risk tolerance
    3. Three immediate next steps
    
    With a few empty lines in between each section.
    """
)

recommendations_prompt = ChatPromptTemplate.from_template(
    """Using the profile and strategies, create comprehensive recommendations:
    
    Profile: {profile_summary}
    Strategies: {strategy_recommendations}
    
    Format the response as follows:

    PROFILE SUMMARY:
    [Insert profile summary]

    KEY FINANCIAL PRIORITIES:
    1. [First priority with specific action items]
    2. [Second priority with specific action items]
    3. [Third priority with specific action items]

    RECOMMENDED PRODUCTS:
    1. [Primary recommendation with explanation]
    2. [Secondary recommendation with explanation]
    3. [Additional relevant products/services]

    INVESTMENT STRATEGY:
    [Detailed investment recommendations]

    IMMEDIATE NEXT STEPS:
    1. [First action item]
    2. [Second action item]
    3. [Third action item]

    LONG-TERM RECOMMENDATIONS:
    [3-5 specific long-term strategies]

    ADDITIONAL CONSIDERATIONS:
    - [Tax implications]
    - [Insurance needs]
    - [Retirement planning]
    - [Emergency fund]
    
    Address the user directly and be specific to their situation. 
    """
)

# Initialize Chain Components
profile_chain = LLMChain(
    llm=llm,
    prompt=profile_analysis_prompt,
    output_key="profile_summary"
)

strategy_chain = LLMChain(
    llm=llm,
    prompt=strategy_generation_prompt,
    output_key="strategy_recommendations"
)

recommendations_chain = LLMChain(
    llm=llm,
    prompt=recommendations_prompt,
    output_key="final_recommendations"
)

# Create Sequential Chain
financial_advisor_chain = SequentialChain(
    chains=[profile_chain, strategy_chain, recommendations_chain],
    input_variables=["age_employment", "financial_goals",
                     "risk_tolerance", "goal_specific_details"],
    output_variables=["profile_summary",
                      "strategy_recommendations", "final_recommendations"]
)


class UserSession:
    def __init__(self):
        self.current_question_index = 0
        self.user_responses = {
            "age_employment": "",
            "financial_goals": "",
            "risk_tolerance": "",
            "goal_specific_details": {}
        }
        self.goal_specific_questions = []
        self.current_goal_question = 0
        self.has_completed_basic_questions = False
        self.has_completed_all_questions = False


sessions = {}


def format_goal_specific_details(details):
    """Format goal-specific details for the prompt"""
    formatted = []
    for key, value in details.items():
        question_num = int(key.replace('goal_q', ''))
        if question_num <= len(GOAL_SPECIFIC_QUESTIONS.get("1", [])):
            formatted.append(f"Q{question_num}: {value}")
    return "\n".join(formatted)


def generate_recommendations(session):
    """Generate comprehensive financial recommendations using the chain"""
    formatted_details = format_goal_specific_details(
        session.user_responses["goal_specific_details"]
    )

    goal_num = session.user_responses["financial_goals"][0]
    goal_category = GOAL_CATEGORIES.get(goal_num, "General Financial Planning")

    chain_response = financial_advisor_chain.invoke({
        "age_employment": session.user_responses["age_employment"],
        "financial_goals": goal_category,
        "risk_tolerance": session.user_responses["risk_tolerance"],
        "goal_specific_details": formatted_details
    })

    return chain_response["final_recommendations"]


def handle_basic_questions(session, user_message):
    """Process initial profile questions"""
    if session.current_question_index > 0:
        session.user_responses[list(session.user_responses.keys())[
            session.current_question_index - 1]] = user_message

        if session.current_question_index == 2:
            goal_number = user_message[0]
            session.goal_specific_questions = GOAL_SPECIFIC_QUESTIONS.get(
                goal_number, GOAL_SPECIFIC_QUESTIONS["5"])

    if session.current_question_index < len(INITIAL_QUESTIONS):
        response = {
            "message": INITIAL_QUESTIONS[session.current_question_index],
            "is_question": True
        }
        session.current_question_index += 1
        return jsonify(response)

    session.has_completed_basic_questions = True
    return handle_goal_questions(session, user_message)


def handle_goal_questions(session, user_message):
    """Process goal-specific questions and generate recommendations"""
    if session.current_goal_question > 0:
        session.user_responses["goal_specific_details"][
            f"goal_q{session.current_goal_question}"] = user_message

    if session.current_goal_question < len(session.goal_specific_questions):
        response = {
            "message": session.goal_specific_questions[session.current_goal_question],
            "is_question": True
        }
        session.current_goal_question += 1
        return jsonify(response)

    session.has_completed_all_questions = True
    recommendations = generate_recommendations(session)

    complete_response = (
        "Thank you for sharing your financial information! I've analyzed your situation "
        "and prepared the following personalized recommendations:\n\n"
        f"{recommendations}\n\n"
        "Feel free to ask any specific questions about these recommendations or request "
        "clarification about any financial terms used above."
    )

    return jsonify({
        "message": complete_response,
        "is_question": False,
        "user_profile": session.user_responses
    })

# API Routes


@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_message = data.get("content")
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        if session_id not in sessions:
            sessions[session_id] = UserSession()

        session = sessions[session_id]

        if not session.has_completed_basic_questions:
            return handle_basic_questions(session, user_message)

        if not session.has_completed_all_questions:
            return handle_goal_questions(session, user_message)

        chain_response = financial_advisor_chain.invoke({
            **session.user_responses,
            "current_question": user_message
        })

        return jsonify({
            "message": chain_response["final_recommendations"],
            "is_question": False,
            "user_profile": session.user_responses
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Reset user session"""
    try:
        data = request.json
        session_id = data.get("session_id", "default")
        if session_id in sessions:
            del sessions[session_id]
        return jsonify({"message": "Session reset successfully"})
    except Exception as e:
        return jsonify({"error": "Error resetting session", "details": str(e)}), 500


@app.route("/")
def start_chat():
    """Initialize chat session"""
    return jsonify({"message": "Welcome to your AI financial advisor! How can I help you today?"})


if __name__ == "__main__":
    app.run(port=8000, debug=True)
