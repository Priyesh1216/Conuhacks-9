import React, { useState } from "react";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
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
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default Chat;