import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, useState } from "react";

import { Arrow, Button, ButtonLink, Logo } from "@/components/kit";
import { clearUser, getUser, type AppUser } from "@/lib/examiner";
import { cn } from "@/lib/utils";

export function useAppUser() {
  const [user, setUserState] = useState<AppUser | null>(null);
  const [ready, setReady] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  useEffect(() => {
    setUserState(getUser());
    setReady(true);
  }, [pathname]);

  return { user, ready, signOut: () => { clearUser(); setUserState(null); } };
}

const MARKETING_LINKS = [
  { label: "Home", to: "/" },
  { label: "How It Works", to: "/", hash: "how-it-works" },
  { label: "Features", to: "/", hash: "features" },
  { label: "For Educators", to: "/", hash: "educators" },
  { label: "Pricing", to: "/", hash: "pricing" },
  { label: "About", to: "/", hash: "about" },
] as const;

export function MarketingNav({ tone = "dark" }: { tone?: "dark" | "light" }) {
  const { user, signOut } = useAppUser();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const light = tone === "light";

  return (
    <header className={cn("relative z-30", light ? "border-b border-line bg-background" : "")}>
      <nav className="container-page flex h-[72px] items-center justify-between gap-4" aria-label="Main">
        <Link to="/" aria-label="ExaminerAI home">
          <Logo tone={light ? "dark" : "light"} />
        </Link>

        <ul className="hidden items-center gap-7 lg:flex">
          {MARKETING_LINKS.map((l) => (
            <li key={l.label}>
              <Link
                to={l.to}
                hash={"hash" in l ? l.hash : undefined}
                className={cn(
                  "text-[0.8125rem] transition-colors duration-150",
                  light ? "text-fg-700 hover:text-fg-950" : "text-white/65 hover:text-white",
                )}
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-3 sm:flex">
          {user ? (
            <>
              <ButtonLink to="/history" size="sm" variant={light ? "ghost" : "outlineDark"}>
                History
              </ButtonLink>
              <ButtonLink to="/exam/configure" size="sm" variant={light ? "primary" : "onDark"}>
                New Examination
              </ButtonLink>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className={cn("text-[0.8125rem] font-medium", light ? "text-fg-700 hover:text-fg-950" : "text-white/75 hover:text-white")}
              >
                Sign In
              </Link>
              <ButtonLink to="/signup" size="sm" variant={light ? "primary" : "primary"}>
                Get Started
              </ButtonLink>
            </>
          )}
        </div>

        <button
          type="button"
          aria-label="Toggle navigation"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          className={cn(
            "grid h-10 w-10 place-items-center rounded-lg border lg:hidden",
            light ? "border-line text-fg-950" : "border-white/15 text-white",
          )}
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
            <path d="M2 5h14M2 9h14M2 13h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      </nav>

      {open ? (
        <div className={cn("border-t lg:hidden", light ? "border-line bg-background" : "border-white/10 bg-ink-950")}>
          <ul className="container-page flex flex-col py-4">
            {MARKETING_LINKS.map((l) => (
              <li key={l.label}>
                <Link
                  to={l.to}
                  hash={"hash" in l ? l.hash : undefined}
                  onClick={() => setOpen(false)}
                  className={cn("block py-2.5 text-sm", light ? "text-fg-700" : "text-white/70")}
                >
                  {l.label}
                </Link>
              </li>
            ))}
            <li className="mt-3 flex gap-3">
              {user ? (
                <>
                  <Button size="sm" variant="secondary" onClick={() => { signOut(); setOpen(false); }}>
                    Sign out
                  </Button>
                  <Button size="sm" onClick={() => { setOpen(false); navigate({ to: "/exam/configure" }); }}>
                    New Examination <Arrow />
                  </Button>
                </>
              ) : (
                <>
                  <ButtonLink to="/login" size="sm" variant="secondary" onClick={() => setOpen(false)}>
                    Sign In
                  </ButtonLink>
                  <ButtonLink to="/signup" size="sm" onClick={() => setOpen(false)}>
                    Get Started
                  </ButtonLink>
                </>
              )}
            </li>
          </ul>
        </div>
      ) : null}
    </header>
  );
}

/** Compact navigation for authenticated, non-examination pages. */
export function AppNav() {
  const { user, signOut } = useAppUser();
  const navigate = useNavigate();

  return (
    <header className="border-b border-line bg-background">
      <nav className="container-page flex h-[68px] items-center justify-between gap-4" aria-label="Application">
        <Link to="/" aria-label="ExaminerAI home">
          <Logo />
        </Link>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link to="/history" className="hidden text-[0.8125rem] text-fg-700 hover:text-fg-950 sm:block" activeProps={{ className: "text-fg-950 font-medium" }}>
            Examination History
          </Link>
          <ButtonLink to="/exam/configure" size="sm">
            New Examination
          </ButtonLink>
          {user ? (
            <button
              type="button"
              onClick={() => { signOut(); navigate({ to: "/" }); }}
              title={`Signed in as ${user.email} — sign out`}
              className="grid h-9 w-9 place-items-center rounded-pill border border-line bg-surface-100 text-[0.6875rem] font-semibold text-fg-700"
            >
              {user.name.slice(0, 2).toUpperCase()}
            </button>
          ) : null}
        </div>
      </nav>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-line bg-background">
      <div className="container-page flex flex-col gap-8 py-12 md:flex-row md:items-center md:justify-between">
        <Logo />
        <ul className="flex flex-wrap gap-x-7 gap-y-3">
          {["About", "Blog", "Careers", "Privacy", "Terms", "Contact"].map((l) => (
            <li key={l}>
              <Link to="/" className="text-[0.8125rem] text-fg-700 hover:text-fg-950">
                {l}
              </Link>
            </li>
          ))}
        </ul>
        <p className="text-[0.8125rem] text-fg-500">Build a deeper understanding.</p>
      </div>
    </footer>
  );
}

/** Client-side guard for authenticated pages. */
export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, ready } = useAppUser();
  const navigate = useNavigate();

  useEffect(() => {
    if (ready && !user) navigate({ to: "/login" });
  }, [ready, user, navigate]);

  if (!ready) {
    return (
      <div className="container-page flex min-h-[50vh] items-center justify-center">
        <span className="soft-pulse text-sm text-fg-500">Preparing your examination workspace…</span>
      </div>
    );
  }
  if (!user) return null;
  return <>{children}</>;
}
