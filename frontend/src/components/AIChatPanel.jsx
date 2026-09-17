import { useEffect, useRef, useState } from "react";
import client from "../api/client";

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 bg-white/5 rounded-lg px-3 py-2.5 w-fit">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce-dot [animation-delay:-0.32s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce-dot [animation-delay:-0.16s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce-dot" />
    </div>
  );
}

export default function AIChatPanel({ problemId, code }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [asking, setAsking] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, asking]);

  async function send() {
    if (!input.trim() || asking) return;
    const userMessage = input;
    setMessages((m) => [...m, { role: "user", text: userMessage }]);
    setInput("");
    setAsking(true);
    try {
      const res = await client.post("/api/ai/ask", {
        context_type: "doubt",
        message: userMessage,
        problem_id: problemId,
        code,
      });
      setMessages((m) => [...m, { role: "ai", text: res.data.response }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "ai", text: "Sorry, the AI tutor is unavailable right now." },
      ]);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="glass-card flex flex-col h-full rounded-lg overflow-hidden">
      <div className="px-4 py-2 border-b border-white/10 font-medium text-slate-200 flex items-center gap-2">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        AI Tutor
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 text-sm">
        {messages.length === 0 && (
          <p className="text-slate-500">Ask about this problem or your code.</p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`whitespace-pre-wrap rounded-lg px-3 py-2 max-w-[90%] animate-fade-in ${
              m.role === "user"
                ? "bg-gradient-to-br from-teal-500/20 to-cyan-600/20 border border-teal-400/20 ml-auto text-slate-100"
                : "bg-white/5 text-slate-300 border border-white/5"
            }`}
          >
            {m.text}
          </div>
        ))}
        {asking && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
      <div className="p-3 border-t border-white/10 flex gap-2">
        <input
          className="glass-input flex-1 rounded-lg px-3 py-2 text-sm transition-shadow disabled:opacity-50"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask the AI tutor..."
          disabled={asking}
        />
        <button
          onClick={send}
          disabled={asking || !input.trim()}
          className="bg-gradient-to-r from-teal-400 to-cyan-500 text-slate-900 font-medium px-4 py-2 rounded-lg hover:brightness-110 active:scale-95 transition-all disabled:opacity-40 disabled:active:scale-100"
        >
          Send
        </button>
      </div>
    </div>
  );
}
