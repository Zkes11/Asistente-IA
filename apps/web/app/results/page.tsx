"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

import { AppShell } from "@/components/shell";
import { Button, Card } from "@/components/ui";
import { api } from "@/lib/api";
import type { RecommendationRun } from "@/lib/types";

export default function ResultsPage() {
  const runsQuery = useQuery<RecommendationRun[]>({ queryKey: ["runs"], queryFn: api.listRecommendations });
  const generateMutation = useMutation({
    mutationFn: api.generateRecommendations,
    onSuccess: () => runsQuery.refetch(),
  });
  const latest = runsQuery.data?.[0];

  return (
    <AppShell>
      <div className="space-y-4">
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Resultados</h2>
              <p className="text-sm text-muted">
                Puntaje de compatibilidad, confianza, evidencia estructurada y factores de desarrollo.
              </p>
            </div>
            <Button onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
              Generar recomendaciones
            </Button>
          </div>
          {latest ? (
            <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <Card className="p-4">
                    <div className="text-sm text-muted">Puntaje general</div>
                    <div className="mt-2 text-3xl font-semibold">{latest.compatibility_score}</div>
                  </Card>
                  <Card className="p-4">
                    <div className="text-sm text-muted">Confianza</div>
                    <div className="mt-2 text-3xl font-semibold capitalize">{latest.confidence_level}</div>
                  </Card>
                  <Card className="p-4">
                    <div className="text-sm text-muted">Version del modelo</div>
                    <div className="mt-2 text-lg font-semibold">{latest.model_version}</div>
                  </Card>
                </div>
                <Card className="h-80 p-4">
                  <div className="mb-4 text-lg font-medium">Top 5 programas</div>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={latest.recommendations}>
                      <XAxis dataKey="program_slug" hide />
                      <YAxis />
                      <Bar dataKey="compatibility_score" fill="#18d7df" radius={8} />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </div>
              <Card className="p-5">
                <div className="mb-4 text-lg font-medium">Explicacion estructurada</div>
                <div className="space-y-4">
                  {latest.recommendations.map((item: RecommendationRun["recommendations"][number]) => (
                    <div key={item.id} className="rounded-2xl border border-border bg-white/5 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-lg font-medium">{item.program_slug.replaceAll("-", " ")}</div>
                        <div className="text-sm text-cyan-200">{item.compatibility_score}</div>
                      </div>
                      <div className="mt-3 text-sm text-muted">{item.supporting_factors.join(" ")}</div>
                      <div className="mt-3 text-sm text-amber-200">{item.development_factors[0]}</div>
                      <div className="mt-3 text-xs text-muted">
                        Reglas: {item.triggered_rules.map((rule) => String(rule["rule_id"] ?? "")).join(", ") || "Sin reglas destacadas"}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ) : (
            <div className="text-sm text-muted">Aun no has generado recomendaciones.</div>
          )}
        </Card>
      </div>
    </AppShell>
  );
}
