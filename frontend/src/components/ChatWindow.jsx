import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";

function ChatWindow({ messages, onSend, loading, onShowSources }) {
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
          <div className="welcome-screen">
            <div className="welcome-icon">✦</div>
            <p className="welcome-eyebrow">YOUR DOCUMENTS, UNDERSTOOD</p>
            <h2>What would you like to know?</h2>
            <p className="welcome-description">
              Ask a question about your uploaded documents. I'll find relevant
              information and provide an answer.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message}
            onShowSources={onShowSources}
          />
        ))}

        {loading && (
          <div className="loading-message">
            <span className="loading-dot" />
            AI is thinking...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <form className="chat-input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Ask anything about your documents..."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={loading}
          />

          <button
            type="submit"
            disabled={!question.trim() || loading}
            aria-label="Send message"
          >
            ↑
          </button>
        </form>

        <p className="input-disclaimer">
          AI can make mistakes. Verify important information with your
          documents.
        </p>
      </div>
    </div>
  );
}

export default ChatWindow;
