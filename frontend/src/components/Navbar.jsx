import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `relative py-1 whitespace-nowrap transition-colors duration-150 hover:text-accent ${
          isActive ? "text-accent" : "text-slate-300"
        }`
      }
    >
      {({ isActive }) => (
        <>
          {children}
          <span
            className={`absolute -bottom-1 left-0 h-0.5 bg-accent rounded-full transition-all duration-200 ${
              isActive ? "w-full" : "w-0"
            }`}
          />
        </>
      )}
    </NavLink>
  );
}

function Avatar({ name }) {
  const initial = name ? name.charAt(0).toUpperCase() : "?";
  return (
    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center text-xs font-semibold text-white shadow-glow flex-shrink-0">
      {initial}
    </div>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="glass-card sticky top-0 z-20 px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-y-2 border-x-0 border-t-0">
      <Link
        to="/"
        className="font-semibold text-lg text-white transition-transform duration-150 hover:scale-[1.02] whitespace-nowrap"
      >
        <span className="hidden sm:inline">AI Power Coding Tutor</span>
        <span className="sm:hidden">AI Tutor</span>
      </Link>
      <div className="flex items-center gap-3 sm:gap-5 text-sm">
        <NavItem to="/courses">Courses</NavItem>
        {user && <NavItem to="/progress">Progress</NavItem>}
        {user?.role === "admin" && <NavItem to="/admin">Admin</NavItem>}
        {user ? (
          <div className="flex items-center gap-2 sm:gap-3 pl-2 sm:pl-3 ml-1 border-l border-white/10">
            <Avatar name={user.name} />
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="text-slate-300 hover:text-accent transition-colors duration-150 active:scale-95 whitespace-nowrap"
            >
              Logout
            </button>
          </div>
        ) : (
          <NavItem to="/login">Login</NavItem>
        )}
      </div>
    </nav>
  );
}
