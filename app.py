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
    """You are a helpful assistant. Please respond to the following question:
    
    Question: {question}
    
    Please provide a clear and concise answer."""
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt)


@cl.on_chat_start
def start_chat():
    """Initialize the chat session"""
    cl.Message(
        content="Hello! I'm your AI assistant. How can I help you today?").send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""

    # Run the chain
    response = await chain.ainvoke(
        {"question": message.content}
    )

    # Send the response back to the user
    await cl.Message(content=response["text"]).send()
