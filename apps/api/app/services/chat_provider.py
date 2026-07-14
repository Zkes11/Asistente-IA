from __future__ import annotations

import re
from typing import Any

AREA_INFO = {
    "interest_technology": {
        "label": "tecnologia y construccion digital",
        "follow_ups": ["logical_reasoning", "interest_data", "practical_learning", "autonomy_preference"],
        "keywords": ["tecnologia", "software", "programar", "codigo", "apps", "sistemas", "digital", "computador"],
    },
    "interest_social": {
        "label": "acompanamiento a personas",
        "follow_ups": ["empathy", "communication", "teamwork_preference"],
        "keywords": ["ayudar", "acompanar", "personas", "social", "comunidad", "servicio", "escuchar", "orientar"],
    },
    "interest_design": {
        "label": "diseno y creatividad visual",
        "follow_ups": ["visual_thinking", "creativity", "communication"],
        "keywords": ["diseno", "visual", "creativo", "interfaces", "dibujar", "colores", "marca", "ux", "grafico"],
    },
    "interest_health": {
        "label": "ciencias naturales y salud",
        "follow_ups": ["theoretical_learning", "practical_learning", "numerical_skill", "autonomy_preference", "empathy"],
        "keywords": [
            "salud",
            "cuidado",
            "bienestar",
            "pacientes",
            "clinico",
            "medico",
            "biologia",
            "quimica",
            "laboratorio",
            "cuerpo",
            "ciencia",
        ],
    },
    "interest_business": {
        "label": "negocios, gestion y liderazgo",
        "follow_ups": ["organization", "autonomy_preference", "communication"],
        "keywords": ["negocio", "empresa", "liderar", "ventas", "emprender", "estrategia", "administracion", "gestion"],
    },
    "interest_data": {
        "label": "datos y analitica",
        "follow_ups": ["numerical_skill", "logical_reasoning", "theoretical_learning"],
        "keywords": ["datos", "analisis", "metricas", "estadistica", "patrones", "tablas", "matematicas", "numeros", "calculo", "fisica"],
    },
}

FEATURE_INFO: dict[str, dict[str, Any]] = {
    "interest_technology": {
        "label": "afinidad con tecnologia",
        "hint": "herramientas digitales, software, automatizacion o construir soluciones",
        "question_seed": "Cuando te imaginas estudiando o trabajando, que parte de la tecnologia te atrae de verdad",
        "keywords": AREA_INFO["interest_technology"]["keywords"],
        "positive_patterns": [r"\bme gusta(?: mucho)? la tecnologia\b", r"\bprogram", r"\bsoftware\b"],
        "negative_patterns": [r"\bno me gusta(?: mucho)? la tecnologia\b", r"\bcasi no me interesa la tecnologia\b", r"\bcasi no me gusta la tecnlogia\b", r"\bcasi no me gusta la tecnologia\b"],
    },
    "interest_social": {
        "label": "interes social",
        "hint": "acompanar personas, orientar, escuchar o aportar a una comunidad",
        "question_seed": "Cuando ayudas a otras personas, que tipo de situaciones te energizan mas",
        "keywords": AREA_INFO["interest_social"]["keywords"],
        "positive_patterns": [r"\bme gusta ayudar\b", r"\bapoyar a la gente\b", r"\bacompanar\b"],
        "negative_patterns": [r"\bno me gusta tratar con gente\b", r"\bno quiero trabajar con gente todos los dias\b"],
    },
    "interest_design": {
        "label": "interes por diseno",
        "hint": "interfaces, imagen, piezas visuales, narrativa visual o experiencia",
        "question_seed": "Si tuvieras que crear algo visual, que te gustaria diseñar y por que",
        "keywords": AREA_INFO["interest_design"]["keywords"],
        "positive_patterns": [r"\bdiseno\b", r"\bvisual\b", r"\bdibujar\b", r"\bux\b"],
        "negative_patterns": [r"\bno me gusta diseñar\b", r"\bcasi no soy visual\b", r"\bno, no me gustaria\b", r"\bno me gustaria\b"],
    },
    "interest_health": {
        "label": "interes por salud y ciencias naturales",
        "hint": "laboratorio, bienestar, cuidado, ciencia aplicada o procesos biologicos",
        "question_seed": "Cuando piensas en biologia, quimica o salud, que es lo que mas te atrae de ese mundo",
        "keywords": AREA_INFO["interest_health"]["keywords"],
        "positive_patterns": [r"\bme gusta la quimica\b", r"\bme gusta la biologia\b", r"\blaboratorio\b", r"\bme interesa la salud\b"],
        "negative_patterns": [
            r"\bno me interesa la salud\b",
            r"\bno me gusta la biologia\b",
            r"\bno me gusta la quimica\b",
            r"\bno me gustan? las ciencias naturales\b",
            r"\bno me gusta(?:n)? el deporte\b",
            r"\bno me gusta(?:n)? los deportes\b",
            r"\bcasi no me gusta(?:n)? los deportes\b",
        ],
    },
    "interest_business": {
        "label": "interes por negocios",
        "hint": "estrategia, gestion, liderazgo, ventas o emprendimiento",
        "question_seed": "Que disfrutas mas cuando piensas en liderar, organizar o mover un proyecto",
        "keywords": AREA_INFO["interest_business"]["keywords"],
        "positive_patterns": [r"\bnegocio", r"\bempresa", r"\bemprend"],
        "negative_patterns": [r"\bno me gustan las ventas\b", r"\bno me interesa administrar\b"],
    },
    "interest_data": {
        "label": "interes por datos",
        "hint": "patrones, metricas, tablas, estadistica o decisiones con evidencia",
        "question_seed": "Que tanto disfrutas encontrar patrones y explicar decisiones con datos",
        "keywords": AREA_INFO["interest_data"]["keywords"],
        "positive_patterns": [r"\bmatematic", r"\bestadistic", r"\bdatos\b", r"\bnumer"],
        "negative_patterns": [r"\bno me gustan los numeros\b", r"\bme cuestan las matematicas\b"],
    },
    "logical_reasoning": {
        "label": "razonamiento logico",
        "hint": "desarmar problemas, pensar paso a paso o encontrar estructura",
        "question_seed": "Cuando aparece un problema dificil, como lo ordenas para resolverlo",
        "keywords": ["logica", "resolver", "problemas", "analizar", "estructurar", "fases", "pasos"],
        "positive_patterns": [r"\bpaso a paso\b", r"\bestructur", r"\bpor fases\b", r"\banaliz"],
        "negative_patterns": [r"\bme pierdo con problemas\b", r"\bno soy tan logico\b"],
    },
    "communication": {
        "label": "comunicacion",
        "hint": "explicar ideas, escribir, presentar o persuadir",
        "question_seed": "En que situaciones sientes que comunicar ideas te sale natural",
        "keywords": ["explicar", "presentar", "escribir", "comunicar", "hablar", "argumentar", "ideas"],
        "positive_patterns": [r"\bme sale natural\b", r"\bexplicar ideas\b", r"\bme gusta escribir\b", r"\bbuen lider\b", r"\blider\b"],
        "negative_patterns": [r"\bcasi no me gusta compartir mis ideas\b", r"\bno me gusta hablar\b", r"\bno tanto\b"],
    },
    "empathy": {
        "label": "empatia",
        "hint": "escuchar, comprender a otros, orientar o contener",
        "question_seed": "Cuando alguien necesita apoyo, como sueles responder tu",
        "keywords": ["escuchar", "comprender", "empatia", "acompanar", "apoyar", "orientar", "ayudar"],
        "positive_patterns": [r"\bsuelo apoyar\b", r"\bme gusta ayudar\b", r"\bescucho mucho\b"],
        "negative_patterns": [r"\bme cuesta escuchar\b", r"\bno me gusta lidiar con personas\b"],
    },
    "creativity": {
        "label": "creatividad",
        "hint": "imaginar soluciones, proponer ideas o experimentar con enfoques nuevos",
        "question_seed": "Cuentame un ejemplo reciente donde hayas creado una idea propia",
        "keywords": ["crear", "imaginar", "ideas", "original", "innovar", "inventar"],
        "positive_patterns": [r"\bcrear\b", r"\bidea propia\b", r"\binnov"],
        "negative_patterns": [r"\bno soy creativo\b", r"\bme cuesta inventar\b"],
    },
    "numerical_skill": {
        "label": "habilidad numerica",
        "hint": "calculos, relaciones cuantitativas, estadistica o lectura de datos",
        "question_seed": "Que tan natural te resulta trabajar con numeros, calculos o relaciones cuantitativas",
        "keywords": ["numeros", "matematicas", "calculos", "estadistica", "finanzas", "cuentas", "calculo", "algebra", "fisica"],
        "positive_patterns": [r"\bme gustan las matematicas\b", r"\bsoy bueno en matematicas\b", r"\bcalculos\b"],
        "negative_patterns": [
            r"\bno me gustan los numeros\b",
            r"\bme cuestan las matematicas\b",
            r"\bno .*numer",
            r"\bno .*matematic",
            r"\bno .*calculo",
            r"\bno soy .*bueno .*numer",
            r"\bno soy .*buena .*numer",
        ],
    },
    "visual_thinking": {
        "label": "pensamiento visual",
        "hint": "organizar ideas con imagenes, diagramas, espacios o interfaces",
        "question_seed": "Cuando entiendes algo complejo, te sirve verlo en esquemas, pantallas o diagramas",
        "keywords": ["visual", "diagramas", "dibujos", "espacios", "interfaces", "mapas"],
        "positive_patterns": [r"\bdiagramas\b", r"\bvisual\b", r"\besquemas\b"],
        "negative_patterns": [r"\bno soy visual\b"],
    },
    "organization": {
        "label": "organizacion",
        "hint": "planificar, priorizar o estructurar tareas",
        "question_seed": "Cuando tienes varias tareas, como decides por donde empezar",
        "keywords": ["organizar", "planear", "orden", "priorizar", "estructura", "agenda"],
        "positive_patterns": [r"\bplan", r"\bprioriz", r"\borden"],
        "negative_patterns": [r"\bme cuesta organizarme\b"],
    },
    "teamwork_preference": {
        "label": "preferencia por trabajo colaborativo",
        "hint": "coordinar, construir en grupo o tomar decisiones con otras personas",
        "question_seed": "En un proyecto, prefieres construir en grupo o avanzar por tu cuenta y luego mostrar resultados",
        "keywords": ["equipo", "grupo", "colaborar", "companeros", "coordinar", "juntos"],
        "positive_patterns": [r"\ben grupo\b", r"\bcon el equipo\b", r"\bjuntos\b"],
        "negative_patterns": [r"\bpor mi cuenta\b", r"\bsolo\b", r"\bpor mi lado\b"],
    },
    "autonomy_preference": {
        "label": "preferencia por autonomia",
        "hint": "trabajar con independencia, decidir tu ritmo o moverte con libertad",
        "question_seed": "Cuanto valoras tener autonomia frente a instrucciones muy marcadas",
        "keywords": ["autonomia", "independiente", "solo", "mi cuenta", "libertad", "autonomo"],
        "positive_patterns": [r"\bpor mi cuenta\b", r"\bindependiente\b", r"\bsolo\b", r"\bautonomia\b"],
        "negative_patterns": [r"\bnecesito mucha guia\b", r"\bprefiero instrucciones claras\b"],
    },
    "practical_learning": {
        "label": "aprendizaje practico",
        "hint": "aprender haciendo, probar, experimentar o construir",
        "question_seed": "Aprendes mejor cuando te explican primero o cuando te dejan probar y construir algo",
        "keywords": ["practico", "haciendo", "taller", "experiencia", "proyecto", "laboratorio", "probar", "ponerlo en practica", "experimentar"],
        "positive_patterns": [r"\bcuando lo hago yo\b", r"\bponerlo en practica\b", r"\bprobar\b", r"\bexperiment"],
        "negative_patterns": [r"\bprefiero solo teoria\b"],
    },
    "theoretical_learning": {
        "label": "aprendizaje teorico",
        "hint": "leer, investigar, profundizar conceptos o entender fundamentos",
        "question_seed": "Disfrutas dedicar tiempo a entender la teoria antes de pasar a la practica",
        "keywords": ["teoria", "leer", "conceptos", "investigar", "profundizar", "fundamentos"],
        "positive_patterns": [r"\bme gusta investigar\b", r"\bme gusta leer\b", r"\bentender la teoria\b", r"\bfundamentos\b"],
        "negative_patterns": [r"\bno me gusta la teoria\b"],
    },
}

QUESTION_TEMPLATES = [
    "Quiero entender mejor {label}. {seed}? Si puedes, dame un ejemplo concreto.",
    "Me falta un poco de precision en {label}. {seed}? Responde como si me contaras una situacion real.",
    "Voy a profundizar un poco en {label}. {seed}? Cuentamelo con tus palabras.",
]
OPENING_PROMPT = (
    "Cuéntame con libertad qué temas te atraen, qué actividades disfrutas, en qué materias te va mejor y qué tipo de trabajo no te imaginas haciendo."
)
SHORT_POSITIVE_RESPONSES = {"si", "me sale natural", "si, me sale natural", "claro", "bastante", "mucho", "probar"}
SPORT_TOKENS = ["deporte", "deportes", "entrenamiento", "actividad fisica", "ejercicio"]
NATURAL_SCIENCE_TOKENS = ["ciencias naturales", "biologia", "quimica", "laboratorio", "salud"]


def _feature_contains_explicit_negative(feature_key: str, text: str) -> bool:
    feature = FEATURE_INFO.get(feature_key)
    if feature is None:
        return False
    return _matches_any(_normalize_text(text), list(feature.get("negative_patterns", [])))


def _feature_contains_explicit_positive(feature_key: str, text: str) -> bool:
    feature = FEATURE_INFO.get(feature_key)
    if feature is None:
        return False
    return _matches_any(_normalize_text(text), list(feature.get("positive_patterns", [])))


def _compact(value: str) -> str:
    return " ".join(value.split()).strip()


def _normalize_text(value: str) -> str:
    return _compact(value.lower())


def _excerpt(text: str, limit: int = 120) -> str:
    cleaned = _compact(text)
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3].rstrip()}..."


def _rank_interest_areas(answers: dict[str, Any]) -> list[tuple[str, float]]:
    areas = [(feature_key, float(answers.get(feature_key, 0) or 0)) for feature_key in AREA_INFO]
    return sorted(areas, key=lambda item: item[1], reverse=True)


def _describe_score(score: float) -> str:
    if score >= 4.5:
        return "muy alta"
    if score >= 4:
        return "alta"
    if score >= 3:
        return "intermedia"
    if score >= 2:
        return "baja"
    return "muy baja"


def _extract_explicit_score(text: str) -> float | None:
    match = re.search(r"\b([1-5])\b", text)
    if match:
        return float(match.group(1))
    return None


def _count_keywords(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _score_feature_from_text(feature_key: str, text: str, *, broad: bool) -> float | None:
    normalized = _normalize_text(text)
    if not normalized:
        return None

    explicit = _extract_explicit_score(normalized)
    feature = FEATURE_INFO.get(feature_key)
    if explicit is not None and not broad:
        return explicit
    if feature is None:
        return None

    positive_patterns = list(feature.get("positive_patterns", []))
    negative_patterns = list(feature.get("negative_patterns", []))
    keywords = list(feature.get("keywords", []))

    if _matches_any(normalized, negative_patterns):
        return 1.0 if broad else 2.0
    if _matches_any(normalized, positive_patterns):
        return 5.0

    positive_hits = _count_keywords(normalized, keywords)
    if positive_hits >= 2:
        return 5.0
    if positive_hits == 1:
        return 4.0

    if normalized in SHORT_POSITIVE_RESPONSES and not broad:
        return 4.0

    if broad:
        return None

    if feature_key == "teamwork_preference" and ("por mi cuenta" in normalized or "solo" in normalized):
        return 1.0
    if feature_key == "autonomy_preference" and ("por mi cuenta" in normalized or "solo" in normalized):
        return 5.0
    if feature_key == "numerical_skill" and (
        "no son tan bueno con los numeros" in normalized
        or "no soy tan bueno con los numeros" in normalized
        or "no soy tan buena con los numeros" in normalized
        or "no soy bueno con los numeros" in normalized
        or "no soy buena con los numeros" in normalized
    ):
        return 1.0
    if feature_key == "practical_learning" and (
        "cuando lo hago yo" in normalized or "ponerlo en practica" in normalized or "probar" in normalized
    ):
        return 5.0
    if feature_key == "communication" and ("casi no" in normalized or "no tanto" in normalized):
        return 2.0
    if feature_key == "numerical_skill" and ("soy muy malo" in normalized or "muy malo" in normalized or "muy mala" in normalized):
        return 1.0

    return 3.0


def _derive_cross_signal_updates(text: str) -> dict[str, float]:
    normalized = _normalize_text(text)
    updates: dict[str, float] = {}

    if any(token in normalized for token in ["quimica", "biologia", "laboratorio"]):
        updates["interest_health"] = max(updates.get("interest_health", 0.0), 5.0)

    if "matematic" in normalized or "fisica" in normalized or "calculo" in normalized:
        updates["interest_data"] = max(updates.get("interest_data", 0.0), 4.0)
        updates["numerical_skill"] = max(updates.get("numerical_skill", 0.0), 4.0)

    if "por mi cuenta" in normalized or "solo" in normalized or "independiente" in normalized:
        updates["autonomy_preference"] = max(updates.get("autonomy_preference", 0.0), 5.0)
        updates["teamwork_preference"] = 1.0

    if "no trataria con gente todos los dias" in normalized or "no quiero trabajar con gente todos los dias" in normalized:
        updates["interest_social"] = min(updates.get("interest_social", 3.0), 2.0)
        updates["teamwork_preference"] = min(updates.get("teamwork_preference", 3.0), 2.0)

    if "ayudar a la gente" in normalized or "suelo apoyar" in normalized or "me gusta ayudar" in normalized:
        updates["empathy"] = max(updates.get("empathy", 0.0), 4.0)

    if "casi no me gusta compartir mis ideas" in normalized or "no me gusta compartir mis ideas" in normalized:
        updates["communication"] = 1.0

    if "lider" in normalized or "liderazgo" in normalized:
        updates["communication"] = max(updates.get("communication", 0.0), 4.0)
        updates["teamwork_preference"] = max(updates.get("teamwork_preference", 0.0), 4.0)

    if "cuando lo hago yo" in normalized or "ponerlo en practica" in normalized or normalized == "probar":
        updates["practical_learning"] = max(updates.get("practical_learning", 0.0), 5.0)

    if "no me gustan las ciencias naturales" in normalized or "no me gusta las ciencias naturales" in normalized:
        updates["interest_health"] = 1.0

    if any(
        phrase in normalized
        for phrase in [
            "no me gusta el deporte",
            "no me gusta los deportes",
            "no me gustan los deportes",
            "ni el deporte",
            "ni los deportes",
            "casi no me gustan los deportes",
        ]
    ):
        updates["interest_health"] = min(updates.get("interest_health", 5.0), 1.0)
        updates["teamwork_preference"] = min(updates.get("teamwork_preference", 3.0), 3.0)

    return updates


def extract_answer_updates(
    answers: dict[str, Any],
    user_messages: list[str],
    evaluated_feature_key: str | None = None,
) -> dict[str, float]:
    if not user_messages:
        return {}

    latest_message = user_messages[-1]
    updates: dict[str, float] = {}

    if evaluated_feature_key:
        score = _score_feature_from_text(evaluated_feature_key, latest_message, broad=False)
        if score is not None:
            updates[evaluated_feature_key] = score
    else:
        for feature_key in AREA_INFO:
            score = _score_feature_from_text(feature_key, latest_message, broad=True)
            if score is not None:
                updates[feature_key] = score

    for feature_key, score in _derive_cross_signal_updates(latest_message).items():
        if feature_key not in updates:
            updates[feature_key] = score
            continue
        if feature_key == "teamwork_preference":
            updates[feature_key] = min(updates[feature_key], score)
        else:
            updates[feature_key] = max(updates[feature_key], score)

    latest_normalized = _normalize_text(latest_message)
    for feature_key, current_score in list(updates.items()):
        previous_score = float(answers.get(feature_key, 0) or 0)
        explicit_negative = _feature_contains_explicit_negative(feature_key, latest_normalized)
        explicit_positive = _feature_contains_explicit_positive(feature_key, latest_normalized)
        contradiction = (previous_score >= 4 and current_score <= 2) or (previous_score <= 2 and current_score >= 4)
        if explicit_negative or explicit_positive or contradiction:
            updates[feature_key] = round(current_score, 2)
        elif previous_score > 0:
            updates[feature_key] = round((previous_score * 0.35) + (current_score * 0.65), 2)
        else:
            updates[feature_key] = round(current_score, 2)

    return updates


def _area_signal_from_messages(user_messages: list[str]) -> list[tuple[str, int]]:
    joined_text = _normalize_text(" ".join(user_messages))
    if not joined_text:
        return []
    ranked_areas: list[tuple[str, int]] = []
    for area_key, config in AREA_INFO.items():
        score = _count_keywords(joined_text, config["keywords"])
        if area_key == "interest_social" and (
            "no trataria con gente todos los dias" in joined_text or "no quiero trabajar con gente todos los dias" in joined_text
        ):
            score -= 2
        if area_key == "interest_technology" and (
            "no me gusta la tecnologia" in joined_text or "casi no me interesa la tecnologia" in joined_text
        ):
            score -= 2
        if area_key == "interest_health" and (
            "no me gustan las ciencias naturales" in joined_text
            or "no me gusta las ciencias naturales" in joined_text
            or "no me gusta el deporte" in joined_text
            or "no me gustan los deportes" in joined_text
            or "ni el deporte" in joined_text
            or "ni los deportes" in joined_text
        ):
            score -= 3
        if score > 0:
            ranked_areas.append((area_key, score))
    ranked_areas.sort(key=lambda item: item[1], reverse=True)
    return ranked_areas


def _choose_seed_area(answers: dict[str, Any], user_messages: list[str]) -> str | None:
    ranked_message_areas = _area_signal_from_messages(user_messages)
    if ranked_message_areas:
        return ranked_message_areas[0][0]

    ranked_answer_areas = _rank_interest_areas(answers)
    for area_key, score in ranked_answer_areas:
        if score >= 3.5:
            return area_key
    return None


def _follow_ups_for_area(area_key: str, user_messages: list[str]) -> list[str]:
    if area_key != "interest_health":
        return list(AREA_INFO[area_key]["follow_ups"])

    joined = _normalize_text(" ".join(user_messages))
    sport_signal = any(token in joined for token in SPORT_TOKENS)
    people_care_signal = any(token in joined for token in ["pacientes", "cuidado", "ayudar", "acompanar", "personas"])
    if sport_signal:
        return ["practical_learning", "teamwork_preference", "autonomy_preference", "empathy"]
    if people_care_signal:
        return ["empathy", "practical_learning", "teamwork_preference", "theoretical_learning"]
    return ["theoretical_learning", "practical_learning", "autonomy_preference", "numerical_skill"]


def _theme_follow_ups(user_messages: list[str]) -> list[str]:
    joined = _normalize_text(" ".join(user_messages))
    if not joined:
        return []

    if any(token in joined for token in SPORT_TOKENS):
        return ["practical_learning", "teamwork_preference", "autonomy_preference", "communication", "empathy"]

    if any(token in joined for token in ["quimica", "biologia", "laboratorio"]):
        return ["theoretical_learning", "practical_learning", "numerical_skill", "autonomy_preference"]

    if any(token in joined for token in ["matematic", "fisica", "calculo", "datos", "estadistica"]):
        return ["logical_reasoning", "numerical_skill", "theoretical_learning", "practical_learning"]

    if any(token in joined for token in ["ayudar", "acompanar", "personas", "lider", "motivar"]):
        return ["empathy", "communication", "teamwork_preference", "autonomy_preference"]

    return []


def _pick_next_feature(answers: dict[str, Any], user_messages: list[str], max_follow_up_questions: int) -> str | None:
    answered_keys = set(answers.keys())
    follow_up_answer_count = sum(1 for feature_key in answered_keys if feature_key not in AREA_INFO)
    if follow_up_answer_count >= max_follow_up_questions:
        return None

    for feature_key in _theme_follow_ups(user_messages):
        if feature_key not in answered_keys:
            return feature_key

    seed_area = _choose_seed_area(answers, user_messages)
    ranked_areas = [seed_area] if seed_area else []
    ranked_areas.extend(
        area_key for area_key, score in _rank_interest_areas(answers) if score >= 3 and area_key not in ranked_areas
    )

    for area_key in ranked_areas:
        if not area_key:
            continue
        for feature_key in _follow_ups_for_area(area_key, user_messages):
            if feature_key not in answered_keys:
                return feature_key

    for feature_key in FEATURE_INFO:
        if feature_key not in answered_keys:
            return feature_key
    return None


def generate_interview_turn(
    answers: dict[str, Any], user_messages: list[str], max_follow_up_questions: int = 4
) -> dict[str, Any]:
    next_feature = _pick_next_feature(answers, user_messages, max_follow_up_questions)
    if not next_feature:
        return {
            "question": (
                "Ya tengo suficiente contexto para cerrar el analisis. Si quieres, procesa el perfil ahora y te devuelvo un plan por este chat."
            ),
            "feature_key": None,
            "should_finalize": True,
            "rationale": "Se alcanzo el maximo de profundizacion util.",
        }

    feature = FEATURE_INFO[next_feature]
    ranked_areas = _rank_interest_areas(answers)
    strongest_area_key = next((area_key for area_key, score in ranked_areas if score >= 3.5), None)
    if strongest_area_key is None:
        strongest_area_key = _choose_seed_area(answers, user_messages)
    strongest_area_label = AREA_INFO[strongest_area_key]["label"] if strongest_area_key else None
    latest_user_excerpt = _excerpt(user_messages[-1]) if user_messages else "lo que contaste hasta ahora"
    first_user_excerpt = _excerpt(user_messages[0]) if user_messages else "tu interes principal"
    template_index = len(user_messages) % len(QUESTION_TEMPLATES)
    prompt_core = QUESTION_TEMPLATES[template_index].format(label=feature["label"], seed=feature["question_seed"])

    question = f'Tomando lo que dijiste sobre "{latest_user_excerpt}", {prompt_core}'
    if strongest_area_label:
        question += (
            f" Por ahora la señal mas clara va hacia {strongest_area_label}, y quiero comprobar si eso tambien se refleja en {feature['hint']}."
        )

    return {
        "question": question,
        "feature_key": next_feature,
        "should_finalize": False,
        "rationale": (
            f'La conversacion arranco con "{first_user_excerpt}" y ahora conviene profundizar en {feature["label"]}.'
        ),
    }


def build_interview_reflection(
    answers: dict[str, Any],
    answer_updates: dict[str, float],
    evaluated_feature_key: str | None,
) -> str:
    if evaluated_feature_key and evaluated_feature_key in answer_updates:
        feature = FEATURE_INFO.get(evaluated_feature_key, {"label": "esta señal"})
        return (
            f"Entendido. Voy registrando una afinidad {_describe_score(answer_updates[evaluated_feature_key])} "
            f"en {feature['label']}."
        )

    ranked = [(AREA_INFO[feature_key]["label"], score) for feature_key, score in _rank_interest_areas(answers) if score > 1][:2]
    if not ranked:
        return "Todavia no tengo una afinidad dominante clara. Voy a hacer una pregunta mas dirigida para no inventar una señal que no aparece en tu respuesta."
    formatted = " y ".join(f"{label} ({round(score, 1)}/5)" for label, score in ranked)
    return (
        f"Con lo que contaste, por ahora veo mas señal en {formatted}. "
        "Voy a profundizar donde hay evidencia real y a bajar el peso de las areas que no se sostienen."
    )


def generate_interview_assistant_turn(
    answers: dict[str, Any],
    user_messages: list[str],
    max_follow_up_questions: int = 4,
    mode: str = "advance",
    evaluated_feature_key: str | None = None,
    evaluated_feature_score: float | None = None,
) -> dict[str, Any]:
    if mode == "start":
        return {
            "messages": [OPENING_PROMPT],
            "feature_key": None,
            "should_finalize": False,
            "rationale": "Inicio del analisis conversacional.",
            "answer_updates": {},
            "merged_answers": {key: float(value) for key, value in answers.items() if value is not None},
        }

    answer_updates = extract_answer_updates(answers, user_messages, evaluated_feature_key)
    merged_answers = {key: float(value) for key, value in answers.items() if value is not None}
    merged_answers.update(answer_updates)
    reflection = build_interview_reflection(merged_answers, answer_updates, evaluated_feature_key)
    next_turn = generate_interview_turn(merged_answers, user_messages, max_follow_up_questions)
    return {
        "messages": [reflection, next_turn["question"]],
        "feature_key": next_turn["feature_key"],
        "should_finalize": next_turn["should_finalize"],
        "rationale": next_turn["rationale"],
        "answer_updates": answer_updates,
        "merged_answers": merged_answers,
    }


def generate_action_plan_content(
    chat_label: str,
    chat_context: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    user_excerpts = chat_context.get("user_excerpts", [])
    assistant_prompts = chat_context.get("assistant_prompts", [])
    focus_areas = chat_context.get("focus_areas", [])
    chat_line = user_excerpts[0] if user_excerpts else "lo que contaste en la conversacion"
    prompt_line = assistant_prompts[-1] if assistant_prompts else ""

    if not recommendations:
        return {
            "title": f"Plan de {chat_label}",
            "summary": (
                f"Este plan sale de tu conversacion {chat_label.lower()}. "
                f"Voy a convertir lo que dijiste sobre \"{chat_line}\" en pasos exploratorios antes de cerrar una recomendacion."
            ),
            "steps": [
                {
                    "title": "Aterrizar lo que dijiste",
                    "description": (
                        f"Resume por que mencionaste \"{chat_line}\" y que parte de ese interes quisieras explorar primero."
                    ),
                    "priority": "high",
                },
                {
                    "title": "Probar una actividad corta",
                    "description": "Haz una actividad breve relacionada con el tema que mas repetiste para validar si el interes se sostiene fuera del chat.",
                    "priority": "high",
                },
                {
                    "title": "Volver con mas contexto",
                    "description": (
                        f"Regresa al chat con un ejemplo concreto de experiencia, materia o proyecto para responder mejor esta pregunta: \"{prompt_line}\"."
                        if prompt_line
                        else "Regresa al chat con un ejemplo concreto de experiencia, materia o proyecto para afinar el siguiente plan."
                    ),
                    "priority": "medium",
                },
            ],
        }

    top = recommendations[0]
    alternative = recommendations[1] if len(recommendations) > 1 else None
    top_name = str(top["program_name"])
    top_support = top["supporting_factors"][0] if top["supporting_factors"] else f"Tu conversacion deja señales compatibles con {top_name}."
    top_development = (
        top["development_factors"][0]
        if top["development_factors"]
        else "Todavia conviene probar la opcion con una actividad concreta antes de decidir."
    )
    alternative_name = str(alternative["program_name"]) if alternative else "otra opcion cercana"

    return {
        "title": f"Plan de {chat_label}: explorar {top_name}",
        "summary": (
            f"Este plan fue generado desde lo que dijiste en {chat_label.lower()}, especialmente cuando mencionaste \"{chat_line}\". "
            f"La idea es comprobar si {top_name} realmente encaja contigo y compararlo con {alternative_name} antes de tomarlo como direccion principal."
        ),
        "steps": [
            {
                "title": f"Entender mejor {top_name}",
                "description": (
                    f"Revisa las asignaturas introductorias, enfoques y contextos reales de {top_name}. "
                    f"Empiezo por ahi porque {top_support}"
                ),
                "priority": "high",
            },
            {
                "title": f"Probar {top_name} en pequeño",
                "description": (
                    f"Haz una actividad corta, observacion guiada o ejercicio practico relacionado con {top_name}. "
                    f"Eso sirve para aterrizar la conversacion y validar si el interes se sostiene. {top_development}"
                ),
                "priority": "high",
            },
            {
                "title": f"Comparar con {alternative_name}",
                "description": (
                    f"Contrasta {top_name} con {alternative_name} mirando tareas tipicas, habilidades requeridas y tipo de entorno. "
                    + (f"Vuelve sobre esta pregunta del chat: \"{prompt_line}\"." if prompt_line else "")
                ),
                "priority": "medium",
            },
            {
                "title": "Cerrar una decision exploratoria",
                "description": (
                    f"Escribe que parte de {top_name} te interesa explorar primero, que duda sigue abierta y que señal te haria mantener o descartar esta opcion."
                    + (f" Tus temas mas visibles en el chat fueron {', '.join(focus_areas)}." if focus_areas else "")
                ),
                "priority": "medium",
            },
        ],
    }


def deterministic_reply(user_input: str, context: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_text(user_input)
    recommendations = context.get("recommendations", [])
    action_plan = context.get("action_plan")

    if "explica" in normalized and recommendations:
        top = recommendations[0]
        return {
            "content": (
                f"Tu recomendacion principal actual es {str(top['program_slug']).replace('-', ' ')} con un puntaje de compatibilidad de {top['compatibility_score']}. "
                "La explicacion se basa en tu conversacion, el perfil calculado y las coincidencias mas fuertes."
            ),
            "citations": [],
        }
    if "plan" in normalized and action_plan:
        return {
            "content": f"Tu plan activo es {action_plan['title']}. Tiene {len(action_plan['steps'])} pasos principales.",
            "citations": [],
        }
    return {
        "content": "No pude interpretar completamente tu pregunta. Puedo ayudarte a revisar tus recomendaciones, explicar tus resultados, comparar opciones o mostrar tu plan.",
        "citations": [],
    }
