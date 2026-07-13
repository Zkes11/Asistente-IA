import type { AssessmentAttempt, Program, Profile, RecommendationRun } from "@orientaia/contracts";

export type { AssessmentAttempt, Program, Profile, RecommendationRun };

export type AssessmentSchema = {
  slug: string;
  title: string;
  description: string;
  version: string;
  sections: Array<{
    key: string;
    title: string;
    description: string;
    questions: Array<{
      key: string;
      prompt: string;
      help_text: string | null;
      question_type: string;
      required: boolean;
      config: { min?: number; max?: number; step?: number };
      options: Array<{ label: string; value: string }>;
    }>;
  }>;
};

export type ActionPlan = {
  id: string;
  title: string;
  summary: string;
  created_at: string;
  steps: Array<{
    id: string;
    title: string;
    description: string;
    priority: string;
    status: string;
    progress: number;
    notes: string | null;
  }>;
};

export type ChatSession = { id: string; title: string; external_llm_enabled: boolean };
export type ChatMessage = {
  id: string;
  role: string;
  content: string;
  citations: Array<{ label: string; target: string }>;
};

export type InterviewTurn = {
  messages: string[];
  feature_key: string | null;
  should_finalize: boolean;
  rationale: string | null;
  answer_updates: Record<string, number>;
  merged_answers: Record<string, number>;
};
