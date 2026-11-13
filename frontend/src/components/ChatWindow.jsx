import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";

function ChatWindow({ messages, onSend, loading }) {
  const [question, setQuestion] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!question.trim() || loading) return;

    onSend(question.trim());
    setQuestion("");
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-chat">
            <h2>Ask your documents anything</h2>
            <p>Upload a PDF and start asking questions.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {loading && <div className="loading-message">AI is thinking...</div>}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask a question about your documents..."
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={loading}
        />

        <button type="submit" disabled={!question.trim() || loading}>
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;
