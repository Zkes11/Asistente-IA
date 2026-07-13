"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/shell";
import { Button, Card, Input } from "@/components/ui";
import { api } from "@/lib/api";
import type { Program } from "@/lib/types";

export default function ProgramsPage() {
  const [filter, setFilter] = useState("");
  const [compare, setCompare] = useState<string[]>([]);
  const programsQuery = useQuery<Program[]>({ queryKey: ["programs"], queryFn: api.listPrograms });
  const compareMutation = useMutation({ mutationFn: api.comparePrograms });
  const filtered = useMemo(
    () =>
      (programsQuery.data ?? []).filter((program) =>
        `${program.name} ${program.academic_area_slug}`.toLowerCase().includes(filter.toLowerCase()),
      ),
    [filter, programsQuery.data],
  );

  return (
    <AppShell>
      <div className="space-y-4">
        <Card className="p-5">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <h2 className="text-2xl font-semibold">Exploracion de programas</h2>
            <Input placeholder="Buscar por nombre o area" value={filter} onChange={(e) => setFilter(e.target.value)} />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            {filtered.map((program) => (
              <Card key={program.slug} className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-medium">{program.name}</h3>
                    <p className="mt-2 text-sm text-muted">{program.short_description}</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={compare.includes(program.slug)}
                    onChange={(event) =>
                      setCompare((current) =>
                        event.target.checked
                          ? [...current, program.slug].slice(0, 3)
                          : current.filter((slug) => slug !== program.slug),
                      )
                    }
                  />
                </div>
                <div className="mt-4 text-sm text-cyan-200">{program.academic_area_slug}</div>
                <div className="mt-3 text-xs text-muted">Fuente: {program.source_name}</div>
                <div className="mt-2 text-xs text-amber-200">Datos de demostracion</div>
                <div className="mt-4">
                  <Button onClick={() => api.favoriteProgram(program.slug)}>Guardar</Button>
                </div>
              </Card>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Comparador</h2>
            <Button onClick={() => compareMutation.mutate(compare)} disabled={compare.length < 2}>
              Comparar seleccionados
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {(compareMutation.data ?? []).map((program: Program) => (
              <div key={program.slug} className="rounded-2xl border border-border bg-white/5 p-4">
                <div className="text-lg font-medium">{program.name}</div>
                <div className="mt-2 text-sm text-muted">{program.short_description}</div>
              </div>
            ))}
            {compareMutation.data?.length ? null : <div className="text-sm text-muted">Selecciona entre dos y tres programas.</div>}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
