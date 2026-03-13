import { useState, useEffect, useRef } from "react";
import ChatInput from "./components/ChatInput";
import MessageBubble from "./components/MessageBubble";
import SourcePanel from "./components/SourcePanel";
import ReasoningPanel from "./components/ReasoningPanel";
import "./index.css";

const API = "/api";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [panelTab, setPanelTab] = useState("sources");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (query) => {
    if (!query.trim() || loading) return;

    const userMsg = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });
      const data = await res.json();

      const assistantMsg = {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
        reasoning: data.reasoning || [],
        confidence: data.confidence,
        is_confident: data.is_confident,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setSelectedMessage(assistantMsg);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Connection error: ${err.message}. Is the backend running?`,
          sources: [],
          reasoning: [],
          confidence: 0,
          is_confident: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const showPanel =
    selectedMessage?.sources?.length > 0 ||
    selectedMessage?.reasoning?.length > 0;

  return (
    <div className="app-root">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-mark">K</div>
          <div>
            <h1 className="brand-title">Knowledge Search Agent</h1>
            <p className="brand-sub">Kore.ai Documentation Assistant</p>
          </div>
        </div>
        {health && (
          <div className="health-pill">
            <span className="health-dot" />
            {health.document_count.toLocaleString()} docs indexed
          </div>
        )}
      </header>

      {/* Body */}
      <div className="app-body">
        {/* Chat */}
        <div className={`chat-col ${showPanel ? "narrow" : ""}`}>
          <div className="msg-scroll">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">
                  <svg width="40" height="40" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                </div>
                <h2>Search Kore.ai Documentation</h2>
                <p>Ask about dialog tasks, NLP training, channels, APIs, and more.</p>
                <div className="chips">
                  {[
                    "How do I create a dialog task?",
                    "What channels does Kore.ai support?",
                    "How to train the NLP engine?",
                    "Compare dialog tasks and alert tasks",
                  ].map((q) => (
                    <button key={q} className="chip" onClick={() => handleSend(q)}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <MessageBubble
                key={i}
                message={msg}
                isSelected={selectedMessage === msg}
                onSelect={() => {
                  if (msg.role === "assistant") {
                    setSelectedMessage(msg);
                    setPanelTab("sources");
                  }
                }}
              />
            ))}

            {loading && (
              <div className="loading-row">
                <div className="dot-pulse"><span /><span /><span /></div>
                <span>Searching documentation…</span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <ChatInput onSend={handleSend} disabled={loading} />
        </div>

        {/* Side panel */}
        {showPanel && (
          <aside className="side-panel">
            <div className="panel-tabs">
              <button
                className={`ptab ${panelTab === "sources" ? "active" : ""}`}
                onClick={() => setPanelTab("sources")}
              >
                Sources
                {selectedMessage?.sources?.length > 0 && (
                  <span className="badge">{selectedMessage.sources.length}</span>
                )}
              </button>
              <button
                className={`ptab ${panelTab === "reasoning" ? "active" : ""}`}
                onClick={() => setPanelTab("reasoning")}
              >
                Reasoning
                {selectedMessage?.reasoning?.length > 0 && (
                  <span className="badge">{selectedMessage.reasoning.length}</span>
                )}
              </button>
            </div>

            <div className="panel-body">
              {panelTab === "sources" ? (
                <SourcePanel
                  sources={selectedMessage?.sources || []}
                  confidence={selectedMessage?.confidence}
                  isConfident={selectedMessage?.is_confident}
                />
              ) : (
                <ReasoningPanel steps={selectedMessage?.reasoning || []} />
              )}
            </div>

            <button className="panel-close" onClick={() => setSelectedMessage(null)}>
              ✕ Close panel
            </button>
          </aside>
        )}
      </div>
    </div>
  );
}