from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np

OUTPUT_PATH = Path(__file__).resolve().parent / "synthetic_vocational_dataset.csv"
SEED = 42
ROWS_PER_AREA = 160

FEATURES = [
    "interest_technology",
    "interest_social",
    "interest_design",
    "interest_health",
    "interest_business",
    "interest_data",
    "creativity",
    "logical_reasoning",
    "communication",
    "empathy",
    "leadership",
    "numerical_skill",
    "visual_thinking",
    "organization",
    "practical_learning",
    "theoretical_learning",
    "teamwork_preference",
    "autonomy_preference",
]

AREA_PROFILES: dict[str, dict[str, object]] = {
    "ingenieria-de-sistemas": {
        "features": {
            "interest_technology": 5,
            "interest_data": 4,
            "logical_reasoning": 5,
            "numerical_skill": 4,
            "organization": 3,
            "practical_learning": 4,
            "theoretical_learning": 3,
            "autonomy_preference": 4,
            "communication": 2,
            "empathy": 2,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "ingenieria-de-software": {
        "features": {
            "interest_technology": 5,
            "interest_data": 4,
            "logical_reasoning": 5,
            "numerical_skill": 4,
            "organization": 4,
            "practical_learning": 4,
            "theoretical_learning": 4,
            "autonomy_preference": 5,
            "communication": 2,
            "empathy": 2,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "ciencia-de-datos": {
        "features": {
            "interest_data": 5,
            "interest_technology": 4,
            "logical_reasoning": 4,
            "numerical_skill": 5,
            "organization": 4,
            "theoretical_learning": 4,
            "practical_learning": 3,
            "autonomy_preference": 4,
            "communication": 2,
        },
        "work_environment": ["oficina", "laboratorio"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "ciberseguridad": {
        "features": {
            "interest_technology": 5,
            "interest_data": 4,
            "logical_reasoning": 5,
            "organization": 4,
            "autonomy_preference": 4,
            "theoretical_learning": 4,
            "practical_learning": 3,
            "communication": 2,
            "empathy": 1,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "psicologia": {
        "features": {
            "interest_social": 5,
            "interest_health": 3,
            "communication": 4,
            "empathy": 5,
            "theoretical_learning": 4,
            "practical_learning": 3,
            "teamwork_preference": 4,
            "autonomy_preference": 2,
        },
        "work_environment": ["mixto", "campo"],
        "preferred_modality": ["presencial", "mixta"],
    },
    "trabajo-social": {
        "features": {
            "interest_social": 5,
            "communication": 4,
            "empathy": 5,
            "practical_learning": 4,
            "teamwork_preference": 5,
            "autonomy_preference": 2,
            "organization": 3,
        },
        "work_environment": ["campo", "mixto"],
        "preferred_modality": ["presencial", "mixta"],
    },
    "diseno-ux-ui": {
        "features": {
            "interest_design": 5,
            "interest_technology": 4,
            "creativity": 5,
            "visual_thinking": 5,
            "communication": 3,
            "practical_learning": 4,
            "theoretical_learning": 3,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "administracion-de-empresas": {
        "features": {
            "interest_business": 5,
            "organization": 5,
            "leadership": 4,
            "communication": 4,
            "autonomy_preference": 4,
            "teamwork_preference": 3,
            "numerical_skill": 3,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["presencial", "mixta"],
    },
    "marketing-digital": {
        "features": {
            "interest_business": 4,
            "interest_design": 3,
            "communication": 5,
            "creativity": 4,
            "interest_data": 3,
            "organization": 3,
            "leadership": 3,
        },
        "work_environment": ["oficina", "mixto"],
        "preferred_modality": ["virtual", "mixta"],
    },
    "enfermeria": {
        "features": {
            "interest_health": 5,
            "interest_social": 4,
            "empathy": 5,
            "practical_learning": 5,
            "teamwork_preference": 4,
            "communication": 4,
            "autonomy_preference": 2,
            "theoretical_learning": 3,
        },
        "work_environment": ["campo", "mixto"],
        "preferred_modality": ["presencial", "mixta"],
    },
    "biologia": {
        "features": {
            "interest_health": 5,
            "interest_data": 3,
            "theoretical_learning": 5,
            "practical_learning": 4,
            "numerical_skill": 3,
            "logical_reasoning": 3,
            "autonomy_preference": 4,
            "communication": 2,
            "empathy": 2,
        },
        "work_environment": ["laboratorio", "campo"],
        "preferred_modality": ["presencial", "mixta"],
    },
    "educacion": {
        "features": {
            "interest_social": 4,
            "communication": 5,
            "empathy": 4,
            "theoretical_learning": 4,
            "teamwork_preference": 4,
            "organization": 3,
            "autonomy_preference": 2,
        },
        "work_environment": ["campo", "mixto"],
        "preferred_modality": ["presencial", "mixta"],
    },
}


def sample_feature_value(rng: np.random.Generator, center: float) -> int:
    sampled = float(rng.normal(loc=center, scale=0.65))
    return int(np.clip(round(sampled), 1, 5))


def synthesize_row(rng: np.random.Generator, area: str) -> dict[str, int | str]:
    profile = AREA_PROFILES[area]
    base = {feature: sample_feature_value(rng, 2.2) for feature in FEATURES}

    for feature, center in profile["features"].items():
        base[feature] = sample_feature_value(rng, float(center))

    base["work_environment"] = str(rng.choice(profile["work_environment"]))
    base["preferred_modality"] = str(rng.choice(profile["preferred_modality"]))
    base["academic_area_label"] = area
    return base


def dataset_hash(csv_text: str) -> str:
    return hashlib.sha256(csv_text.encode("utf-8")).hexdigest()


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows: list[dict[str, int | str]] = []
    for area in AREA_PROFILES:
        rows.extend(synthesize_row(rng, area) for _ in range(ROWS_PER_AREA))

    headers = list(rows[0].keys())
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    csv_text = OUTPUT_PATH.read_text(encoding="utf-8")
    print(f"Dataset sintetico generado en {OUTPUT_PATH}")
    print(f"Filas: {len(rows)}")
    print(f"Hash: {dataset_hash(csv_text)}")


if __name__ == "__main__":
    main()
