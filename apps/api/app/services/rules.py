from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, model_validator

RULES_PATH = Path(__file__).resolve().parents[4] / "intelligence" / "rules" / "rules.yaml"


class RuleCondition(BaseModel):
    feature: str
    operator: str
    value: Any


class RuleAction(BaseModel):
    type: str
    target: str
    weight: float


class RuleExplanation(BaseModel):
    title: str
    template: str


class RuleDefinition(BaseModel):
    id: str
    version: int
    enabled: bool
    priority: int = 100
    conditions: dict[str, Any]
    actions: list[RuleAction]
    explanation: RuleExplanation
    abstention: bool = False

    @model_validator(mode="after")
    def validate_conditions(self) -> RuleDefinition:
        keys = set(self.conditions.keys())
        if not keys.intersection({"all", "any", "not"}):
            raise ValueError("Las condiciones deben incluir all, any o not")
        return self


def load_rules() -> list[RuleDefinition]:
    raw = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))
    return [RuleDefinition.model_validate(item) for item in raw["rules"]]


def evaluate_condition(condition: RuleCondition, features: dict[str, Any]) -> bool:
    value = features.get(condition.feature)
    if condition.operator == "gte":
        return float(value or 0) >= float(condition.value)
    if condition.operator == "lte":
        return float(value or 0) <= float(condition.value)
    if condition.operator == "eq":
        return bool(value == condition.value)
    if condition.operator == "contains":
        return bool(condition.value in (value or []))
    return False


def rule_matches(rule: RuleDefinition, features: dict[str, Any]) -> bool:
    def parse(entries: list[dict[str, Any]]) -> list[bool]:
        return [evaluate_condition(RuleCondition.model_validate(entry), features) for entry in entries]

    if "all" in rule.conditions and not all(parse(rule.conditions["all"])):
        return False
    if "any" in rule.conditions and not any(parse(rule.conditions["any"])):
        return False
    if "not" in rule.conditions and any(parse(rule.conditions["not"])):
        return False
    return True


def score_rules(features: dict[str, Any]) -> tuple[dict[str, float], list[dict[str, Any]], list[str]]:
    scores: dict[str, float] = {}
    triggered: list[dict[str, Any]] = []
    abstentions: list[str] = []
    for rule in sorted(load_rules(), key=lambda item: item.priority):
        if not rule.enabled or not rule_matches(rule, features):
            continue
        if rule.abstention:
            abstentions.append(rule.id)
        for action in rule.actions:
            if action.type == "increase_program_score":
                scores[action.target] = scores.get(action.target, 0.0) + action.weight
        triggered.append(
            {
                "rule_id": rule.id,
                "title": rule.explanation.title,
                "explanation": rule.explanation.template,
                "actions": [action.model_dump() for action in rule.actions],
            }
        )
    return scores, triggered, abstentions
