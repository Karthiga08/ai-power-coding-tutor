import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client";
import AIChatPanel from "../components/AIChatPanel.jsx";
import CodeEditor from "../components/CodeEditor.jsx";

const STATUS_STYLES = {
  passed: {
    badge: "bg-emerald-400/15 text-emerald-400",
    border: "border-emerald-400/30",
    bg: "bg-emerald-400/5",
    icon: "✓",
  },
  failed: {
    badge: "bg-amber-400/15 text-amber-400",
    border: "border-amber-400/30",
    bg: "bg-amber-400/5",
    icon: "✗",
  },
  error: {
    badge: "bg-red-400/15 text-red-400",
    border: "border-red-400/30",
    bg: "bg-red-400/5",
    icon: "!",
  },
};

export default function ProblemSolve() {
  const { problemId } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    setProblem(null);
    setResult(null);
    client.get(`/api/problems/${problemId}`).then((res) => {
      setProblem(res.data);
      setCode(res.data.starter_code || "");
    });
  }, [problemId]);

  async function handleSubmit() {
    setRunning(true);
    setResult(null);
    try {
      const res = await client.post("/api/submissions", { problem_id: problemId, code });
      setResult(res.data);
    } finally {
      setRunning(false);
    }
  }

  function handleReset() {
    setCode(problem.starter_code || "");
  }

  if (!problem) {
    return (
      <div className="max-w-6xl mx-auto p-6 animate-pulse">
        <div className="h-7 w-64 bg-white/10 rounded" />
        <div className="h-4 w-96 bg-white/5 rounded mt-3" />
        <div className="h-64 w-full bg-white/10 rounded-lg mt-4" />
      </div>
    );
  }

  const statusStyle = result ? STATUS_STYLES[result.status] || STATUS_STYLES.error : null;

  return (
    <div className="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
      <div className="lg:col-span-2 space-y-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-white">{problem.title}</h1>
            <span className="text-xs font-medium px-2 py-1 rounded-full bg-teal-400/10 text-accent border border-teal-400/20 uppercase">
              {problem.language}
            </span>
          </div>
          <p className="text-slate-400 mt-2 whitespace-pre-wrap">{problem.description}</p>
        </div>

        <CodeEditor value={code} onChange={setCode} language={problem.language} />

        <div className="flex items-center gap-2">
          <button
            onClick={handleSubmit}
            disabled={running}
            className="bg-gradient-to-r from-emerald-400 to-teal-500 text-slate-900 font-medium px-4 py-2 rounded-lg hover:brightness-110 active:scale-[0.97] transition-all disabled:opacity-50 disabled:active:scale-100 flex items-center gap-2"
          >
            {running && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}
            {running ? "Running..." : "Run & Submit"}
          </button>
          <button
            onClick={handleReset}
            disabled={running}
            title="Reset to starter code"
            className="text-slate-300 px-3 py-2 rounded-lg glass-card hover:border-white/25 hover:text-white active:scale-[0.97] transition-all text-sm disabled:opacity-50"
          >
            Reset
          </button>
        </div>

        {result && (
          <div
            className={`glass-card border rounded-lg p-4 text-sm space-y-2 animate-scale-in ${statusStyle.border} ${statusStyle.bg}`}
          >
            <p className="flex items-center gap-2">
              <span
                className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${statusStyle.badge}`}
              >
                {statusStyle.icon}
              </span>
              <span className={`font-medium capitalize ${statusStyle.badge.split(" ")[1]}`}>
                {result.status}
              </span>
            </p>
            {result.stdout && (
              <pre className="bg-black/30 text-slate-200 p-2 rounded overflow-x-auto border border-white/5">{result.stdout}</pre>
            )}
            {result.stderr && (
              <pre className="bg-red-950/40 text-red-300 p-2 rounded overflow-x-auto border border-red-400/10">
                {result.stderr}
              </pre>
            )}
          </div>
        )}
      </div>

      <div className="h-[32rem]">
        <AIChatPanel problemId={problem.id} code={code} />
      </div>
    </div>
  );
}
