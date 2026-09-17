import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import client from "../api/client";

function useCountUp(target, durationMs = 700) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let start = null;
    let frame;
    function step(timestamp) {
      if (start === null) start = timestamp;
      const progress = Math.min((timestamp - start) / durationMs, 1);
      setValue(Math.round(progress * target));
      if (progress < 1) frame = requestAnimationFrame(step);
    }
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}

export default function Quiz() {
  const { quizId } = useParams();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    client.get(`/api/quizzes/${quizId}`).then((res) => setQuiz(res.data));
  }, [quizId]);

  function selectAnswer(questionIndex, optionIndex) {
    setAnswers((prev) => ({ ...prev, [questionIndex]: optionIndex }));
  }

  async function handleSubmit() {
    setSubmitting(true);
    try {
      const orderedAnswers = quiz.questions.map((_, i) => answers[i] ?? -1);
      const res = await client.post(`/api/quizzes/${quizId}/attempt`, {
        answers: orderedAnswers,
      });
      setResult(res.data);
    } finally {
      setSubmitting(false);
    }
  }

  const animatedScore = useCountUp(result?.score ?? 0);

  if (!quiz) {
    return (
      <div className="max-w-2xl mx-auto p-6 animate-pulse">
        <div className="h-7 w-56 bg-white/10 rounded" />
        <div className="h-4 w-40 bg-white/5 rounded mt-3 mb-6" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-24 w-full bg-white/10 rounded-lg mb-4" />
        ))}
      </div>
    );
  }

  const answeredCount = quiz.questions.filter((_, i) => answers[i] !== undefined).length;
  const allAnswered = answeredCount === quiz.questions.length;
  const progressPercent = (answeredCount / quiz.questions.length) * 100;

  if (result) {
    const passed = result.score >= quiz.passing_score;
    return (
      <div className="max-w-xl mx-auto p-6 text-center">
        <div
          className={`glass-card border rounded-2xl p-8 animate-scale-in shadow-glow ${
            passed ? "border-emerald-400/30" : "border-red-400/30"
          }`}
        >
          <p className="text-sm uppercase tracking-wide text-slate-400">
            {quiz.title}
          </p>
          <p className={`text-5xl font-bold mt-2 tabular-nums ${passed ? "text-emerald-400" : "text-red-400"}`}>
            {animatedScore}%
          </p>
          <p className="mt-2 text-slate-300">
            {passed
              ? "Passed — nice work!"
              : `Not quite — you need ${quiz.passing_score}% to pass. Give it another go.`}
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={() => {
                setResult(null);
                setAnswers({});
              }}
              className="px-4 py-2 rounded-lg glass-card text-slate-200 hover:border-white/25 active:scale-95 transition-all"
            >
              Retake
            </button>
            <Link
              to={`/courses/${quiz.course_id}`}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-teal-400 to-cyan-500 text-slate-900 font-medium hover:brightness-110 active:scale-95 transition-all"
            >
              Back to course
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 pb-24 animate-fade-in">
      <h1 className="text-2xl font-semibold mb-1 text-white">{quiz.title}</h1>
      <p className="text-sm text-slate-400 mb-3">
        {quiz.questions.length} questions &middot; {quiz.passing_score}% to pass
      </p>

      <div className="glass-card rounded-xl px-4 py-3 mb-4">
        <div className="flex justify-between text-xs text-slate-400 mb-1.5">
          <span>{answeredCount} of {quiz.questions.length} answered</span>
          {allAnswered && <span className="text-emerald-400 font-medium">Ready to submit</span>}
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-teal-400 to-cyan-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      <div className="space-y-4">
        {quiz.questions.map((q, qi) => {
          const answered = answers[qi] !== undefined;
          return (
            <div
              key={qi}
              className={`glass-card rounded-xl p-4 transition-colors duration-150 ${
                answered ? "border-teal-400/25" : ""
              }`}
            >
              <p className="font-medium mb-3 flex items-center gap-2 text-slate-100">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0 transition-colors duration-150 ${
                    answered ? "bg-gradient-to-br from-teal-400 to-cyan-500 text-slate-900" : "bg-white/10 text-slate-400"
                  }`}
                >
                  {answered ? "✓" : qi + 1}
                </span>
                {q.question}
              </p>
              <div className="space-y-2">
                {q.options.map((option, oi) => (
                  <label
                    key={oi}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-sm transition-all duration-150 ${
                      answers[qi] === oi
                        ? "border-teal-400/50 bg-teal-400/10 text-slate-100"
                        : "border-white/10 text-slate-300 hover:bg-white/5 hover:border-white/20"
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${qi}`}
                      checked={answers[qi] === oi}
                      onChange={() => selectAnswer(qi, oi)}
                    />
                    {option}
                  </label>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!allAnswered || submitting}
        className="mt-6 bg-gradient-to-r from-emerald-400 to-teal-500 text-slate-900 font-medium px-5 py-2 rounded-lg hover:brightness-110 active:scale-95 transition-all disabled:opacity-40 disabled:active:scale-100"
      >
        {submitting ? "Submitting..." : "Submit Quiz"}
      </button>
    </div>
  );
}
