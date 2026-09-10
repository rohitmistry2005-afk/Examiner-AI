import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Arrow, Button, Field, Input, Logo } from "@/components/kit";
import { setUser } from "@/lib/examiner";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — ExaminerAI" },
      { name: "description", content: "Sign in to continue your examinations with the ExaminerAI examiner." },
      { property: "og:title", content: "Sign in — ExaminerAI" },
      { property: "og:description", content: "Sign in to continue your examinations with the ExaminerAI examiner." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  return (
    <div className="grid min-h-screen lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <aside className="relative hidden overflow-hidden bg-ink-950 p-12 lg:flex lg:flex-col lg:justify-between">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -left-24 bottom-0 h-[460px] w-[460px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(88,101,242,0.2), transparent 65%)" }}
        />
        <Link to="/" className="relative" aria-label="ExaminerAI home">
          <Logo tone="light" />
        </Link>
        <div className="relative max-w-sm">
          <h2 className="font-display text-[2.5rem] leading-[1.1] tracking-tight text-white">
            The examination is a conversation.
          </h2>
          <p className="mt-5 text-[0.9375rem] leading-relaxed text-white/55">
            Your examiner remembers what you struggled with last time — and will ask about it again.
          </p>
        </div>
        <p className="relative text-[0.75rem] text-white/35">Academic assessment, conducted by AI.</p>
      </aside>

      <main className="flex items-center justify-center px-5 py-16">
        <div className="w-full max-w-sm">
          <div className="lg:hidden">
            <Link to="/" aria-label="ExaminerAI home">
              <Logo />
            </Link>
          </div>
          <h1 className="mt-8 font-display text-[2.25rem] leading-tight tracking-tight text-fg-950 lg:mt-0">
            Welcome back
          </h1>
          <p className="mt-2 text-sm text-fg-700">Sign in to continue your examinations.</p>

          <form
            className="mt-9 space-y-5"
            onSubmit={(e) => {
              e.preventDefault();
              if (!email || !password) {
                setError("Enter your email and password to continue.");
                return;
              }
              setError(null);
              setBusy(true);
              setUser({ name: email.split("@")[0] ?? "Student", email });
              navigate({ to: "/exam/configure" });
            }}
          >
            <Field label="Email" htmlFor="email">
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@university.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Field>
            <Field label="Password" htmlFor="password">
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Field>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-[0.8125rem] text-fg-700">
                <input type="checkbox" className="h-4 w-4 rounded border-line accent-[var(--indigo-600)]" />
                Remember me
              </label>
              <Link to="/login" className="text-[0.8125rem] text-indigo-600 hover:underline">
                Forgot password?
              </Link>
            </div>

            {error ? (
              <p role="alert" className="text-[0.8125rem] text-error">
                {error}
              </p>
            ) : null}

            <Button type="submit" size="lg" className="w-full" disabled={busy}>
              {busy ? "Signing in…" : "Sign In"} <Arrow />
            </Button>
          </form>

          <p className="mt-8 text-center text-[0.8125rem] text-fg-700">
            New to ExaminerAI?{" "}
            <Link to="/signup" className="font-medium text-indigo-600 hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
