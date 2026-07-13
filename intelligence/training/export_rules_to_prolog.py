from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules" / "rules.yaml"
OUTPUT_PATH = ROOT / "prolog" / "generated_rules.pl"


def normalize_slug(value: str) -> str:
    return value.replace("-", "_")


def main() -> None:
    payload = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))
    lines = ["% Reglas exportadas desde YAML"]
    for rule in payload["rules"]:
        if rule.get("abstention"):
            continue
        for action in rule.get("actions", []):
            if action["type"] != "increase_program_score":
                continue
            conditions = []
            for condition in rule["conditions"].get("all", []):
                feature = condition["feature"]
                if feature.startswith("interest_"):
                    conditions.append(f"interes(Estudiante, {normalize_slug(feature.removeprefix('interest_'))})")
                else:
                    conditions.append(f"habilidad(Estudiante, {normalize_slug(feature)})")
            body = ", ".join(conditions) if conditions else "true"
            lines.append(f"recomendar(Estudiante, {normalize_slug(action['target'])}) :- {body}.")
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Exportado {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
