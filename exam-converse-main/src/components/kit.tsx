import { Link } from "@tanstack/react-router";
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

/* ------------------------------- Logo ------------------------------- */

export function Logo({ tone = "dark", className }: { tone?: "dark" | "light"; className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span className="grid h-7 w-7 shrink-0 grid-cols-2 gap-[3px] rounded-md p-[5px]" aria-hidden="true"
        style={{ background: "color-mix(in oklab, var(--indigo-600) 14%, transparent)" }}>
        <i className="block rounded-[2px] bg-indigo-600" />
        <i className="block rounded-[2px] bg-violet-500 opacity-70" />
        <i className="block rounded-[2px] bg-violet-500 opacity-70" />
        <i className="block rounded-[2px] bg-indigo-600" />
      </span>
      <span className={cn("text-[1.0625rem] font-semibold tracking-tight", tone === "light" ? "text-white" : "text-fg-950")}>
        Examiner<span className="text-indigo-500">AI</span>
      </span>
    </span>
  );
}

/* ------------------------------ Button ------------------------------ */

type Variant = "primary" | "secondary" | "ghost" | "onDark" | "outlineDark";
type Size = "sm" | "md" | "lg";

const base =
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-[transform,background-color,box-shadow,color] duration-200 ease-[cubic-bezier(0.22,1,0.36,1)] hover:-translate-y-px active:translate-y-0 active:scale-[0.985] disabled:pointer-events-none disabled:opacity-50";

const variants: Record<Variant, string> = {
  primary: "bg-indigo-600 text-white shadow-xs hover:bg-indigo-500 hover:shadow-sm",
  secondary: "border border-line bg-background text-fg-950 hover:bg-surface-100",
  ghost: "text-fg-700 hover:bg-surface-100 hover:text-fg-950",
  onDark: "bg-white text-ink-950 hover:bg-surface-100",
  outlineDark: "border border-white/20 bg-white/5 text-white hover:bg-white/10",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3.5 text-[0.8125rem]",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-[0.9375rem]",
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button className={cn(base, variants[variant], sizes[size], className)} {...props} />;
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: React.ComponentProps<typeof Link> & { variant?: Variant; size?: Size }) {
  return (
    <Link className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </Link>
  );
}

/* ------------------------------ Surfaces ---------------------------- */

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn("surface-card p-6", className)}>{children}</div>;
}

export function Badge({
  tone = "neutral",
  children,
  className,
}: {
  tone?: "neutral" | "indigo" | "success" | "warning" | "error" | "dark";
  children: ReactNode;
  className?: string;
}) {
  const tones = {
    neutral: "bg-surface-100 text-fg-700 border-line",
    indigo: "border-transparent text-indigo-600",
    success: "border-transparent text-success",
    warning: "border-transparent text-warning",
    error: "border-transparent text-error",
    dark: "border-white/15 bg-white/5 text-white/80",
  } as const;
  const bg =
    tone === "indigo"
      ? { background: "color-mix(in oklab, var(--indigo-600) 10%, transparent)" }
      : tone === "success"
        ? { background: "color-mix(in oklab, var(--success) 12%, transparent)" }
        : tone === "warning"
          ? { background: "color-mix(in oklab, var(--warning) 14%, transparent)" }
          : tone === "error"
            ? { background: "color-mix(in oklab, var(--error) 12%, transparent)" }
            : undefined;
  return (
    <span
      style={bg}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 text-[0.6875rem] font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  align = "center",
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "center" | "left";
}) {
  return (
    <div className={cn("max-w-2xl", align === "center" && "mx-auto text-center")}>
      {eyebrow ? <p className="eyebrow text-indigo-600">{eyebrow}</p> : null}
      <h2 className="mt-4 font-display text-[2.125rem] leading-[1.1] tracking-tight text-fg-950 sm:text-[2.75rem]">
        {title}
      </h2>
      {description ? <p className="mt-4 text-[0.9375rem] leading-relaxed text-fg-700">{description}</p> : null}
    </div>
  );
}

export function Divider({ className }: { className?: string }) {
  return <hr className={cn("border-0 border-t border-line", className)} />;
}

/* -------------------------------- Form ------------------------------ */

export function Field({
  label,
  hint,
  htmlFor,
  children,
}: {
  label: string;
  hint?: string;
  htmlFor: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={htmlFor} className="block text-[0.8125rem] font-medium text-fg-950">
        {label}
      </label>
      {children}
      {hint ? <p className="text-xs text-fg-500">{hint}</p> : null}
    </div>
  );
}

const control =
  "w-full rounded-lg border border-line bg-background px-3.5 py-2.5 text-sm text-fg-950 placeholder:text-fg-500 transition-colors duration-150 hover:border-fg-500/40 focus:border-indigo-600";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(control, "h-11", className)} {...props} />;
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(control, "min-h-28 resize-y leading-relaxed", className)} {...props} />;
}

export function Select({ className, children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(control, "h-11 appearance-none pr-9", className)} {...props}>
      {children}
    </select>
  );
}

/* ------------------------------ Feedback ---------------------------- */

export function Metric({ value, label, tone }: { value: string; label: string; tone?: "indigo" }) {
  return (
    <div>
      <p className={cn("font-display text-[2.25rem] leading-none tracking-tight", tone === "indigo" ? "text-indigo-600" : "text-fg-950")}>
        {value}
      </p>
      <p className="mt-2 text-[0.8125rem] text-fg-700">{label}</p>
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="surface-card flex flex-col items-center px-6 py-16 text-center">
      <h3 className="font-display text-2xl tracking-tight text-fg-950">{title}</h3>
      <p className="mt-2 max-w-sm text-sm text-fg-700">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-fg-500" role="status">
      <span className="soft-pulse h-1.5 w-1.5 rounded-full bg-indigo-600" />
      {label}
    </div>
  );
}

export function ScoreBar({ value }: { value: number }) {
  const tone = value >= 75 ? "var(--success)" : value >= 55 ? "var(--warning)" : "var(--error)";
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-pill bg-surface-200" role="presentation">
      <div className="h-full rounded-pill transition-[width] duration-500" style={{ width: `${value}%`, background: tone }} />
    </div>
  );
}

export function AIIndicator({ tone = "light" }: { tone?: "light" | "dark" }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "grid h-8 w-8 shrink-0 place-items-center rounded-lg border text-[0.625rem] font-semibold tracking-wider",
        tone === "dark" ? "border-white/15 bg-white/10 text-white" : "border-line text-indigo-600",
      )}
      style={tone === "light" ? { background: "color-mix(in oklab, var(--indigo-600) 8%, transparent)" } : undefined}
    >
      AI
    </span>
  );
}

export function Arrow() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M3 8h10m0 0-4-4m4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Check({ className }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true" className={className}>
      <path d="M3.5 8.5 6.5 11.5 12.5 4.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
