import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  Cell,
  LabelList,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import client from "../api/client";

function CustomTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload;
  return (
    <div className="glass-card rounded-lg px-3 py-2 text-sm shadow-glow">
      <p className="font-medium text-slate-100">{point.course}</p>
      <p className="text-slate-400">{point.completion}% complete</p>
    </div>
  );
}

function makeBarLabel(peakValue) {
  return function BarLabel({ x, y, width, value }) {
    const cx = x + width / 2;
    if (value === peakValue && peakValue > 0) {
      const badgeWidth = 48;
      return (
        <foreignObject x={cx - badgeWidth / 2} y={y - 32} width={badgeWidth} height={24}>
          <div className="bg-gradient-to-r from-teal-400 to-cyan-500 text-slate-900 text-[11px] font-semibold rounded-full px-2 py-1 text-center shadow-glow animate-fade-in">
            {value}%
          </div>
        </foreignObject>
      );
    }
    return (
      <text x={cx} y={y - 10} textAnchor="middle" fontSize={11} fill="#94a3b8">
        {value}%
      </text>
    );
  };
}

export default function Progress() {
  const [data, setData] = useState(null);

  useEffect(() => {
    Promise.all([client.get("/api/analytics/me"), client.get("/api/courses")]).then(
      ([progressRes, coursesRes]) => {
        const progressByCourseId = Object.fromEntries(
          progressRes.data.map((p) => [p.course_id, p.completion_percent])
        );
        const merged = coursesRes.data.map((c) => ({
          course: c.title,
          completion: Math.round(progressByCourseId[c.id] ?? 0),
          attempted: c.id in progressByCourseId,
        }));
        setData(merged);
      }
    );
  }, []);

  if (!data) {
    return (
      <div className="max-w-3xl mx-auto p-6 animate-pulse">
        <div className="h-7 w-48 bg-white/10 rounded" />
        <div className="h-24 w-full bg-white/10 rounded-2xl mt-4" />
        <div className="h-80 w-full bg-white/10 rounded-2xl mt-4" />
      </div>
    );
  }

  const anyAttempted = data.some((d) => d.attempted);
  const attemptedCount = data.filter((d) => d.attempted).length;
  const overallAverage = Math.round(data.reduce((sum, d) => sum + d.completion, 0) / data.length);
  const peakValue = Math.max(...data.map((d) => d.completion));

  return (
    <div className="max-w-3xl mx-auto p-6 animate-fade-in">
      <h1 className="text-2xl font-semibold mb-2 text-white">Your Progress</h1>
      <p className="text-slate-400 text-sm mb-6 max-w-xl">
        Each bar is a course's completion percentage. Right now that number
        comes only from <strong className="text-slate-300">quiz scores</strong> — each time you complete
        a course's quiz, its bar updates to a running average of your
        attempts. It doesn't yet factor in how many lessons you've read or
        coding problems you've solved, so a 0% bar just means you haven't
        taken that course's quiz yet, not that you haven't done anything.
      </p>

      <div className="glass-card rounded-2xl p-6 mb-4 shadow-glow">
        <div className="flex items-end justify-between flex-wrap gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Average completion</p>
            <p className="text-5xl font-bold text-white mt-1 tabular-nums">{overallAverage}%</p>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase tracking-wide text-slate-400">Quizzes taken</p>
            <p className="text-2xl font-semibold text-accent mt-1 tabular-nums">
              {attemptedCount}
              <span className="text-slate-500 text-base font-normal"> / {data.length}</span>
            </p>
          </div>
        </div>
      </div>

      {!anyAttempted && (
        <div className="mb-4 text-sm glass-card border-amber-400/30 text-amber-300 rounded-xl px-4 py-3">
          You haven't completed any quizzes yet, so every course sits at 0%.
          Open a course and take its quiz to see a bar move.
        </div>
      )}

      <div className="glass-card h-80 rounded-2xl p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 40, right: 10, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.08)" />
            <XAxis
              dataKey="course"
              angle={-30}
              textAnchor="end"
              interval={0}
              height={70}
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
              label={{ value: "Completion %", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
            <Bar dataKey="completion" radius={[6, 6, 0, 0]}>
              {data.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.completion === peakValue && peakValue > 0 ? "url(#barActive)" : "url(#barMuted)"}
                />
              ))}
              <LabelList dataKey="completion" content={makeBarLabel(peakValue)} />
            </Bar>
            <defs>
              <linearGradient id="barActive" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2dd4bf" />
                <stop offset="100%" stopColor="#0891b2" />
              </linearGradient>
              <linearGradient id="barMuted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgba(148,163,184,0.35)" />
                <stop offset="100%" stopColor="rgba(148,163,184,0.15)" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
