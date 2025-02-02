import React, { useEffect, useState, useRef } from "react";
import "./styles/Chat.css";
import { FaArrowUp, FaSyncAlt } from "react-icons/fa";
import logo from "./images/BankBud-Logo.png";
const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  useEffect(()=>{
    const fetchStartText = async () => {
        try{
            const response = await fetch("http://localhost:8000/", {
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
              }
        
              const data = await response.json();
              setMessages([{ text: data.message, sender: "bot" }]);
        } catch(error){
            console.error("Error:", error);
        }
    };
    fetchStartText();
  }, []);

  useEffect(() => {
    // Scroll to the bottom whenever messages update
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    try {
      setIsLoading(true);
      setMessages(prev => [...prev, { text: input, sender: "user" }]);
      
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: input }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { text: data.message, sender: "bot" }]);
      setInput("");
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { 
        text: "Sorry, there was an error processing your message.", 
        sender: "bot",
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetSession = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: "default" }),
      });
      const data = await response.json();
      setMessages([{ text: data.message, sender: "bot" }, {text: "Hello! I am your AI financial advisor! Let's start with some questions that will help me understand your situation. Type OK to continue", sender: "bot"}]);
    } catch (error) {
      console.error("Error:", error);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <header><button className="refresh-button" onClick={resetSession}>
          <FaSyncAlt />
        </button><img id="logo" src={logo} alt="BankBud Logo"></img></header>
      <div className="messages-area">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
          >
            <div className={`message-bubble ${msg.error ? "error-message" : ""}`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef}></div>
      </div>
      
      <div className="input-area">
        <input
          className="message-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button
          className={`send-button ${isLoading ? "loading" : ""}`}
          onClick={sendMessage}
          disabled={isLoading}
        >
            <FaArrowUp />
        </button>
      </div>
    </div>
  );
};

export default Chat;