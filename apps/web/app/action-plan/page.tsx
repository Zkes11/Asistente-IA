"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/shell";
import { Button, Card, GlassCard, OriAvatar } from "@/components/ui";
import { api } from "@/lib/api";
import type { ActionPlan, ChatSession, RecommendationRun } from "@/lib/types";

const ACTIVE_PLAN_STORAGE_KEY = "orientaia-active-plan-id";

function formatPlanDate(value: string) {
  return new Intl.DateTimeFormat("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function ActionPlanPage() {
  const [activePlanId, setActivePlanId] = useState<string | null>(null);

  const plansQuery = useQuery<ActionPlan[]>({
    queryKey: ["plans"],
    queryFn: api.listActionPlans,
  });
  const recommendationsQuery = useQuery<RecommendationRun[]>({
    queryKey: ["recommendations"],
    queryFn: api.listRecommendations,
  });
  const chatSessionsQuery = useQuery<ChatSession[]>({
    queryKey: ["chat-sessions"],
    queryFn: api.listChatSessions,
  });

  const latestRun = recommendationsQuery.data?.[0];
  const latestChatSession = chatSessionsQuery.data?.[0];

  const createMutation = useMutation({
    mutationFn: () => api.createActionPlan(latestRun?.id, latestChatSession?.id),
    onSuccess: async (plan) => {
      window.localStorage.setItem(ACTIVE_PLAN_STORAGE_KEY, plan.id);
      setActivePlanId(plan.id);
      await plansQuery.refetch();
    },
  });
  const deleteMutation = useMutation({
    mutationFn: (planId: string) => api.deleteActionPlan(planId),
    onSuccess: async () => {
      window.localStorage.removeItem(ACTIVE_PLAN_STORAGE_KEY);
      setActivePlanId(null);
      await plansQuery.refetch();
    },
  });

  useEffect(() => {
    setActivePlanId(window.localStorage.getItem(ACTIVE_PLAN_STORAGE_KEY));
  }, []);

  useEffect(() => {
    if (!plansQuery.data?.length) {
      return;
    }
    const exists = plansQuery.data.some((plan) => plan.id === activePlanId);
    if (!exists) {
      const nextPlanId = plansQuery.data[0].id;
      setActivePlanId(nextPlanId);
      window.localStorage.setItem(ACTIVE_PLAN_STORAGE_KEY, nextPlanId);
    }
  }, [activePlanId, plansQuery.data]);

  const plans = useMemo(() => plansQuery.data ?? [], [plansQuery.data]);
  const activePlan = useMemo(
    () => plans.find((plan) => plan.id === activePlanId) ?? plans[0] ?? null,
    [activePlanId, plans],
  );

  return (
    <AppShell>
      {!latestRun && !plans.length ? (
        <GlassCard className="p-6">
          <div className="grid gap-6 md:grid-cols-[minmax(0,1fr)_240px] md:items-center">
            <div>
              <div className="mb-2 text-sm text-cyan-300">Plan bloqueado</div>
              <h2 className="text-3xl font-semibold">Todavía no hay análisis suficiente.</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
                El plan de accion se genera despues de completar la entrevista guiada en el chat. Primero debemos entender
                intereses, habilidades y preferencias.
              </p>
            </div>
            <OriAvatar variant="thinking" size="xl" className="mx-auto animate-float" />
          </div>
          <div className="mt-5">
            <Link href="/chat">
              <Button>Ir al chat de analisis</Button>
            </Link>
          </div>
        </GlassCard>
      ) : (
        <div className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
          <Card className="p-4">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <div className="text-sm text-cyan-300">Planes por chat</div>
                <div className="text-xl font-semibold">{plans.length ? `${plans.length} guardados` : "Sin planes"}</div>
              </div>
              {!plans.length && (
                <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creando..." : "Crear plan"}
                </Button>
              )}
            </div>
            <div className="space-y-3">
              {plans.map((plan) => (
                <button
                  key={plan.id}
                  onClick={() => {
                    setActivePlanId(plan.id);
                    window.localStorage.setItem(ACTIVE_PLAN_STORAGE_KEY, plan.id);
                  }}
                  className={`w-full rounded-2xl border p-4 text-left transition ${
                    plan.id === activePlan?.id
                      ? "border-cyan-400/25 bg-cyan-400/10"
                      : "border-white/8 bg-white/5 hover:border-white/15"
                  }`}
                >
                  <div className="text-sm font-medium text-text">{plan.title}</div>
                  <div className="mt-1 text-xs text-muted">{formatPlanDate(plan.created_at)}</div>
                  <div className="mt-2 line-clamp-3 text-xs text-muted">{plan.summary}</div>
                </button>
              ))}
              {!plans.length && (
                <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-muted">
                  Cuando cierres un analisis en el chat, aqui quedara un plan por cada conversacion.
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <GlassCard className="mb-5 overflow-hidden p-0">
              <div className="grid gap-5 p-5 md:grid-cols-[minmax(0,1fr)_200px] md:items-center">
                <div>
                  <div className="text-sm font-medium text-cyan-200">Excelente trabajo 🎉</div>
                  <h3 className="mt-2 text-2xl font-semibold">Ya tengo suficiente información para ayudarte a explorar caminos que encajan contigo.</h3>
                </div>
                <OriAvatar variant="celebrating" size="lg" className="mx-auto animate-float" />
              </div>
            </GlassCard>

            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold">{activePlan?.title ?? "Plan de accion"}</h2>
                <p className="text-sm text-muted">
                  {activePlan?.summary ?? "Selecciona un plan generado desde cualquiera de tus chats."}
                </p>
              </div>
              {latestRun && latestChatSession && (
                <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creando..." : "Crear plan del chat actual"}
                </Button>
              )}
            </div>

            {activePlan ? (
              <div className="space-y-4">
                <Card className="overflow-hidden p-0">
                  <div className="bg-[linear-gradient(135deg,rgba(14,165,233,0.20),rgba(34,211,238,0.12),rgba(139,92,246,0.10))] p-5">
                    <div className="text-xs uppercase tracking-wide text-cyan-100">Plan activo</div>
                    <div className="mt-2 text-xl font-semibold">{activePlan.title}</div>
                    <div className="mt-2 max-w-3xl text-sm text-[#d5e0ee]">{activePlan.summary}</div>
                    <div className="mt-3 text-xs text-cyan-100/90">
                      Este plan se armó desde un chat concreto. Cada conversación puede tener su propio plan.
                    </div>
                  </div>
                </Card>

                <div className="grid gap-4 md:grid-cols-2">
                  {activePlan.steps.map((step) => (
                    <Card key={step.id} className="p-5 transition duration-200 hover:-translate-y-0.5 hover:border-cyan-200/20">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-lg font-medium">{step.title}</div>
                        <div className="text-xs uppercase text-cyan-300">{step.priority}</div>
                      </div>
                      <p className="mt-2 text-sm text-muted">{step.description}</p>
                      <div className="mt-3 text-sm">Estado: {step.status}</div>
                      <div className="mt-3 h-2 rounded-full bg-white/10">
                        <div className="h-2 rounded-full bg-gradient-to-r from-blue to-primary" style={{ width: `${step.progress}%` }} />
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-sm text-muted">Todavia no hay un plan activo para mostrar.</div>
            )}
          </Card>
        </div>
      )}
    </AppShell>
  );
}
