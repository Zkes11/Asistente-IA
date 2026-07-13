from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import delete, select

from app.db.models import (
    AcademicArea,
    AcademicProgram,
    AssessmentDefinition,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentSection,
    AssessmentVersion,
    ExpertRule,
    ModelVersion,
    Role,
    RoleName,
    RuleVersion,
    User,
    UserProfile,
    UserRole,
    University,
)
from app.security.passwords import hash_password
from app.db.session import SessionLocal
from app.services.rules import load_rules

AREAS = [
    ("tecnologia-ingenieria", "Tecnologia e Ingenieria"),
    ("datos", "Datos y Analitica"),
    ("ciberseguridad", "Ciberseguridad"),
    ("sociales", "Ciencias Sociales"),
    ("psicologia", "Psicologia y Comportamiento"),
    ("comunicacion", "Comunicacion"),
    ("diseno", "Diseno"),
    ("negocios", "Negocios"),
    ("salud", "Salud"),
    ("naturales", "Ciencias Naturales"),
    ("educacion", "Educacion"),
    ("aplicadas", "Areas Tecnicas y Aplicadas"),
]

PROGRAMS = [
    ("ingenieria-de-sistemas", "Ingenieria de Sistemas", "tecnologia-ingenieria"),
    ("ingenieria-de-software", "Ingenieria de Software", "tecnologia-ingenieria"),
    ("ingenieria-industrial", "Ingenieria Industrial", "tecnologia-ingenieria"),
    ("ciencia-de-datos", "Ciencia de Datos", "datos"),
    ("analitica-de-negocios", "Analitica de Negocios", "datos"),
    ("ciberseguridad", "Ciberseguridad", "ciberseguridad"),
    ("psicologia", "Psicologia", "psicologia"),
    ("trabajo-social", "Trabajo Social", "sociales"),
    ("comunicacion-social", "Comunicacion Social", "comunicacion"),
    ("periodismo-digital", "Periodismo Digital", "comunicacion"),
    ("diseno-grafico", "Diseno Grafico", "diseno"),
    ("diseno-ux-ui", "Diseno UX/UI", "diseno"),
    ("administracion-de-empresas", "Administracion de Empresas", "negocios"),
    ("marketing-digital", "Marketing Digital", "negocios"),
    ("enfermeria", "Enfermeria", "salud"),
    ("biologia", "Biologia", "naturales"),
    ("educacion", "Educacion", "educacion"),
    ("gestion-ambiental", "Gestion Ambiental", "naturales"),
    ("logistica", "Logistica", "aplicadas"),
    ("mecatronica", "Mecatronica", "tecnologia-ingenieria"),
    ("gastronomia", "Gastronomia", "aplicadas"),
    ("produccion-audiovisual", "Produccion Audiovisual", "comunicacion"),
    ("finanzas", "Finanzas", "negocios"),
    ("fisioterapia", "Fisioterapia", "salud"),
    ("quimica-aplicada", "Quimica Aplicada", "naturales"),
]

QUESTIONS = [
    ("intereses", "interest_technology", "Que tanto te atrae la tecnologia y crear soluciones digitales?", "slider"),
    ("intereses", "interest_social", "Que tanto disfrutas ayudar y acompanar a otras personas?", "slider"),
    ("intereses", "interest_design", "Que tanto te interesa el diseno visual o de experiencias?", "slider"),
    ("intereses", "interest_health", "Que tanto te atraen los contextos de salud y cuidado?", "slider"),
    ("intereses", "interest_business", "Que tanto te interesa liderar o gestionar proyectos?", "slider"),
    ("intereses", "interest_data", "Que tanto disfrutas analizar datos y patrones?", "slider"),
    ("habilidades", "logical_reasoning", "Como evaluras tu razonamiento logico?", "likert"),
    ("habilidades", "communication", "Que tan comodo te sientes comunicando ideas?", "likert"),
    ("habilidades", "empathy", "Que tan facil te resulta comprender a otras personas?", "likert"),
    ("habilidades", "creativity", "Que tanto disfrutas proponer ideas originales?", "likert"),
    ("habilidades", "numerical_skill", "Que tan fuerte te consideras en habilidades numericas?", "likert"),
    ("habilidades", "visual_thinking", "Que tan facil te resulta pensar visualmente?", "likert"),
    ("preferencias", "organization", "Que tan organizado te consideras al trabajar?", "likert"),
    ("preferencias", "teamwork_preference", "Prefieres trabajar en equipo?", "likert"),
    ("preferencias", "autonomy_preference", "Prefieres trabajar con autonomia?", "likert"),
    ("aprendizaje", "practical_learning", "Disfrutas aprender haciendo?", "likert"),
    ("aprendizaje", "theoretical_learning", "Disfrutas profundizar en conceptos teoricos?", "likert"),
]


async def main() -> None:
    await seed(reset=True)


async def seed(reset: bool = True) -> None:
    async with SessionLocal() as session:
        if reset:
            for model in [University, AcademicProgram, AcademicArea, ModelVersion, ExpertRule, Role, AssessmentVersion, AssessmentOption, AssessmentQuestion, AssessmentSection, AssessmentDefinition]:
                await session.execute(delete(model))
            await session.commit()
        existing_definition = (
            await session.execute(select(AssessmentDefinition).where(AssessmentDefinition.slug == "orientaia-main"))
        ).scalar_one_or_none()
        if existing_definition is not None and not reset:
            return

        roles = [Role(name=RoleName.student), Role(name=RoleName.counselor), Role(name=RoleName.admin)]
        session.add_all(roles)
        await session.flush()

        demo_user = User(
            email="demo@orientaia.local",
            password_hash=hash_password("demo-orientaia-123"),
            preferred_name="Estudiante Demo",
            is_active=True,
        )
        session.add(demo_user)
        await session.flush()
        session.add(
            UserProfile(
                user_id=demo_user.id,
                grade_level="11",
                country="Colombia",
                city="Bogota",
                goal="explorar",
                known_areas=["Tecnologia", "Diseno"],
                onboarding_completed=True,
                privacy_policy_accepted=True,
                assessment_consent=True,
                guardian_consent_required=False,
                guardian_consent_granted=False,
            )
        )
        student_role = next(role for role in roles if role.name == RoleName.student)
        session.add(UserRole(user_id=demo_user.id, role_id=student_role.id))

        area_models = [
            AcademicArea(slug=slug, name=name, description=f"Area de demostracion para {name}.")
            for slug, name in AREAS
        ]
        session.add_all(area_models)

        for slug, name, area_slug in PROGRAMS:
            session.add(
                AcademicProgram(
                    slug=slug,
                    name=name,
                    academic_area_slug=area_slug,
                    short_description=f"Programa de demostracion orientado a {name.lower()} con informacion educativa general.",
                    metadata_json={
                        "duration": "8 semestres",
                        "modality": "Mixta",
                        "skills": ["Pensamiento critico", "Comunicacion", "Aprendizaje continuo"],
                        "typical_subjects": ["Fundamentos", "Proyecto integrador", "Contexto profesional"],
                        "occupational_fields": ["Practica profesional orientativa", "Investigacion aplicada"],
                        "warning": "Datos de demostracion",
                    },
                )
            )

        for index in range(1, 6):
            session.add(
                University(
                    slug=f"universidad-demo-{index}",
                    name=f"Universidad Demo {index}",
                    city="Bogota",
                    country="Colombia",
                    is_demo_data=True,
                )
            )

        definition = AssessmentDefinition(
            slug="orientaia-main",
            title="Cuestionario vocacional OrientaIA",
            description="Cuestionario exploratorio para identificar afinidades academicas.",
            current_version="2026.1",
        )
        session.add(definition)
        await session.flush()
        section_models: dict[str, AssessmentSection] = {}
        for order, key in enumerate(["intereses", "habilidades", "preferencias", "aprendizaje"], start=1):
            section = AssessmentSection(
                definition_id=definition.id,
                key=key,
                title=key.capitalize(),
                description=f"Bloque de {key}.",
                order_index=order,
            )
            session.add(section)
            await session.flush()
            section_models[key] = section

        for order, (section_key, key, prompt, question_type) in enumerate(QUESTIONS, start=1):
            question = AssessmentQuestion(
                section_id=section_models[section_key].id,
                key=key,
                prompt=prompt,
                help_text="Escala de 1 a 5.",
                question_type=question_type,
                order_index=order,
                config={"min": 1, "max": 5, "step": 1, "estimated_seconds": 25},
            )
            session.add(question)
            await session.flush()
            for value in range(1, 6):
                session.add(
                    AssessmentOption(
                        question_id=question.id,
                        label=str(value),
                        value=str(value),
                        weight_map={key: float(value)},
                        order_index=value,
                    )
                )

        session.add(
            AssessmentVersion(
                definition_id=definition.id,
                version="2026.1",
                is_active=True,
                schema_snapshot={"question_count": len(QUESTIONS)},
            )
        )

        for rule in load_rules():
            expert_rule = ExpertRule(rule_key=rule.id, current_version=rule.version, enabled=rule.enabled)
            session.add(expert_rule)
            await session.flush()
            session.add(RuleVersion(rule_id=expert_rule.id, version=rule.version, definition=rule.model_dump()))

        session.add(
            ModelVersion(
                version="demo-heuristic-v0",
                status="candidate",
                artifact_path="intelligence/models/artifacts/approved_model.joblib",
                metrics={"note": "Pendiente entrenamiento o fallback heuristico."},
                approved_at=datetime.now(UTC),
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
