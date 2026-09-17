import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

const ROLE_STYLES = {
  admin: "bg-amber-400/15 text-amber-300 border-amber-400/20",
  instructor: "bg-teal-400/15 text-teal-300 border-teal-400/20",
  student: "bg-white/5 text-slate-300 border-white/10",
};

function RowSkeleton() {
  return (
    <div className="glass-card rounded-xl p-4 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="w-9 h-9 rounded-full bg-white/10" />
        <div className="flex-1">
          <div className="h-4 w-32 bg-white/10 rounded" />
          <div className="h-3 w-48 bg-white/5 rounded mt-2" />
        </div>
        <div className="h-5 w-16 bg-white/10 rounded-full" />
      </div>
      <div className="h-3 w-56 bg-white/5 rounded mt-4" />
    </div>
  );
}

export default function Users() {
  const [users, setUsers] = useState(null);

  useEffect(() => {
    client.get("/api/users/with-stats").then((res) => setUsers(res.data));
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-6 animate-fade-in">
      <Link to="/admin" className="text-accent text-sm hover:underline">
        ← Back to admin dashboard
      </Link>
      <h1 className="text-2xl font-semibold mt-2 mb-6 text-white">
        Users {users && <span className="text-slate-500 text-lg font-normal">({users.length})</span>}
      </h1>

      <div className="space-y-2">
        {!users && Array.from({ length: 4 }).map((_, i) => <RowSkeleton key={i} />)}

        {users &&
          users.map((u, i) => (
            <div
              key={u.id}
              style={{ animationDelay: `${i * 40}ms` }}
              className="glass-card rounded-xl p-4 animate-fade-in"
            >
              <div className="flex items-center gap-4">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center text-xs font-semibold text-white flex-shrink-0">
                  {u.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-slate-100 font-medium truncate">{u.name}</p>
                  <p className="text-slate-500 text-sm truncate">{u.email}</p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded-full border capitalize flex-shrink-0 ${ROLE_STYLES[u.role] || ROLE_STYLES.student}`}
                >
                  {u.role}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-3 pt-3 border-t border-white/10 text-xs">
                <span>
                  <span className="text-slate-500">Avg quiz score</span>{" "}
                  <span className="font-semibold text-accent tabular-nums">
                    {u.average_quiz_score}%
                  </span>
                </span>
                <span>
                  <span className="text-slate-500">Submissions</span>{" "}
                  <span className="font-semibold text-slate-100 tabular-nums">
                    {u.total_submissions}
                  </span>
                </span>
                {u.total_submissions > 0 && (
                  <span>
                    <span className="text-slate-500">Pass rate</span>{" "}
                    <span className="font-semibold text-emerald-400 tabular-nums">
                      {u.pass_rate}%
                    </span>
                    <span className="text-slate-500"> ({u.passed_submissions}/{u.total_submissions})</span>
                  </span>
                )}
              </div>
            </div>
          ))}

        {users && users.length === 0 && (
          <p className="text-slate-500">No users yet.</p>
        )}
      </div>
    </div>
  );
}
