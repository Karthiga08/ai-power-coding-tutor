import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await register(name, email, password);
      navigate("/courses");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-20 p-6 animate-fade-in">
      <div className="glass-card rounded-2xl p-6 shadow-glow">
        <h1 className="text-xl font-semibold mb-5 text-white">Create an account</h1>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            className="glass-input w-full rounded-lg px-3 py-2.5 text-sm transition-shadow"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            className="glass-input w-full rounded-lg px-3 py-2.5 text-sm transition-shadow"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="glass-input w-full rounded-lg px-3 py-2.5 text-sm transition-shadow"
            type="password"
            placeholder="Password (min 8 chars)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="w-full bg-gradient-to-r from-teal-400 to-cyan-500 text-slate-900 font-medium rounded-lg px-3 py-2.5 hover:brightness-110 active:scale-[0.98] transition-all">
            Register
          </button>
        </form>
        <p className="text-sm text-slate-400 mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-accent hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
