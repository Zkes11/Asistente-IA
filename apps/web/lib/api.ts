import type {
  ActionPlan,
  AssessmentAttempt,
  AssessmentSchema,
  ChatMessage,
  ChatSession,
  InterviewTurn,
  Program,
  Profile,
  RecommendationRun,
} from "@/lib/types";

function buildApiCandidates() {
  const explicitUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  const candidates = new Set<string>();

  if (explicitUrl) {
    candidates.add(explicitUrl.replace(/\/$/, ""));
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    candidates.add(`${protocol}//${hostname}:8002/api/v1`);
    candidates.add(`${protocol}//${hostname}:8000/api/v1`);
    candidates.add(`${protocol}//${hostname}:8003/api/v1`);
  }

  candidates.add("http://127.0.0.1:8002/api/v1");
  candidates.add("http://localhost:8002/api/v1");
  candidates.add("http://127.0.0.1:8000/api/v1");
  candidates.add("http://localhost:8000/api/v1");

  return Array.from(candidates);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...(init?.headers ?? {}),
  };
  const candidates = buildApiCandidates();
  let lastNetworkError: Error | null = null;

  for (const apiUrl of candidates) {
    try {
      const response = await fetch(`${apiUrl}${path}`, {
        ...init,
        headers,
        credentials: "omit",
        cache: "no-store",
      });

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({ detail: "Error inesperado" }))) as {
          detail?: string;
        };
        throw new Error(payload.detail ?? "Error inesperado");
      }

      return (await response.json()) as T;
    } catch (error) {
      if (error instanceof TypeError) {
        lastNetworkError = error;
        continue;
      }
      throw error;
    }
  }

  throw new Error(
    `No fue posible conectar con la API local. Verifica que el backend esté activo en alguno de estos endpoints: ${candidates.join(", ")}.`,
    { cause: lastNetworkError ?? undefined },
  );
}

export const api = {
  register: (body: unknown) => request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: unknown) => request("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request("/auth/me"),
  getProfile: (): Promise<Profile> => request("/profile"),
  updateProfile: (body: unknown): Promise<Profile> =>
    request("/profile", { method: "PATCH", body: JSON.stringify(body) }),
  currentAssessment: (): Promise<AssessmentSchema> => request("/assessments/current"),
  createAttempt: (): Promise<AssessmentAttempt> =>
    request("/assessments/attempts", { method: "POST", body: JSON.stringify({}) }),
  getAttempt: (id: string): Promise<AssessmentAttempt> => request(`/assessments/attempts/${id}`),
  patchAttempt: (id: string, answers: Record<string, unknown>) =>
    request<AssessmentAttempt>(`/assessments/attempts/${id}/answers`, {
      method: "PATCH",
      body: JSON.stringify({ answers }),
    }),
  completeAttempt: (id: string) => request(`/assessments/attempts/${id}/complete`, { method: "POST" }),
  generateRecommendations: (): Promise<RecommendationRun> => request("/recommendations/generate", { method: "POST" }),
  listRecommendations: (): Promise<RecommendationRun[]> => request("/recommendations"),
  listPrograms: (): Promise<Program[]> => request("/programs"),
  comparePrograms: (slugs: string[]) =>
    request<Program[]>("/programs/compare", { method: "POST", body: JSON.stringify({ slugs }) }),
  favoriteProgram: (slug: string) => request(`/programs/${slug}/favorite`, { method: "POST" }),
  listActionPlans: (): Promise<ActionPlan[]> => request("/action-plans"),
  currentActionPlan: (): Promise<ActionPlan | null> => request("/action-plans/current"),
  getActionPlan: (planId: string): Promise<ActionPlan> => request(`/action-plans/${planId}`),
  createActionPlan: (recommendationRunId?: string, chatSessionId?: string) =>
    request<ActionPlan>("/action-plans", {
      method: "POST",
      body: JSON.stringify({
        recommendation_run_id: recommendationRunId ?? null,
        chat_session_id: chatSessionId ?? null,
      }),
    }),
  updateActionPlanStep: (planId: string, stepId: string, body: unknown) =>
    request(`/action-plans/${planId}/steps/${stepId}`, { method: "PATCH", body: JSON.stringify(body) }),
  createChatSession: (title: string) =>
    request<ChatSession>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ title, external_llm_enabled: false }),
    }),
  listChatSessions: (): Promise<ChatSession[]> => request("/chat/sessions"),
  deleteChatSession: (sessionId: string) => request(`/chat/sessions/${sessionId}`, { method: "DELETE" }),
  listMessages: (sessionId: string): Promise<ChatMessage[]> => request(`/chat/sessions/${sessionId}/messages`),
  generateInterviewTurn: (
    sessionId: string,
    body: {
      answers: Record<string, number | string>;
      max_follow_up_questions?: number;
      mode?: "start" | "advance";
      evaluated_feature_key?: string | null;
      evaluated_feature_score?: number | null;
    },
  ) =>
    request<InterviewTurn>(`/chat/sessions/${sessionId}/interview-turn`, { method: "POST", body: JSON.stringify(body) }),
  appendChatMessage: (sessionId: string, body: { role: "assistant" | "user"; content: string }) =>
    request<ChatMessage>(`/chat/sessions/${sessionId}/messages/raw`, { method: "POST", body: JSON.stringify(body) }),
  sendMessage: (sessionId: string, content: string) =>
    request<ChatMessage>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
};
