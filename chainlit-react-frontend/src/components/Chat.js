import React, { useState } from "react";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;

    const response = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: input }),
    });

    const data = await response.json();
    setMessages([...messages, { text: input, sender: "user" }, { text: data.message, sender: "bot" }]);
    setInput("");
  };

  return (
    <div>
      <div id="conversation">
        {messages.map((msg, i) => (
          <p key={i} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>{msg.text}</p>
        ))}
      </div>
      <input id="textInput" value={input} onChange={(e) => setInput(e.target.value)} />
      <button id="sendButton" onClick={sendMessage}>Send</button>
    </div>
  );
};

export default Chat;
