"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, MessageSquare, Route, Sparkles } from "lucide-react";
import { ReactNode } from "react";

import { Card, OriAvatar } from "./ui";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "Analisis en chat", icon: MessageSquare },
  { href: "/action-plan", label: "Plan", icon: Route },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="relative min-h-screen bg-background lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_24%),radial-gradient(circle_at_bottom_left,rgba(14,165,233,0.16),transparent_24%),linear-gradient(135deg,rgba(255,255,255,0.03),transparent_28%)]" />
      <aside className="relative border-b border-white/10 bg-sidebar/78 p-5 backdrop-blur-2xl lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="mb-8 flex items-center gap-3">
          <OriAvatar variant="greeting" size="sm" />
          <div>
            <div className="text-lg font-semibold">OrientaIA</div>
            <div className="text-xs text-muted">Ori te acompaña paso a paso</div>
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
                    ? "border border-cyan-300/25 bg-cyan-300/12 text-cyan-50 shadow-glow"
                    : "border border-transparent text-muted hover:border-white/10 hover:bg-white/6 hover:text-text"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Card className="mt-8 p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium text-text">
            <Sparkles className="h-4 w-4 text-cyan-300" />
            Consejo de Ori
          </div>
          <p className="mt-2 text-sm text-muted">
            Usa el chat para explorar afinidades, revisar el porqué de las recomendaciones y replantear tu plan.
          </p>
        </Card>
      </aside>
      <main className="relative min-w-0 p-4 md:p-6">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="text-sm text-cyan-300">Asistente conversacional para orientación vocacional</div>
            <h1 className="text-3xl font-semibold tracking-tight text-balance">Habla primero, analiza después</h1>
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
