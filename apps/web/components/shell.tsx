"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, LayoutDashboard, MessageSquare, Route } from "lucide-react";
import { ReactNode } from "react";

import { Card } from "./ui";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "Analisis en chat", icon: MessageSquare },
  { href: "/action-plan", label: "Plan", icon: Route },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="relative min-h-screen bg-background lg:grid lg:grid-cols-[260px_minmax(0,1fr)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(47,128,255,0.18),transparent_22%),radial-gradient(circle_at_bottom_left,rgba(24,215,223,0.14),transparent_20%)]" />
      <aside className="relative border-b border-border bg-sidebar/86 p-5 backdrop-blur lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/15 text-cyan-300">
            <Compass className="h-5 w-5" />
          </div>
          <div>
            <div className="text-lg font-semibold">OrientaIA</div>
            <div className="text-xs text-muted">Analisis guiado por conversacion</div>
          </div>
        </div>
        <nav className="space-y-2">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                  active
                    ? "border border-cyan-400/20 bg-cyan-400/12 text-cyan-100 shadow-[0_0_0_1px_rgba(24,215,223,0.08)]"
                    : "border border-transparent text-muted hover:border-white/8 hover:bg-white/5 hover:text-text"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Card className="mt-8 p-4">
          <div className="text-sm font-medium text-text">Consejo vocacional</div>
          <p className="mt-2 text-sm text-muted">
            Usa el chat para explorar afinidades, revisar el porqué de las recomendaciones y replantear tu plan.
          </p>
        </Card>
      </aside>
      <main className="relative min-w-0 p-4 md:p-6">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="text-sm text-cyan-300">Asistente conversacional para orientacion vocacional</div>
            <h1 className="text-3xl font-semibold tracking-tight text-balance">Habla primero, analiza despues</h1>
          </div>
          <Card className="w-full max-w-md p-3">
            <div className="text-sm text-muted">
              Datos de demostracion con fines academicos. Las recomendaciones son orientativas y no reemplazan
              acompanamiento humano.
            </div>
          </Card>
        </div>
        {children}
      </main>
    </div>
  );
}
