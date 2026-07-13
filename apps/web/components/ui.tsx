"use client";

import { clsx } from "clsx";
import React, { ComponentProps } from "react";

export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={clsx(
        "rounded-panel border border-border bg-surface/92 shadow-panel backdrop-blur-sm",
        className,
      )}
      {...props}
    />
  );
}

export function Button({ className, ...props }: ComponentProps<"button">) {
  return (
    <button
      className={clsx(
        "rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-medium text-text transition duration-200 hover:border-cyan-300/50 hover:bg-cyan-400/20 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export function Input(props: ComponentProps<"input">) {
  return (
    <input
      className="w-full rounded-xl border border-border bg-white/5 px-3 py-2 text-sm text-text outline-none transition placeholder:text-muted focus:border-cyan-300 focus:bg-white/8"
      {...props}
    />
  );
}

export function Textarea(props: ComponentProps<"textarea">) {
  return (
    <textarea
      className="min-h-[96px] w-full resize-y rounded-xl border border-border bg-white/5 px-3 py-3 text-sm text-text outline-none transition placeholder:text-muted focus:border-cyan-300 focus:bg-white/8"
      {...props}
    />
  );
}

export function Select(props: ComponentProps<"select">) {
  return (
    <select
      className="w-full rounded-xl border border-border bg-white/5 px-3 py-2 text-sm text-text outline-none transition focus:border-cyan-300"
      {...props}
    />
  );
}
