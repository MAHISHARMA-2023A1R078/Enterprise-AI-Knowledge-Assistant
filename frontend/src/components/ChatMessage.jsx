function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">{isUser ? "You" : "AI"}</div>

      <div className="message-content">
        <div className="message-text">{message.content}</div>

        {!isUser && message.sources?.length > 0 && (
          <div className="sources">
            <h4>Sources</h4>

            {message.sources.map((source, index) => (
              <div className="source-item" key={index}>
                <span>{source.filename}</span>
                <span>Page {source.page_number}</span>
                <span>Score: {source.score}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
