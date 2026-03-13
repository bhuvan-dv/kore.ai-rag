export default function MessageBubble({ message, isSelected, onSelect }) {
    const isUser = message.role === "user";
    const confidenceLevel = message.confidence_level || (message.is_confident ? "high" : "low");
    const confidenceLabel = {
        high: "✓ Confident",
        medium: "• Cautious",
        low: "⚠ Low confidence",
    }[confidenceLevel];

    return (
        <div
            className={`msg-row ${isUser ? "user" : "assistant"} ${isSelected ? "selected" : ""}`}
            onClick={onSelect}
        >
            {/* Avatar */}
            <div className={`avatar ${isUser ? "avatar-user" : "avatar-bot"}`}>
                {isUser ? "Y" : "K"}
            </div>

            {/* Bubble */}
            <div className="bubble-wrap">
                <div className={`bubble ${isUser ? "bubble-user" : "bubble-bot"}`}>
                    <div className="bubble-text">{message.content}</div>
                </div>

                {/* Meta row for assistant messages */}
                {!isUser && message.confidence !== undefined && (
                    <div className="bubble-meta">
                        <span className={`confidence-tag ${confidenceLevel}`}>
                            {confidenceLabel} · {(message.confidence * 100).toFixed(0)}%
                        </span>

                        {message.sources?.length > 0 && (
                            <button className="meta-link" onClick={onSelect}>
                                {message.sources.length} sources
                            </button>
                        )}

                        {message.reasoning?.length > 0 && (
                            <button className="meta-link" onClick={onSelect}>
                                {message.reasoning.length} steps
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
