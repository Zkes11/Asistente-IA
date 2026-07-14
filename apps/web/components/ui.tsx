"use client";

import { clsx } from "clsx";
import React, { ComponentProps, useState } from "react";

export type OriVariant = "greeting" | "thinking" | "analyzing" | "celebrating";

const oriSrcByVariant: Record<OriVariant, string> = {
  greeting: "/ori/ori-greeting.png",
  thinking: "/ori/ori-thinking.png",
  analyzing: "/ori/ori-analyzing.png",
  celebrating: "/ori/ori-celebrating.png",
};

export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={clsx(
        "rounded-panel border border-white/10 bg-surface/80 shadow-panel backdrop-blur-xl",
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
        "rounded-2xl border border-cyan-300/30 bg-gradient-to-r from-blue to-primary px-5 py-2.5 text-sm font-semibold text-slate-950 shadow-glow transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_0_44px_rgba(34,211,238,0.26)] focus:outline-none focus:ring-2 focus:ring-cyan-300/60 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0",
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

export function GlassCard({ className, ...props }: ComponentProps<"div">) {
  return (
    <Card
      className={clsx(
        "relative overflow-hidden bg-white/[0.055] before:pointer-events-none before:absolute before:inset-x-[-30%] before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-cyan-200/70 before:to-transparent",
        className,
      )}
      {...props}
    />
  );
}

export function OriAvatar({
  variant = "greeting",
  size = "md",
  className,
}: {
  variant?: OriVariant;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}) {
  const [imageFailed, setImageFailed] = useState(false);
  const sizeClasses = {
    sm: "h-12 w-12",
    md: "h-20 w-20",
    lg: "h-36 w-36 md:h-44 md:w-44",
    xl: "h-52 w-52 md:h-64 md:w-64",
  };

  return (
    <div
      className={clsx(
        "relative flex shrink-0 items-center justify-center overflow-visible rounded-[32px]",
        sizeClasses[size],
        className,
      )}
      aria-label={`Ori ${variant}`}
    >
      {!imageFailed ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={oriSrcByVariant[variant]}
          alt={`Ori ${variant}`}
          className="h-full w-full object-contain drop-shadow-[0_24px_50px_rgba(34,211,238,0.25)]"
          onError={() => setImageFailed(true)}
        />
      ) : (
        <div className="relative h-[72%] w-[72%] rounded-[32%] border border-cyan-100/30 bg-slate-950/70">
          <div className="absolute left-1/2 top-[18%] h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-cyan-200 shadow-[0_0_12px_rgba(34,211,238,0.9)]" />
          <div className="absolute left-[23%] top-[40%] h-2 w-2 rounded-full bg-cyan-200" />
          <div className="absolute right-[23%] top-[40%] h-2 w-2 rounded-full bg-cyan-200" />
          <div className="absolute bottom-[24%] left-1/2 h-1 w-8 -translate-x-1/2 rounded-full bg-cyan-200/80" />
        </div>
      )}
    </div>
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
