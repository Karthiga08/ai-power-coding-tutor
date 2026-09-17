import { useMemo } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { python } from "@codemirror/lang-python";
import { java } from "@codemirror/lang-java";
import { StreamLanguage } from "@codemirror/language";
import { ruby } from "@codemirror/legacy-modes/mode/ruby";

const LANGUAGE_META = {
  python: { icon: "🐍", label: "Python", filename: "solution.py", extensions: [python()] },
  java: { icon: "☕", label: "Java", filename: "Main.java", extensions: [java()] },
  ruby: { icon: "💎", label: "Ruby", filename: "solution.rb", extensions: [StreamLanguage.define(ruby)] },
};

export default function CodeEditor({ value, onChange, language = "python" }) {
  const meta = LANGUAGE_META[language] || LANGUAGE_META.python;
  const lineCount = useMemo(() => value.split("\n").length, [value]);
  const charCount = value.length;

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/10 bg-black/20">
        <div className="flex items-center gap-2 text-slate-300 text-xs">
          <span className="text-sm leading-none">{meta.icon}</span>
          <span className="font-mono">{meta.filename}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="px-1.5 py-0.5 rounded bg-accent/10 border border-accent/20 text-accent font-medium">
            {meta.label}
          </span>
          <span className="tabular-nums">
            {lineCount} {lineCount === 1 ? "line" : "lines"}
          </span>
          <span className="text-slate-600">&middot;</span>
          <span className="tabular-nums">{charCount} chars</span>
        </div>
      </div>
      <CodeMirror
        value={value}
        onChange={onChange}
        theme={vscodeDark}
        extensions={meta.extensions}
        height="16rem"
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          autocompletion: true,
          highlightActiveLine: true,
        }}
        className="text-sm"
      />
    </div>
  );
}
