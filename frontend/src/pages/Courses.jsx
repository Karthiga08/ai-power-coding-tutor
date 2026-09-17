import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

const ICONS = [
  { match: /python/i, emoji: "🐍", gradient: "from-yellow-400 to-blue-500" },
  { match: /data structure/i, emoji: "🌳", gradient: "from-lime-400 to-emerald-600" },
  { match: /java(?!script)/i, emoji: "☕", gradient: "from-orange-400 to-red-500" },
  { match: /ruby|rails/i, emoji: "💎", gradient: "from-red-400 to-rose-600" },
  { match: /ai|machine learning/i, emoji: "🤖", gradient: "from-purple-400 to-cyan-600" },
];

function courseIcon(title) {
  return ICONS.find((i) => i.match.test(title)) || { emoji: "📘", gradient: "from-slate-400 to-slate-600" };
}

function CourseCardSkeleton() {
  return (
    <div className="glass-card rounded-2xl p-4 animate-pulse">
      <div className="w-10 h-10 rounded-xl bg-white/10" />
      <div className="h-5 w-2/3 bg-white/10 rounded mt-3" />
      <div className="h-4 w-full bg-white/5 rounded mt-3" />
      <div className="h-4 w-1/2 bg-white/5 rounded mt-2" />
      <div className="h-5 w-16 bg-white/10 rounded mt-4" />
    </div>
  );
}

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get("/api/courses")
      .then((res) => setCourses(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-6 text-white">Courses</h1>
      <div className="grid gap-4 sm:grid-cols-2">
        {loading &&
          Array.from({ length: 4 }).map((_, i) => <CourseCardSkeleton key={i} />)}

        {!loading &&
          courses.map((c, i) => {
            const icon = courseIcon(c.title);
            return (
              <Link
                key={c.id}
                to={`/courses/${c.id}`}
                style={{ animationDelay: `${i * 40}ms` }}
                className="group glass-card rounded-2xl p-4 transition-all duration-200 hover:shadow-glow hover:-translate-y-0.5 hover:border-teal-400/30 animate-fade-in"
              >
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${icon.gradient} flex items-center justify-center text-lg shadow-md`}
                >
                  {icon.emoji}
                </div>
                <h2 className="font-medium text-lg text-white mt-3 group-hover:text-accent transition-colors">
                  {c.title}
                </h2>
                <p className="text-sm text-slate-400 mt-1">{c.description}</p>
                <span className="inline-block mt-3 text-xs px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300 group-hover:border-teal-400/40 group-hover:text-accent transition-colors">
                  {c.difficulty_level}
                </span>
              </Link>
            );
          })}

        {!loading && courses.length === 0 && (
          <p className="text-slate-400">No courses yet. An admin can add some.</p>
        )}
      </div>
    </div>
  );
}
