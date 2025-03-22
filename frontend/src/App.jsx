import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const initialTranscript = `GROUP DISCUSSION TRANSCRIPT:
HUMAN: "Hi!"
WHITE_HAT: "Hello! I am the White Hat."
GREEN_HAT: "Hello! I am the Green Hat."
BLACK_HAT: "Hello! I am the Black Hat."`;

  const [messages, setMessages] = useState([
    { role: "system", content: "Welcome to the Six Thinking Hats group chat!" },
    { role: "WHITE_HAT", content: "Hello! I am the White Hat.", decision: "SEND" },
    { role: "GREEN_HAT", content: "Hello! I am the Green Hat.", decision: "SEND" },
    { role: "BLACK_HAT", content: "Hello! I am the Black Hat.", decision: "SEND" }
  ]);

  const [agentTranscripts, setAgentTranscripts] = useState({
    "white_hat": initialTranscript,
    "black_hat": initialTranscript,
    "green_hat": initialTranscript
  });

  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showNotSent, setShowNotSent] = useState(false);
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!userInput.trim()) return;
    
    // Add user message to messages
    const userMessage = userInput.trim();
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setUserInput("");
    setIsLoading(true);
    
    // Update transcripts with user message
    const updatedTranscripts = {...agentTranscripts};
    for (const agent in updatedTranscripts) {
      updatedTranscripts[agent] += `\nHUMAN: "${userMessage}"\n`;
    }
    
    try {
      // API call
      const response = await fetch('http://127.0.0.1:5000/api/send-message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          message: userMessage,
          agentTranscripts: updatedTranscripts
        })
      });
      
      const data = await response.json();
      console.log("Responses from API:", data.responses);
      // Update transcripts with AI responses
      const newTranscripts = updateAgentTranscripts(updatedTranscripts, data.responses);
      setAgentTranscripts(newTranscripts);
      
      // Add AI messages to display
      const newMessages = data.responses.map(resp => ({
        role: resp.agent.toUpperCase(),
        content: resp.message.replace(/^[A-Z_]+: /g, ''), // Remove prefixes like "WHITE_HAT: "
        innerVoice: resp.innerVoice,
        decision: resp.decision
      }));
      
      setMessages(prev => [...prev, ...newMessages]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, {
        role: "system", 
        content: "Error communicating with the server. Please try again."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateAgentTranscripts = (transcripts, responses) => {
    const result = {...transcripts};
    const responsesByAgent = {};
    
    responses.forEach(resp => {
      responsesByAgent[resp.agent] = resp;
    });
    
    // Update each agent's transcript
    for (const hat in result) {
      const resp = responsesByAgent[hat];
      let innerVoiceAddition = `NEW MESSAGE: ${hat.toUpperCase()}: ${resp.message}\n`;
      innerVoiceAddition += `INNER VOICE: ${resp.innerVoice}\n`;
      
      // Add other agents' messages if SEND
      let sentAdditions = "";
      for (const agent in responsesByAgent) {
        if (agent !== hat && responsesByAgent[agent].decision === "SEND") {
          sentAdditions += `${agent.toUpperCase()}: ${responsesByAgent[agent].message}\n`;
        }
      }
      
      result[hat] = result[hat] + innerVoiceAddition + sentAdditions;
    }
    
    return result;
  };

  const resetChat = () => {
    if (window.confirm("Are you sure you want to reset the chat?")) {
      setMessages([
        { role: "system", content: "Welcome to the Six Thinking Hats group chat!" },
        { role: "WHITE_HAT", content: "Hello! I am the White Hat.", decision: "SEND" },
        { role: "GREEN_HAT", content: "Hello! I am the Green Hat.", decision: "SEND" },
        { role: "BLACK_HAT", content: "Hello! I am the Black Hat.", decision: "SEND" }
      ]);
      setAgentTranscripts({
        "white_hat": initialTranscript,
        "black_hat": initialTranscript,
        "green_hat": initialTranscript
      });
    }
  };

  const getAgentColor = (role) => {
    switch(role.toLowerCase()) {
      case 'white_hat':
        return 'rgb(30, 144, 255)'; // Dodger Blue
      case 'black_hat':
        return 'rgb(255, 69, 0)';   // Orange Red
      case 'green_hat':
        return 'rgb(50, 205, 50)';  // Lime Green
      default:
        return 'rgb(128, 128, 128)'; // Gray
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🧢 Six Thinking Hats AI Discussion</h1>
        <div className="header-controls">
          <label className="toggle-label">
            <input 
              type="checkbox" 
              checked={showNotSent} 
              onChange={() => setShowNotSent(!showNotSent)}
            />
            Show Hidden Messages
          </label>
          <button className="reset-button" onClick={resetChat}>Reset Chat</button>
        </div>
      </header>
      
      <div className="messages-container">
        {messages.map((msg, index) => {
          // Skip NOT_SEND messages if showNotSent is false
          if (msg.decision === "NOT SEND" && !showNotSent) return null;
          
          return (
            <div 
              key={index} 
              className={`message ${msg.role.toLowerCase()} ${msg.decision === 'NOT_SEND' ? 'not-sent' : ''}`}
            >
              <div className="message-header" style={{ color: getAgentColor(msg.role) }}>
                <span className="agent-name">{msg.role}</span>
                {msg.decision === 'NOT_SEND' && <span className="not-sent-badge">Not Sent</span>}
              </div>
              <div className="message-content">{msg.content}</div>
              {msg.innerVoice && (
                <details className="inner-voice">
                  <summary>Inner Voice</summary>
                  <div className="inner-voice-content">{msg.innerVoice}</div>
                </details>
              )}
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Thinking..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default App;