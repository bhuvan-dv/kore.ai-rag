import { useState } from "react";

export default function SourcePanel({ sources, confidence, confidenceLevel = "low" }) {
    const [expandedSources, setExpandedSources] = useState({});
    const summary = {
        high: "Confident",
        medium: "Medium / cautious",
        low: "Low confidence",
    }[confidenceLevel];

    const toggleSource = (index) => {
        setExpandedSources((prev) => ({
            ...prev,
            [index]: !prev[index],
        }));
    };

    return (
        <div className="source-panel">
            {/* Confidence bar */}
            <div className="confidence-section">
                <div className="conf-header">
                    <span className="conf-label">Confidence</span>
                    <span className={`conf-value ${confidenceLevel}`}>
                        {summary} · {(confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="conf-bar-track">
                    <div
                        className={`conf-bar-fill ${confidenceLevel}`}
                        style={{ width: `${confidence * 100}%` }}
                    />
                </div>
                {confidenceLevel === "medium" && (
                    <p className="conf-warning cautious">
                        Medium confidence — answer looks plausible, but it is worth double-checking the sources.
                    </p>
                )}
                {confidenceLevel === "low" && (
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
                            <div className="source-heading">
                                <span className="source-num">Source {i + 1}</span>
                                {src.source_url ? (
                                    <a
                                        className="source-link"
                                        href={src.source_url}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        {src.source_url}
                                    </a>
                                ) : (
                                    <span className="source-path">{src.source}</span>
                                )}
                            </div>
                            <span className="source-score">
                                {(src.score * 100).toFixed(0)}% match
                            </span>
                        </div>
                        {src.source_url && (
                            <p className="source-path">{src.source}</p>
                        )}
                        <div className={`source-content ${expandedSources[i] ? "expanded" : "collapsed"}`}>
                            {src.content}
                        </div>
                        <button
                            className="source-toggle"
                            onClick={() => toggleSource(i)}
                            type="button"
                        >
                            {expandedSources[i] ? "Show less" : "Show more"}
                        </button>
                    </div>
                ))}
            </div>

            {sources.length === 0 && (
                <p className="panel-empty">No sources available for this response.</p>
            )}
        </div>
    );
}
