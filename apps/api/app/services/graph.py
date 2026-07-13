from __future__ import annotations

from typing import Any

GRAPH_MAPPINGS: dict[str, dict[str, list[str]]] = {
    "ingenieria-de-sistemas": {
        "interests": ["Tecnologia", "Datos"],
        "skills": ["Pensamiento logico", "Resolucion de problemas"],
    },
    "ciencia-de-datos": {
        "interests": ["Datos", "Tecnologia"],
        "skills": ["Analisis numerico", "Pensamiento logico"],
    },
    "psicologia": {
        "interests": ["Social", "Salud"],
        "skills": ["Empatia", "Comunicacion"],
    },
    "diseno-ux-ui": {
        "interests": ["Diseno", "Tecnologia"],
        "skills": ["Pensamiento visual", "Creatividad"],
    },
    "biologia": {
        "interests": ["Salud", "Datos"],
        "skills": ["Aprendizaje teorico", "Aprendizaje practico"],
    },
    "quimica-aplicada": {
        "interests": ["Salud", "Datos"],
        "skills": ["Analisis numerico", "Aprendizaje practico"],
    },
    "enfermeria": {
        "interests": ["Salud", "Social"],
        "skills": ["Empatia", "Aprendizaje practico"],
    },
    "fisioterapia": {
        "interests": ["Salud", "Social"],
        "skills": ["Aprendizaje practico", "Empatia", "Trabajo en equipo"],
    },
    "educacion": {
        "interests": ["Social", "Salud"],
        "skills": ["Comunicacion", "Aprendizaje practico"],
    },
    "trabajo-social": {
        "interests": ["Social"],
        "skills": ["Empatia", "Comunicacion"],
    },
}


def score_graph(features: dict[str, Any]) -> tuple[dict[str, float], dict[str, list[dict[str, Any]]]]:
    interest_lookup = {
        "interest_technology": "Tecnologia",
        "interest_data": "Datos",
        "interest_social": "Social",
        "interest_health": "Salud",
        "interest_design": "Diseno",
        "interest_business": "Negocios",
    }
    skill_lookup = {
        "logical_reasoning": "Pensamiento logico",
        "numerical_skill": "Analisis numerico",
        "communication": "Comunicacion",
        "empathy": "Empatia",
        "visual_thinking": "Pensamiento visual",
        "creativity": "Creatividad",
        "theoretical_learning": "Aprendizaje teorico",
        "practical_learning": "Aprendizaje practico",
        "teamwork_preference": "Trabajo en equipo",
    }
    active_interests = {label for key, label in interest_lookup.items() if float(features.get(key, 0)) >= 4}
    active_skills = {label for key, label in skill_lookup.items() if float(features.get(key, 0)) >= 4}
    scores: dict[str, float] = {}
    paths: dict[str, list[dict[str, Any]]] = {}
    for program, mapping in GRAPH_MAPPINGS.items():
        overlap = len(active_interests.intersection(mapping["interests"])) + len(
            active_skills.intersection(mapping["skills"])
        )
        if overlap:
            scores[program] = min(overlap / 4, 1.0)
            paths[program] = [
                {"from": "Estudiante", "relation": "HAS_INTEREST", "to": label}
                for label in sorted(active_interests.intersection(mapping["interests"]))
            ] + [
                {"from": label, "relation": "RELATES_TO", "to": program}
                for label in sorted(active_interests.intersection(mapping["interests"]))
            ] + [
                {"from": "Estudiante", "relation": "HAS_SKILL", "to": label}
                for label in sorted(active_skills.intersection(mapping["skills"]))
            ]
    return scores, paths
