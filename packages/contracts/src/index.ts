export type Profile = {
  preferred_name: string | null;
  grade_level: string | null;
  country: string | null;
  city: string | null;
  goal: string | null;
  known_areas: string[];
  onboarding_completed: boolean;
  privacy_policy_accepted: boolean;
  assessment_consent: boolean;
  guardian_consent_required: boolean;
  guardian_consent_granted: boolean;
};

export type Program = {
  slug: string;
  name: string;
  short_description: string;
  academic_area_slug: string;
  metadata_json: Record<string, unknown>;
  source_name: string;
  source_url: string | null;
  verified_at: string | null;
};

export type AssessmentAttempt = {
  id: string;
  version: string;
  status: string;
  progress: number;
  estimated_minutes_remaining: number;
  answers: Record<string, unknown>;
};

export type Recommendation = {
  id: string;
  program_slug: string;
  rank: number;
  compatibility_score: number;
  confidence_level: string;
  triggered_rules: Array<Record<string, unknown>>;
  supporting_factors: string[];
  development_factors: string[];
  knowledge_graph_paths: Array<Record<string, unknown>>;
};

export type RecommendationRun = {
  id: string;
  compatibility_score: number;
  confidence_level: string;
  score_components: Record<string, unknown>;
  structured_explanation: Record<string, unknown>;
  model_version: string;
  explanation_version: string;
  recommendations: Recommendation[];
};
