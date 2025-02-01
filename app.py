"""
openai==1.12.0
langchain==0.1.0
chainlit==1.0.0
python-dotenv==1.0.0
"""

# app.py
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

# Create a prompt template
prompt = ChatPromptTemplate.from_template(
    """You are a knowledeable and friendly financial wellness assistant for Sun Life.
    
    Question: {question}
    
    Please provide a clear and concise answer."""
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("content")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Run the chain
    response = chain.invoke({"question": user_message})
    
    return jsonify({"message": response["text"]})

if __name__ == "__main__":
    app.run(port=8000, debug=True)