"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Bot, Brain, ChartColumn, ClipboardList, GraduationCap, Rocket, Route, Star, Target } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/shell";
import { Button, Card, GlassCard, OriAvatar } from "@/components/ui";
import { api } from "@/lib/api";
import type { ActionPlan, Profile, RecommendationRun } from "@/lib/types";

const RESET_PENDING_STORAGE_KEY = "orientaia-analysis-reset-pending";

const welcomeCards = [
  { title: "Descubrir intereses", icon: Target, emoji: "🎯" },
  { title: "Conocer fortalezas", icon: Brain, emoji: "🧠" },
  { title: "Explorar carreras", icon: GraduationCap, emoji: "📚" },
  { title: "Construir un plan", icon: Rocket, emoji: "🚀" },
];

export default function DashboardPage() {
  const [resetPending, setResetPending] = useState(false);
  const profileQuery = useQuery<Profile>({ queryKey: ["profile"], queryFn: api.getProfile });
  const recommendationsQuery = useQuery<RecommendationRun[]>({
    queryKey: ["recommendations"],
    queryFn: api.listRecommendations,
  });
  const planQuery = useQuery<ActionPlan | null>({ queryKey: ["plan"], queryFn: api.currentActionPlan });
  const profile = profileQuery.data;
  const latest = !resetPending ? recommendationsQuery.data?.[0] : undefined;
  const plan = planQuery.data;

  useEffect(() => {
    setResetPending(window.localStorage.getItem(RESET_PENDING_STORAGE_KEY) === "true");
  }, []);

  return (
    <AppShell>
      <section className="mb-5 space-y-5">
        <GlassCard className="overflow-hidden p-0">
          <div className="relative grid gap-8 p-6 md:p-8 lg:grid-cols-[minmax(0,1fr)_260px] lg:items-center">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_75%_20%,rgba(34,211,238,0.18),transparent_28%),linear-gradient(135deg,rgba(14,165,233,0.13),rgba(139,92,246,0.08))]" />
            <div className="relative">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-200/20 bg-cyan-300/10 px-3 py-1 text-xs font-medium text-cyan-100">
                <SparkleDot /> Bienvenida a OrientaIA
              </div>
              <h2 className="text-4xl font-bold tracking-tight text-balance md:text-5xl">Hola, soy Ori 👋</h2>
              <p className="mt-4 text-xl font-medium text-cyan-100">Tu asistente de orientación vocacional.</p>
              <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">
                Voy a acompañarte mientras descubrimos qué áreas, carreras y oportunidades pueden encajar mejor contigo.
              </p>
              <div className="mt-7">
                <Link href="/chat">
                  <Button className="inline-flex items-center gap-2 px-6 py-3 text-base">
                    Comenzar conversación <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative mx-auto flex flex-col items-center gap-3">
              <OriAvatar variant="greeting" size="xl" className="animate-float" />
              <div className="rounded-full border border-white/10 bg-white/8 px-4 py-2 text-sm text-cyan-100 shadow-glow">
                Ori está listo para ayudarte
              </div>
            </div>
          </div>
        </GlassCard>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {welcomeCards.map((item) => {
            const Icon = item.icon;
            return (
              <GlassCard key={item.title} className="group p-5 transition duration-200 hover:-translate-y-1 hover:border-cyan-200/25">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/8 text-2xl">
                  <span aria-hidden>{item.emoji}</span>
                </div>
                <div className="flex items-center gap-2 text-lg font-semibold">
                  <Icon className="h-4 w-4 text-cyan-300" />
                  {item.title}
                </div>
                <p className="mt-2 text-sm text-muted">Una guía visual para avanzar con claridad, sin agregar funciones nuevas.</p>
              </GlassCard>
            );
          })}
        </div>
      </section>

      {!latest ? (
        <Card className="p-5">
          <div className="mb-3 flex items-center justify-between text-sm text-muted">
            Estado del perfil <ClipboardList className="h-4 w-4" />
          </div>
          <div className="text-2xl font-semibold">Sin analizar</div>
          <p className="mt-2 text-sm text-muted">
            Aún no hay puntajes ni plan porque el análisis todavía no se ha completado.
          </p>
        </Card>
      ) : (
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <section className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="p-5">
              <div className="mb-3 flex items-center justify-between text-sm text-muted">
                Progreso general <ClipboardList className="h-4 w-4" />
              </div>
              <div className="text-3xl font-semibold">100%</div>
              <p className="mt-2 text-sm text-muted">Analisis conversacional, ranking y plan.</p>
            </Card>
            <Card className="p-5">
              <div className="mb-3 flex items-center justify-between text-sm text-muted">
                Puntaje promedio <ChartColumn className="h-4 w-4" />
              </div>
              <div className="text-3xl font-semibold">{latest?.compatibility_score ?? 0}</div>
              <p className="mt-2 text-sm text-muted">Compatibilidad del resultado mas reciente.</p>
            </Card>
            <Card className="p-5">
              <div className="mb-3 flex items-center justify-between text-sm text-muted">
                Confianza <Star className="h-4 w-4" />
              </div>
              <div className="text-3xl font-semibold capitalize">{latest?.confidence_level ?? "sin datos"}</div>
              <p className="mt-2 text-sm text-muted">Si es baja, el sistema sugiere ampliar informacion.</p>
            </Card>
          </div>
          <Card className="p-6">
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <div className="text-sm text-cyan-300">Resumen del estudiante</div>
                <h2 className="text-2xl font-semibold">
                  {profile?.preferred_name ? `Hola, ${profile.preferred_name}` : "Completa tu perfil inicial"}
                </h2>
              </div>
              <Link href="/chat">
                <Button className="inline-flex items-center gap-2">
                  Reabrir analisis en chat <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-border bg-white/5 p-4">
                <div className="text-xs uppercase tracking-wide text-muted">Objetivo</div>
                <div className="mt-2 text-lg">{profile?.goal ?? "Explorar"}</div>
              </div>
              <div className="rounded-2xl border border-border bg-white/5 p-4">
                <div className="text-xs uppercase tracking-wide text-muted">Areas conocidas</div>
                <div className="mt-2 text-lg">{profile?.known_areas?.join(", ") || "Aun no registradas"}</div>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Vista previa de recomendaciones</h2>
              <Link href="/results" className="text-sm text-cyan-300">
                Ver detalle
              </Link>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {latest?.recommendations?.slice(0, 4).map((item: RecommendationRun["recommendations"][number]) => (
                <div key={item.id} className="rounded-2xl border border-border bg-white/5 p-4">
                  <div className="text-lg font-medium">{item.program_slug.replaceAll("-", " ")}</div>
                  <div className="mt-2 text-sm text-muted">Puntaje de compatibilidad: {item.compatibility_score}</div>
                  <div className="mt-3 text-sm text-cyan-200">{item.supporting_factors[0]}</div>
                </div>
              )) ?? <div className="text-sm text-muted">Aun no hay resultados generados.</div>}
            </div>
          </Card>
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Siguientes pasos sugeridos</h2>
              <Link href="/action-plan" className="text-sm text-cyan-300">
                Ver plan
              </Link>
            </div>
            {plan ? (
              <div className="grid gap-3 md:grid-cols-2">
                {plan.steps.slice(0, 4).map((step) => (
                  <div key={step.id} className="rounded-2xl border border-border bg-white/5 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-base font-medium">{step.title}</div>
                      <div className="text-xs uppercase text-cyan-300">{step.priority}</div>
                    </div>
                    <div className="mt-2 text-sm text-muted">{step.description}</div>
                    <div className="mt-3 text-xs text-muted">Estado: {step.status}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted">
                El analisis ya existe, pero todavia no has creado el plan de accion.
              </div>
            )}
          </Card>
        </section>
        <aside className="space-y-4">
          <Card className="p-5">
            <div className="mb-3 flex items-center gap-2 text-cyan-300">
              <Bot className="h-4 w-4" />
              Chat rapido
            </div>
            <p className="text-sm text-muted">
              Pide explicaciones, compara opciones o solicita consejo vocacional.
            </p>
            <Link href="/chat" className="mt-4 inline-block text-sm text-cyan-200">
              Continuar conversacion
            </Link>
          </Card>
          <Card className="p-5">
            <div className="mb-2 flex items-center gap-2 text-sm text-muted">
              <Route className="h-4 w-4" />
              Proximas acciones
            </div>
            <ul className="space-y-3 text-sm">
              <li>Revisar por que el top 3 encaja contigo.</li>
              <li>Contrastar opciones cercanas antes de decidir.</li>
              <li>Usar el plan para convertir hallazgos en pasos concretos.</li>
            </ul>
          </Card>
        </aside>
      </div>
      )}
    </AppShell>
  );
}

function SparkleDot() {
  return <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.9)]" />;
}
