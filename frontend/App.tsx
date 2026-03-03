import { useState, useEffect } from 'react'
import './App.css'

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // 1. Fetch History on Load
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/history')
      .then(res => res.json())
      .then(data => {
        // Flatten DB rows into a chat list
        // Note: We map user_message and ai_response from your SQLAlchemy model
        const history: Message[] = [];
        // We reverse because the backend usually sends newest first
        [...data].reverse().forEach((chat: any) => {
          history.push({ sender: 'user', text: chat.user_message });
          history.push({ sender: 'ai', text: chat.ai_response });
        });
        setMessages(history);
      })
      .catch(err => console.error("Could not load history:", err));
  }, []);

  // 2. Send Message function
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });
      const data = await response.json();
      
      const aiMsg: Message = { sender: 'ai', text: data.response };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header><h1>Gemini SaaS</h1></header>
      <div className="chat-window" style={{ display: 'flex', flexDirection: 'column' }}>
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>
            <strong>{m.sender === 'user' ? 'You: ' : 'AI: '}</strong>
            <span>{m.text}</span>
          </div>
        ))}
        {loading && <div className="message ai">Thinking...</div>}
      </div>
      <div className="input-area">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  )
}

export default App
