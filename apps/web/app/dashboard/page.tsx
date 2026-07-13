"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Bot, ChartColumn, ClipboardList, Route, Star } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/shell";
import { Card, Button } from "@/components/ui";
import { api } from "@/lib/api";
import type { ActionPlan, Profile, RecommendationRun } from "@/lib/types";

const RESET_PENDING_STORAGE_KEY = "orientaia-analysis-reset-pending";

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
      {!latest ? (
        <Card className="p-6">
          <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
            <div>
              <div className="mb-2 text-sm text-cyan-300">Analisis pendiente</div>
              <h2 className="text-3xl font-semibold">
                {profile?.preferred_name ? `${profile.preferred_name}, primero conversemos.` : "Primero conversemos."}
              </h2>
              <p className="mt-3 max-w-2xl text-sm text-muted">
                Este panel solo muestra resultados cuando OrientaIA termina una entrevista guiada en el chat.
                Ahi capturamos intereses, habilidades, preferencias y luego generamos recomendaciones y plan.
              </p>
              <div className="mt-5">
                <Link href="/chat">
                  <Button className="inline-flex items-center gap-2">
                    Iniciar analisis en chat <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            <Card className="p-5">
              <div className="mb-3 flex items-center justify-between text-sm text-muted">
                Estado del perfil <ClipboardList className="h-4 w-4" />
              </div>
              <div className="text-3xl font-semibold">Sin analizar</div>
              <p className="mt-2 text-sm text-muted">
                Aun no hay puntajes ni plan porque el analisis todavia no se ha completado.
              </p>
            </Card>
          </div>
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
