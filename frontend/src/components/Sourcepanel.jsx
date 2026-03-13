export default function SourcePanel({ sources, confidence, isConfident }) {
    return (
        <div className="source-panel">
            {/* Confidence bar */}
            <div className="confidence-section">
                <div className="conf-header">
                    <span className="conf-label">Confidence</span>
                    <span className={`conf-value ${isConfident ? "high" : "low"}`}>
                        {(confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="conf-bar-track">
                    <div
                        className={`conf-bar-fill ${isConfident ? "high" : "low"}`}
                        style={{ width: `${confidence * 100}%` }}
                    />
                </div>
                {!isConfident && (
                    <p className="conf-warning">
                        Low confidence — verify with the sources below.
                    </p>
                )}
            </div>

            {/* Source cards */}
            <div className="source-list">
                {sources.map((src, i) => (
                    <div key={i} className="source-card">
                        <div className="source-header">
                            <span className="source-num">Source {i + 1}</span>
                            <span className="source-score">
                                {(src.score * 100).toFixed(0)}% match
                            </span>
                        </div>
                        <p className="source-path">{src.source}</p>
                        <p className="source-content">{src.content.slice(0, 200)}…</p>
                    </div>
                ))}
            </div>

            {sources.length === 0 && (
                <p className="panel-empty">No sources available for this response.</p>
            )}
        </div>
    );
}