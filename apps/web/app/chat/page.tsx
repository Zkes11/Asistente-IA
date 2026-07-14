"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { MessageSquarePlus, RefreshCcw, Send, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/shell";
import { Button, Card, GlassCard, OriAvatar, type OriVariant, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import type {
  ActionPlan,
  AssessmentAttempt,
  AssessmentSchema,
  ChatMessage,
  ChatSession,
  RecommendationRun,
} from "@/lib/types";

const ATTEMPT_STORAGE_KEY = "orientaia-chat-attempt-id";
const RESET_PENDING_STORAGE_KEY = "orientaia-analysis-reset-pending";
const ACTIVE_PLAN_STORAGE_KEY = "orientaia-active-plan-id";
const MAX_FOLLOW_UP_QUESTIONS = 4;

const AREA_KEYS = new Set([
  "interest_technology",
  "interest_social",
  "interest_design",
  "interest_health",
  "interest_business",
  "interest_data",
]);

const FEATURE_LABELS: Record<string, string> = {
  interest_technology: "afinidad con tecnologia",
  interest_social: "interes social",
  interest_design: "interes por diseno",
  interest_health: "interes por salud y ciencias naturales",
  interest_business: "interes por negocios",
  interest_data: "interes por datos",
  logical_reasoning: "razonamiento logico",
  communication: "comunicacion",
  empathy: "empatia",
  creativity: "creatividad",
  numerical_skill: "habilidad numerica",
  visual_thinking: "pensamiento visual",
  organization: "organizacion",
  teamwork_preference: "trabajo colaborativo",
  autonomy_preference: "autonomia",
  practical_learning: "aprendizaje practico",
  theoretical_learning: "aprendizaje teorico",
};

type AnswerValue = number | string;
type TranscriptMessage = { id: string; role: "assistant" | "user"; content: string; muted?: boolean };
type PromptState = { kind: "idle" | "broad" | "feature"; featureKey?: string; content: string };
type QuestionItem = AssessmentSchema["sections"][number]["questions"][number];

function getOriVariant({ isThinking, interviewCompleted }: { isThinking?: boolean; interviewCompleted?: boolean }): OriVariant {
  if (interviewCompleted) {
    return "celebrating";
  }
  if (isThinking) {
    return "thinking";
  }
  return "analyzing";
}

function ChatBubble({
  role,
  content,
  label,
  muted,
  oriVariant,
}: {
  role: "assistant" | "user";
  content: string;
  label: string;
  muted?: boolean;
  oriVariant: OriVariant;
}) {
  const isAssistant = role === "assistant";
  return (
    <div className={`flex max-w-4xl gap-3 ${isAssistant ? "mr-auto" : "ml-auto flex-row-reverse"}`}>
      {isAssistant && <OriAvatar variant={oriVariant} size="sm" className="mt-1" />}
      <div
        className={`relative rounded-[24px] border px-5 py-4 text-sm leading-6 shadow-panel ${
          isAssistant
            ? "border-cyan-300/16 bg-cyan-300/[0.085] text-slate-100"
            : "border-white/10 bg-white/[0.075] text-slate-50"
        }`}
      >
        <div className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">{label}</div>
        <div className={muted ? "text-slate-300" : "text-text"}>{content}</div>
      </div>
    </div>
  );
}

function createId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function buildCompletionAnswers(
  currentAnswers: Record<string, AnswerValue>,
  questions: QuestionItem[],
) {
  const completed = { ...currentAnswers };

  for (const question of questions) {
    if (completed[question.key] !== undefined) {
      continue;
    }
    completed[question.key] = 3;
  }

  return completed;
}

export default function ChatPage() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [resetPending, setResetPending] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([
    {
      id: createId("assistant"),
      role: "assistant",
      content:
        "Soy OrientaIA. Puedo conversar contigo para entender intereses, habilidades y preferencias antes de sugerir opciones y un plan orientativo.",
    },
  ]);
  const [promptState, setPromptState] = useState<PromptState>({ kind: "idle", content: "" });

  const sessionsQuery = useQuery<ChatSession[]>({ queryKey: ["chat-sessions"], queryFn: api.listChatSessions });
  const messagesQuery = useQuery<ChatMessage[]>({
    queryKey: ["chat-messages", activeSessionId],
    queryFn: () => api.listMessages(activeSessionId!),
    enabled: Boolean(activeSessionId),
  });
  const schemaQuery = useQuery<AssessmentSchema>({ queryKey: ["assessment"], queryFn: api.currentAssessment });
  const attemptQuery = useQuery<AssessmentAttempt>({
    queryKey: ["attempt", attemptId],
    queryFn: () => api.getAttempt(attemptId!),
    enabled: Boolean(attemptId),
  });
  const recommendationsQuery = useQuery<RecommendationRun[]>({
    queryKey: ["recommendations"],
    queryFn: api.listRecommendations,
  });
  const planQuery = useQuery<ActionPlan | null>({ queryKey: ["plan"], queryFn: api.currentActionPlan });
  const plansQuery = useQuery<ActionPlan[]>({ queryKey: ["plans"], queryFn: api.listActionPlans });

  const createSessionMutation = useMutation({
    mutationFn: () => api.createChatSession(`Chat #${(sessionsQuery.data?.length ?? 0) + 1}`),
    onSuccess: async (session: ChatSession) => {
      setActiveSessionId(session.id);
      await sessionsQuery.refetch();
    },
  });
  const createAttemptMutation = useMutation({
    mutationFn: api.createAttempt,
    onSuccess: (attempt: AssessmentAttempt) => {
      setAttemptId(attempt.id);
      setAnswers((attempt.answers as Record<string, AnswerValue>) ?? {});
    },
  });
  const saveMutation = useMutation({
    mutationFn: ({ id, nextAnswers }: { id: string; nextAnswers: Record<string, AnswerValue> }) =>
      api.patchAttempt(id, nextAnswers),
  });
  const sendMutation = useMutation({
    mutationFn: ({ sessionId, content }: { sessionId: string; content: string }) => api.sendMessage(sessionId, content),
    onSuccess: async () => {
      setDraft("");
      await messagesQuery.refetch();
    },
  });
  const deleteSessionMutation = useMutation({
    mutationFn: (sessionId: string) => api.deleteChatSession(sessionId),
    onSuccess: async () => {
      setActiveSessionId(null);
      await sessionsQuery.refetch();
    },
  });

  useEffect(() => {
    const storedAttemptId = window.localStorage.getItem(ATTEMPT_STORAGE_KEY);
    const storedResetPending = window.localStorage.getItem(RESET_PENDING_STORAGE_KEY) === "true";
    if (storedAttemptId) {
      setAttemptId(storedAttemptId);
    }
    setResetPending(storedResetPending);
  }, []);

  useEffect(() => {
    if (attemptId) {
      window.localStorage.setItem(ATTEMPT_STORAGE_KEY, attemptId);
    }
  }, [attemptId]);

  useEffect(() => {
    window.localStorage.setItem(RESET_PENDING_STORAGE_KEY, String(resetPending));
  }, [resetPending]);

  useEffect(() => {
    if (attemptQuery.data) {
      setAnswers((attemptQuery.data.answers as Record<string, AnswerValue>) ?? {});
    }
  }, [attemptQuery.data]);

  useEffect(() => {
    if (!activeSessionId && sessionsQuery.data?.length) {
      setActiveSessionId(sessionsQuery.data[0].id);
    }
  }, [activeSessionId, sessionsQuery.data]);

  useEffect(() => {
    if (sessionsQuery.isSuccess && !sessionsQuery.data.length && !activeSessionId && !createSessionMutation.isPending) {
      createSessionMutation.mutate();
    }
  }, [activeSessionId, createSessionMutation, sessionsQuery.data, sessionsQuery.isSuccess]);

  const questions = useMemo(
    () => schemaQuery.data?.sections.flatMap((section) => section.questions) ?? [],
    [schemaQuery.data],
  );
  const answeredQuestions = questions.filter((question) => answers[question.key] !== undefined);
  const followUpAnswerCount = useMemo(
    () => Object.keys(answers).filter((key) => !AREA_KEYS.has(key)).length,
    [answers],
  );
  const latestRecommendation = !resetPending ? recommendationsQuery.data?.[0] : undefined;
  const currentPlan = !resetPending ? planQuery.data : null;
  const interviewStarted = Boolean(attemptId) || answeredQuestions.length > 0 || promptState.kind !== "idle";
  const interviewCompleted = Boolean(latestRecommendation);
  const persistedTranscriptSet = useMemo(
    () => new Set(transcript.map((message) => `${message.role}:${message.content}`)),
    [transcript],
  );

  function appendAssistant(content: string, muted = false) {
    setTranscript((current) => [...current, { id: createId("assistant"), role: "assistant", content, muted }]);
  }

  function appendUser(content: string) {
    setTranscript((current) => [...current, { id: createId("user"), role: "user", content }]);
  }

  async function ensureActiveSessionId(preferredId?: string | null) {
    if (preferredId && sessionsQuery.data?.some((session) => session.id === preferredId)) {
      return preferredId;
    }
    if (activeSessionId && sessionsQuery.data?.some((session) => session.id === activeSessionId)) {
      return activeSessionId;
    }
    const listedSessionId = sessionsQuery.data?.[0]?.id;
    if (listedSessionId) {
      setActiveSessionId(listedSessionId);
      return listedSessionId;
    }
    const session = await createSessionMutation.mutateAsync();
    setActiveSessionId(session.id);
    return session.id;
  }

  async function appendAssistantMessages(messages: string[], muted = false, sessionId?: string | null) {
    for (const message of messages) {
      appendAssistant(message, muted);
      await persistAnalysisMessage("assistant", message, sessionId);
    }
  }

  async function persistAnalysisMessage(role: "assistant" | "user", content: string, sessionId?: string | null) {
    const resolvedSessionId = await ensureActiveSessionId(sessionId ?? activeSessionId);
    await api.appendChatMessage(resolvedSessionId, { role, content });
  }

  async function requestInterviewTurn(
    sessionId: string,
    nextAnswers: Record<string, AnswerValue>,
    options?: { mode?: "start" | "advance"; evaluatedFeatureKey?: string | null; evaluatedFeatureScore?: number | null },
  ) {
    const turn = await api.generateInterviewTurn(sessionId, {
      answers: Object.fromEntries(Object.entries(nextAnswers).map(([key, value]) => [key, Number(value)])),
      max_follow_up_questions: MAX_FOLLOW_UP_QUESTIONS,
      mode: options?.mode ?? "advance",
      evaluated_feature_key: options?.evaluatedFeatureKey ?? null,
      evaluated_feature_score: options?.evaluatedFeatureScore ?? null,
    });
    return turn;
  }

  function resetInterviewState() {
    window.localStorage.removeItem(ATTEMPT_STORAGE_KEY);
    setAttemptId(null);
    setAnswers({});
    setDraft("");
    setIsFinalizing(false);
    setPromptState({ kind: "idle", content: "" });
    setTranscript([
      {
        id: createId("assistant"),
        role: "assistant",
        content: "Empecemos de nuevo. El siguiente mensaje saldrá del motor conversacional actualizado.",
      },
    ]);
  }

  async function queueInterviewTurn(
    sessionId: string,
    nextAnswers: Record<string, AnswerValue>,
    targetAttemptId: string | null,
    options?: { mode?: "start" | "advance"; evaluatedFeatureKey?: string | null; evaluatedFeatureScore?: number | null },
  ) {
    setIsThinking(true);
    try {
      const turn = await requestInterviewTurn(sessionId, nextAnswers, options);
      const mergedAnswers = Object.keys(turn.merged_answers ?? {}).length
        ? (turn.merged_answers as Record<string, AnswerValue>)
        : { ...nextAnswers, ...(turn.answer_updates as Record<string, AnswerValue> | undefined) };
      setAnswers(mergedAnswers);
      if (targetAttemptId && turn.answer_updates && Object.keys(turn.answer_updates).length) {
        await saveMutation.mutateAsync({
          id: targetAttemptId,
          nextAnswers: turn.answer_updates as Record<string, AnswerValue>,
        });
      }
      const lastMessage = turn.messages[turn.messages.length - 1] ?? "";
      const nextPromptState: PromptState =
        turn.should_finalize || !turn.feature_key
          ? { kind: "idle", content: lastMessage }
          : { kind: "feature", featureKey: turn.feature_key, content: lastMessage };
      setPromptState(nextPromptState);
      await appendAssistantMessages(turn.messages, true, sessionId);
    } finally {
      setIsThinking(false);
    }
  }

  async function startInterview() {
    const sessionId = await ensureActiveSessionId(activeSessionId);
    const attempt = attemptId ? { id: attemptId } : await createAttemptMutation.mutateAsync();
    setResetPending(true);
    setAttemptId(attempt.id);
    await queueInterviewTurn(sessionId, {}, attempt.id, { mode: "start" });
    setPromptState({ kind: "broad", content: "" });
  }

  async function startNewConversation() {
    resetInterviewState();
    setResetPending(true);
    const session = await createSessionMutation.mutateAsync();
    setActiveSessionId(session.id);
  }

  async function removeCurrentConversation() {
    if (!activeSessionId) {
      return;
    }
    resetInterviewState();
    setResetPending(true);
    await deleteSessionMutation.mutateAsync(activeSessionId);
  }

  async function finalizeInterview() {
    if (!attemptId || isFinalizing) {
      return;
    }
    setIsFinalizing(true);
    try {
      const completedAnswers = buildCompletionAnswers(answers, questions);
      const missingAnswers = Object.fromEntries(
        Object.entries(completedAnswers).filter(([key]) => answers[key] === undefined),
      );
      if (Object.keys(missingAnswers).length) {
        await saveMutation.mutateAsync({ id: attemptId, nextAnswers: missingAnswers });
        setAnswers(completedAnswers);
      }
      await api.completeAttempt(attemptId);
      const run = await api.generateRecommendations();
      await recommendationsQuery.refetch();
      const generatedPlan = await api.createActionPlan(run.id, activeSessionId ?? undefined);
      window.localStorage.setItem(ACTIVE_PLAN_STORAGE_KEY, generatedPlan.id);
      await planQuery.refetch();
      await plansQuery.refetch();
      setResetPending(false);
      if (activeSessionId) {
        await api.sendMessage(activeSessionId, "explica mi resultado");
        await messagesQuery.refetch();
      }
      window.localStorage.removeItem(ATTEMPT_STORAGE_KEY);
      setAttemptId(null);
      setPromptState({ kind: "idle", content: "" });
    } finally {
      setIsFinalizing(false);
    }
  }

  async function handleConversationSubmit() {
    const content = draft.trim();
    if (!content) {
      return;
    }

    if (interviewCompleted) {
      appendUser(content);
      if (activeSessionId) {
        setIsThinking(true);
        try {
          await sendMutation.mutateAsync({ sessionId: activeSessionId, content });
        } finally {
          setIsThinking(false);
        }
      }
      return;
    }

    if (!attemptId) {
      return;
    }

    appendUser(content);
    setDraft("");
    const sessionId = await ensureActiveSessionId(activeSessionId);
    await persistAnalysisMessage("user", content, sessionId);

    await queueInterviewTurn(sessionId, answers, attemptId, {
      mode: "advance",
      evaluatedFeatureKey: promptState.kind === "feature" ? promptState.featureKey ?? null : null,
    });
  }

  return (
    <AppShell>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Card className="relative overflow-hidden p-0">
          <div className="border-b border-white/10 bg-[linear-gradient(135deg,rgba(14,165,233,0.20),rgba(34,211,238,0.12),rgba(139,92,246,0.10))] px-6 py-5">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-black/10 px-3 py-1 text-xs text-cyan-100">
              <Sparkles className="h-3.5 w-3.5" />
              Ori · asistente local de orientación
            </div>
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-3xl font-semibold">Conversemos antes de decidir</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-[#d3deed]">
                  La primera pregunta es abierta. Después, OrientaIA cambia la dirección de la entrevista según lo que
                  realmente aparece con más fuerza en tu perfil.
                </p>
              </div>
              <OriAvatar variant={getOriVariant({ isThinking, interviewCompleted })} size="lg" className="animate-float" />
            </div>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button onClick={() => startNewConversation()} disabled={createSessionMutation.isPending}>
                <MessageSquarePlus className="mr-2 h-4 w-4" />
                {createSessionMutation.isPending ? "Abriendo..." : "Nueva conversacion"}
              </Button>
              <Button
                className="border-white/10 bg-white/8"
                onClick={() => removeCurrentConversation()}
                disabled={!activeSessionId || deleteSessionMutation.isPending}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {deleteSessionMutation.isPending ? "Eliminando..." : "Eliminar conversacion"}
              </Button>
            </div>
          </div>

          <div className="flex min-h-[68vh] flex-col bg-slate-950/20 p-5">
            <div className="flex-1 space-y-5 overflow-auto pr-1">
              {transcript.map((message) => (
                    <ChatBubble
                    key={message.id}
                    role={message.role === "assistant" ? "assistant" : "user"}
                  content={message.content}
                  muted={message.muted}
                  label={message.role === "assistant" ? "Ori · OrientaIA" : "Tu respuesta"}
                  oriVariant={interviewCompleted ? "celebrating" : "analyzing"}
                />
              ))}

              {interviewCompleted &&
                messagesQuery.data
                  ?.filter((message) => !persistedTranscriptSet.has(`${message.role}:${message.content}`))
                  .map((message) => (
                  <ChatBubble
                    key={message.id}
                    role={message.role === "assistant" ? "assistant" : "user"}
                    content={message.content}
                    label={message.role === "assistant" ? "Ori · OrientaIA" : "Tu pregunta"}
                    oriVariant="celebrating"
                  />
                ))}

              {isThinking && (
                <div className="flex max-w-4xl gap-3">
                  <OriAvatar variant="thinking" size="sm" className="mt-1 animate-float" />
                  <div className="rounded-[24px] border border-cyan-300/16 bg-cyan-300/[0.085] px-5 py-4 text-sm shadow-panel">
                    <div className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Ori · OrientaIA</div>
                    <div className="flex items-center gap-3 text-[#d2dcf0]">
                    <span>Ori está pensando...</span>
                    <span className="flex items-center gap-1">
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:120ms]" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:240ms]" />
                    </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-5 space-y-4 border-t border-white/10 pt-4">
              {!interviewStarted && !interviewCompleted && (
                <div className="flex flex-wrap items-center gap-3">
                  <Button onClick={() => startInterview()} disabled={createAttemptMutation.isPending}>
                    <Sparkles className="mr-2 h-4 w-4" />
                    {createAttemptMutation.isPending ? "Preparando analisis..." : "Comenzar analisis"}
                  </Button>
                  <div className="text-sm text-muted">
                    Solo la primera pregunta es fija. Las demás cambian según tus afinidades y no insisten en áreas bajas.
                  </div>
                </div>
              )}

              {interviewStarted && !interviewCompleted && (
                <>
                  <GlassCard className="px-4 py-3 text-xs text-muted">
                    Señales registradas: {answeredQuestions.length}/{questions.length}. Profundización activa:{" "}
                    {promptState.featureKey ? FEATURE_LABELS[promptState.featureKey] ?? promptState.featureKey : "exploracion abierta"}.{" "}
                    Seguimiento hechos: {followUpAnswerCount}/{MAX_FOLLOW_UP_QUESTIONS}.
                  </GlassCard>
                  <Textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    placeholder={isThinking ? "OrientaIA está analizando..." : "Escribe con libertad. No necesitas responder con un número si no quieres."}
                    disabled={isThinking}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        void handleConversationSubmit();
                      }
                    }}
                  />
                  <div className="flex flex-wrap items-center gap-3">
                    <Button onClick={() => void handleConversationSubmit()} disabled={saveMutation.isPending || isThinking || !draft.trim()}>
                      <Send className="mr-2 h-4 w-4" />
                      {isThinking || saveMutation.isPending ? "Pensando..." : "Enviar respuesta"}
                    </Button>
                    {promptState.kind === "idle" && (
                      <Button className="bg-blue/20" onClick={() => finalizeInterview()} disabled={isFinalizing || isThinking}>
                        <RefreshCcw className="mr-2 h-4 w-4" />
                        {isFinalizing ? "Analizando perfil..." : "Procesar analisis"}
                      </Button>
                    )}
                  </div>
                </>
              )}

              {interviewCompleted && (
                <>
                  <div className="flex flex-wrap gap-3">
                    <Link href="/dashboard">
                      <Button>Ver dashboard</Button>
                    </Link>
                    <Link href="/action-plan">
                      <Button className="bg-blue/20">Abrir plan</Button>
                    </Link>
                    <Button className="border-white/10 bg-white/8" onClick={() => startNewConversation()}>
                      Sacar otro plan
                    </Button>
                  </div>
                  <Textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    placeholder="Pregunta por tus resultados, fortalezas, alternativas o por qué salió cierta carrera."
                    disabled={sendMutation.isPending}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        void handleConversationSubmit();
                      }
                    }}
                  />
                  <Button onClick={() => void handleConversationSubmit()} disabled={!activeSessionId || !draft.trim() || sendMutation.isPending}>
                    <Send className="mr-2 h-4 w-4" />
                    {sendMutation.isPending ? "Enviando..." : "Enviar pregunta"}
                  </Button>
                </>
              )}
            </div>
          </div>
        </Card>

        <aside className="space-y-4">
          <Card className="p-5">
            <div className="mb-2 text-sm text-muted">Estado del analisis</div>
            <div className="text-2xl font-semibold">
              {interviewCompleted ? "Resultado disponible" : interviewStarted ? "Entrevista en curso" : "Sin iniciar"}
            </div>
            <div className="mt-2 text-sm text-muted">
              {interviewCompleted
                ? "Ya puedes revisar recomendaciones, contrastar explicaciones y pedir un nuevo plan."
                : "La conversación sigue el área mejor puntuada y evita insistir en intereses bajos."}
            </div>
          </Card>

          <Card className="p-5">
                  <div className="mb-3 text-sm text-muted">Conversaciones</div>
            <div className="space-y-2">
              {sessionsQuery.data?.map((session) => (
                <button
                  key={session.id}
                  onClick={() => setActiveSessionId(session.id)}
                  className={`w-full rounded-xl border px-3 py-3 text-left text-sm transition ${
                    session.id === activeSessionId
                      ? "border-cyan-400/20 bg-cyan-400/10 text-cyan-100"
                      : "border-white/6 bg-white/5 text-muted hover:border-white/10 hover:text-text"
                  }`}
                >
                  {session.title}
                </button>
              )) ?? <div className="text-sm text-muted">Sin conversaciones activas.</div>}
            </div>
          </Card>

          <Card className="p-5">
            <div className="mb-3 text-sm text-muted">Resumen actual</div>
            {latestRecommendation ? (
              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-xs uppercase text-muted">Top 1 actual</div>
                  <div className="mt-1 text-lg font-medium">
                    {latestRecommendation.recommendations[0]?.program_slug.replaceAll("-", " ") ?? "Sin dato"}
                  </div>
                </div>
                <div>
                  Puntaje de compatibilidad:{" "}
                  <span className="font-medium text-cyan-200">{latestRecommendation.compatibility_score}</span>
                </div>
                <div>
                  Confianza: <span className="capitalize text-cyan-200">{latestRecommendation.confidence_level}</span>
                </div>
                {currentPlan && <div className="text-muted">Plan activo: {currentPlan.title}</div>}
              </div>
            ) : (
              <div className="text-sm text-muted">
                El panel se actualizará cuando completes el nuevo análisis conversacional.
              </div>
            )}
          </Card>
        </aside>
      </div>
    </AppShell>
  );
}
