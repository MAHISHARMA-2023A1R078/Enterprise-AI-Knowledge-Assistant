function ChatMessage({ message, onShowSources }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div className={`message-avatar ${isUser ? "user-avatar" : "ai-avatar"}`}>
        {isUser ? "Y" : "✦"}
      </div>

      <div className="message-content">
        <div className="message-author">{isUser ? "You" : "AI Assistant"}</div>

        <div className="message-text">{message.content}</div>

        {!isUser && message.sources?.length > 0 && (
          <button
            className="sources-trigger"
            onClick={() => onShowSources(message.sources)}
          >
            <span>◈</span>
            Sources ({message.sources.length})
            <span className="sources-arrow">↗</span>
          </button>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
