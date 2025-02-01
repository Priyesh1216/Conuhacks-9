import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import chainlit as cl
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Define the initial questions for gathering user information
INITIAL_QUESTIONS = [
    "What is your current age and employment status?",
    "What are your primary financial goals (e.g., retirement savings, debt management, investment growth)?",
    "Do you currently have any insurance products or employee benefits?",
    "What is your risk tolerance for investments (conservative, moderate, or aggressive)?"
]

# Create a more comprehensive prompt template
prompt = ChatPromptTemplate.from_template(
    """You are a knowledgeable and friendly financial wellness assistant for Sun Life in Canada. Use the following information to provide personalized financial advice:

    User Profile:
    Age/Employment: {age_employment}
    Financial Goals: {financial_goals}
    Insurance/Benefits: {insurance_benefits}
    Risk Tolerance: {risk_tolerance}
    
    Additional Context: {additional_context}
    
    Current Question: {current_question}
    
    Please provide clear, actionable advice that:
    1. Considers Canadian tax laws and financial regulations
    2. References specific Sun Life products when relevant
    3. Emphasizes long-term financial wellness
    4. Includes both immediate steps and long-term strategies
    5. Mentions any relevant government programs or benefits
    
    Provide your response in a clear, friendly tone with specific recommendations."""
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt)

class UserSession:
    def __init__(self):
        self.current_question_index = 0
        self.user_responses = {
            "age_employment": "",
            "financial_goals": "",
            "insurance_benefits": "",
            "risk_tolerance": "",
        }
        self.has_completed_questions = False

# Store user sessions
sessions = {}

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("content")
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Initialize or get session
    if session_id not in sessions:
        sessions[session_id] = UserSession()
    
    session = sessions[session_id]
    
    # If we haven't completed the initial questions
    if not session.has_completed_questions:
        # Store the answer to the current question
        if session.current_question_index > 0:  # If not the first question
            current_question_key = list(session.user_responses.keys())[session.current_question_index - 1]
            session.user_responses[current_question_key] = user_message
        
        # If we have more questions to ask
        if session.current_question_index < len(INITIAL_QUESTIONS):
            response = {
                "message": INITIAL_QUESTIONS[session.current_question_index],
                "is_question": True,
                "question_number": session.current_question_index + 1
            }
            session.current_question_index += 1
            return jsonify(response)
        else:
            session.has_completed_questions = True
    
    # After completing questions or for subsequent interactions
    response = chain.invoke({
        "age_employment": session.user_responses["age_employment"],
        "financial_goals": session.user_responses["financial_goals"],
        "insurance_benefits": session.user_responses["insurance_benefits"],
        "risk_tolerance": session.user_responses["risk_tolerance"],
        "additional_context": "",
        "current_question": user_message
    })
    
    return jsonify({
        "message": response["text"],
        "is_question": False,
        "user_profile": session.user_responses  # Include user profile for context
    })

@app.route("/api/reset", methods=["POST"])
def reset_session():
    data = request.json
    session_id = data.get("session_id", "default")
    if session_id in sessions:
        del sessions[session_id]
    return jsonify({"message": "Session reset successfully"})

if __name__ == "__main__":
    app.run(port=8000, debug=True)