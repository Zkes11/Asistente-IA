from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_main_flow_smoke() -> None:
    with TestClient(app) as client:
        email = f"test-{uuid.uuid4()}@example.com"

        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "supersegura123", "preferred_name": "Alex"},
        )
        assert register.status_code == 200, register.text

        login = client.post("/api/v1/auth/login", json={"email": email, "password": "supersegura123"})
        assert login.status_code == 200, login.text

        profile = client.get("/api/v1/profile")
        assert profile.status_code == 200, profile.text

        assessment = client.get("/api/v1/assessments/current")
        assert assessment.status_code == 200, assessment.text

        create_attempt = client.post(
            "/api/v1/assessments/attempts",
            json={"definition_slug": "orientaia-main"},
        )
        assert create_attempt.status_code == 200, create_attempt.text
        attempt_id = create_attempt.json()["id"]

        answers = {
            "interest_technology": 5,
            "interest_social": 2,
            "interest_design": 3,
            "interest_health": 2,
            "interest_business": 3,
            "interest_data": 5,
            "logical_reasoning": 5,
            "communication": 3,
            "empathy": 2,
            "creativity": 3,
            "numerical_skill": 5,
            "visual_thinking": 3,
            "organization": 4,
            "teamwork_preference": 3,
            "autonomy_preference": 4,
            "practical_learning": 4,
            "theoretical_learning": 4,
        }
        patch = client.patch(
            f"/api/v1/assessments/attempts/{attempt_id}/answers",
            json={"answers": answers},
        )
        assert patch.status_code == 200, patch.text

        complete = client.post(f"/api/v1/assessments/attempts/{attempt_id}/complete")
        assert complete.status_code == 200, complete.text

        generate = client.post("/api/v1/recommendations/generate")
        assert generate.status_code == 200, generate.text
        payload = generate.json()
        assert payload["recommendations"]
        assert payload["compatibility_score"] >= 0
