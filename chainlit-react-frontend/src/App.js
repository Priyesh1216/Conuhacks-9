import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  // Function to send message
  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;

    // Add the user's message to the chat
    setMessages([...messages, { sender: 'user', text: inputMessage }]);

    try {
      // Call Chainlit backend (assumes it's running on localhost:5005)
      const response = await axios.post('http://localhost:5005/api/message', {
        message: inputMessage,
      });

      // Add the response from Chainlit to the chat
      setMessages([...messages, { sender: 'user', text: inputMessage }, { sender: 'bot', text: response.data.response }]);
    } catch (error) {
      console.error("Error sending message:", error);
    }

    setInputMessage('');
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message"
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default App;
