import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

const ICONS = {
  "Total users": "👥",
  "Total submissions": "📦",
  "Pass rate": "✅",
  "Avg. quiz score": "🎯",
};

function StatCardSkeleton() {
  return (
    <div className="glass-card rounded-2xl p-4 animate-pulse">
      <div className="w-8 h-8 rounded-lg bg-white/10" />
      <div className="h-4 w-20 bg-white/10 rounded mt-4" />
      <div className="h-7 w-16 bg-white/10 rounded mt-2" />
    </div>
  );
}

export default function Admin() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    client.get("/api/analytics/admin").then((res) => setStats(res.data));
  }, []);

  const cards = stats
    ? [
        { label: "Total users", value: stats.total_users, to: "/admin/users" },
        { label: "Total submissions", value: stats.total_submissions },
        { label: "Pass rate", value: `${stats.pass_rate}%` },
        { label: "Avg. quiz score", value: `${stats.average_quiz_score}%` },
      ]
    : [];

  return (
    <div className="max-w-3xl mx-auto p-6 animate-fade-in">
      <h1 className="text-2xl font-semibold mb-6 text-white">Admin Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        {!stats && Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)}

        {stats &&
          cards.map((c, i) => {
            const Wrapper = c.to ? Link : "div";
            return (
              <Wrapper
                key={c.label}
                to={c.to}
                style={{ animationDelay: `${i * 60}ms` }}
                className={`glass-card rounded-2xl p-4 transition-all duration-200 animate-fade-in ${
                  c.to ? "hover:shadow-glow hover:-translate-y-0.5 cursor-pointer" : ""
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="w-8 h-8 rounded-lg bg-teal-400/10 flex items-center justify-center text-base">
                    {ICONS[c.label]}
                  </div>
                  {c.to && <span className="text-accent text-xs">View all →</span>}
                </div>
                <p className="text-sm text-slate-400 mt-3">{c.label}</p>
                <p className="text-2xl font-semibold mt-1 text-white tabular-nums">{c.value}</p>
              </Wrapper>
            );
          })}
      </div>
    </div>
  );
}
