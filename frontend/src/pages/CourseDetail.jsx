import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import client from "../api/client";

function ChevronIcon({ open }) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      className={`w-4 h-4 flex-shrink-0 transition-transform duration-200 ${open ? "rotate-90" : ""}`}
    >
      <path
        fillRule="evenodd"
        d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function LessonProblems({ lessonId }) {
  const [problems, setProblems] = useState(null);

  useEffect(() => {
    client.get(`/api/problems/by-lesson/${lessonId}`).then((res) => setProblems(res.data));
  }, [lessonId]);

  if (problems === null) {
    return <p className="text-xs text-slate-500 mt-3">Loading problems...</p>;
  }
  if (problems.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {problems.map((p) => (
        <Link
          key={p.id}
          to={`/problems/${p.id}`}
          className="text-xs px-3 py-1 rounded-full bg-teal-400/10 text-accent border border-teal-400/20 hover:bg-teal-400/20 hover:shadow-glow transition-all duration-150 active:scale-95"
        >
          {p.title}
        </Link>
      ))}
    </div>
  );
}

function LessonAccordionItem({ lesson, open, onToggle }) {
  return (
    <div
      className={`glass-card rounded-xl transition-colors duration-150 ${
        open ? "border-teal-400/30 bg-teal-400/[0.03]" : "hover:border-white/20"
      }`}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-3 text-left p-4 text-slate-100"
      >
        <h3 className="font-medium">{lesson.title}</h3>
        <span className={open ? "text-accent" : "text-slate-500"}>
          <ChevronIcon open={open} />
        </span>
      </button>

      <div
        className="grid transition-[grid-template-rows] duration-300 ease-in-out"
        style={{ gridTemplateRows: open ? "1fr" : "0fr" }}
      >
        <div className="overflow-hidden">
          <div className="px-4 pb-4">
            <p className="text-sm text-slate-400 whitespace-pre-wrap">{lesson.content}</p>
            {open && <LessonProblems lessonId={lesson.id} />}
          </div>
        </div>
      </div>
    </div>
  );
}

function CourseQuizzes({ courseId }) {
  const [quizzes, setQuizzes] = useState(null);

  useEffect(() => {
    client.get(`/api/quizzes/by-course/${courseId}`).then((res) => setQuizzes(res.data));
  }, [courseId]);

  if (!quizzes || quizzes.length === 0) return null;

  return (
    <>
      <h2 className="text-lg font-medium mt-8 mb-3 text-white">Quizzes</h2>
      <div className="space-y-2">
        {quizzes.map((q) => (
          <Link
            key={q.id}
            to={`/quizzes/${q.id}`}
            className="glass-card block rounded-xl p-4 transition-all duration-150 hover:shadow-glow hover:-translate-y-0.5 hover:border-teal-400/30"
          >
            <h3 className="font-medium text-slate-100">{q.title}</h3>
            <p className="text-sm text-slate-400 mt-1">
              {q.questions.length} questions &middot; {q.passing_score}% to pass
            </p>
          </Link>
        ))}
      </div>
    </>
  );
}

export default function CourseDetail() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [openLessonId, setOpenLessonId] = useState(null);

  useEffect(() => {
    client.get(`/api/courses/${courseId}`).then((res) => {
      setCourse(res.data);
      if (res.data.lessons.length > 0) setOpenLessonId(res.data.lessons[0].id);
    });
  }, [courseId]);

  if (!course) return <div className="p-6 text-slate-400">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto p-6 animate-fade-in">
      <h1 className="text-2xl font-semibold text-white">{course.title}</h1>
      <p className="text-slate-400 mt-2">{course.description}</p>

      <div className="flex items-center justify-between mt-8 mb-3">
        <h2 className="text-lg font-medium text-white">Lessons</h2>
        <span className="text-xs text-slate-500">Click a lesson to expand it</span>
      </div>
      <div className="space-y-2">
        {course.lessons.map((l) => (
          <LessonAccordionItem
            key={l.id}
            lesson={l}
            open={openLessonId === l.id}
            onToggle={() => setOpenLessonId(openLessonId === l.id ? null : l.id)}
          />
        ))}
        {course.lessons.length === 0 && (
          <p className="text-slate-500">No lessons yet.</p>
        )}
      </div>

      <CourseQuizzes courseId={courseId} />

      <Link
        to="/courses"
        className="inline-block mt-6 text-accent text-sm hover:underline"
      >
        ← Back to courses
      </Link>
    </div>
  );
}
