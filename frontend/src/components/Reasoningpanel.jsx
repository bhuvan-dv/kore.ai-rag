const TOOL_ICONS = {
    vector_search: "🔍",
    api_lookup: "🔌",
    structured_lookup: "📊",
    llm_generation: "🤖",
    null: "🧠",
};

export default function ReasoningPanel({ steps }) {
    return (
        <div className="reasoning-panel">
            <div className="steps-timeline">
                {steps.map((step, i) => (
                    <div key={i} className="step-item">
                        {/* Connector line */}
                        {i < steps.length - 1 && <div className="step-line" />}

                        {/* Step dot */}
                        <div className="step-dot">
                            <span>{TOOL_ICONS[step.tool_used] || "🧠"}</span>
                        </div>

                        {/* Step content */}
                        <div className="step-body">
                            <div className="step-head">
                                <span className="step-action">{step.action}</span>
                                <span className="step-num">Step {step.step}</span>
                            </div>
                            <p className="step-desc">{step.description}</p>
                            {step.tool_used && (
                                <span className="tool-badge">{step.tool_used}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {steps.length === 0 && (
                <p className="panel-empty">No reasoning trace available.</p>
            )}
        </div>
    );
}