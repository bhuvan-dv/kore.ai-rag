export default function MessageBubble({ message, isSelected, onSelect }) {
    const isUser = message.role === "user";
    const confidenceLevel = message.confidence_level || (message.is_confident ? "high" : "low");
    const confidenceLabel = {
        high: "✓ Confident",
        medium: "• Cautious",
        low: "⚠ Low confidence",
    }[confidenceLevel];
    const uniqueSources = !isUser
        ? message.sources?.reduce((acc, source) => {
            const key = source.source_url || source.source;
            if (!key || acc.some((item) => item.key === key)) {
                return acc;
            }

            acc.push({
                key,
                url: source.source_url,
                label: source.source_url || source.source,
                path: source.source,
            });
            return acc;
        }, []) || []
        : [];

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
                    {!isUser && uniqueSources.length > 0 && (
                        <div className="bubble-sources">
                            <div className="bubble-sources-title">Sources</div>
                            {uniqueSources.map((source) => (
                                <div key={source.key} className="bubble-source-item">
                                    {source.url ? (
                                        <a
                                            className="bubble-source-link"
                                            href={source.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            onClick={(event) => event.stopPropagation()}
                                        >
                                            {source.label}
                                        </a>
                                    ) : (
                                        <span className="bubble-source-link muted">{source.label}</span>
                                    )}
                                    {source.url && source.path && (
                                        <div className="bubble-source-path">{source.path}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
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
