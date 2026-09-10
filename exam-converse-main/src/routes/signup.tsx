import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Arrow, Button, Field, Input, Logo } from "@/components/kit";
import { setUser } from "@/lib/examiner";

export const Route = createFileRoute("/signup")({
  head: () => ({
    meta: [
      { title: "Create your account — ExaminerAI" },
      { name: "description", content: "Create an ExaminerAI account and sit your first conversational examination." },
      { property: "og:title", content: "Create your account — ExaminerAI" },
      { property: "og:description", content: "Create an ExaminerAI account and sit your first conversational examination." },
    ],
  }),
  component: SignupPage,
});

function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-16">
      <div className="w-full max-w-md">
        <Link to="/" aria-label="ExaminerAI home">
          <Logo />
        </Link>
        <h1 className="mt-9 font-display text-[2.25rem] leading-tight tracking-tight text-fg-950">Create your account</h1>
        <p className="mt-2 text-sm text-fg-700">One account. Every examination, evaluated and remembered.</p>

        <form
          className="surface-card mt-8 space-y-5 p-7"
          onSubmit={(e) => {
            e.preventDefault();
            if (!form.name || !form.email || !form.password) {
              setError("Fill in every field to create your account.");
              return;
            }
            if (form.password !== form.confirm) {
              setError("Passwords do not match.");
              return;
            }
            setError(null);
            setUser({ name: form.name, email: form.email });
            navigate({ to: "/exam/configure" });
          }}
        >
          <Field label="Full name" htmlFor="name">
            <Input id="name" autoComplete="name" placeholder="Ada Lovelace" value={form.name} onChange={set("name")} />
          </Field>
          <Field label="Email" htmlFor="email">
            <Input id="email" type="email" autoComplete="email" placeholder="you@university.edu" value={form.email} onChange={set("email")} />
          </Field>
          <Field label="Password" htmlFor="password" hint="At least 8 characters.">
            <Input id="password" type="password" autoComplete="new-password" placeholder="••••••••" value={form.password} onChange={set("password")} />
          </Field>
          <Field label="Confirm password" htmlFor="confirm">
            <Input id="confirm" type="password" autoComplete="new-password" placeholder="••••••••" value={form.confirm} onChange={set("confirm")} />
          </Field>

          {error ? (
            <p role="alert" className="text-[0.8125rem] text-error">
              {error}
            </p>
          ) : null}

          <Button type="submit" size="lg" className="w-full">
            Create Account <Arrow />
          </Button>
        </form>

        <p className="mt-8 text-center text-[0.8125rem] text-fg-700">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-indigo-600 hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </main>
  );
}
