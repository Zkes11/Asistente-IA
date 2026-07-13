from app.services.rules import load_rules, score_rules


def test_ruleset_loads() -> None:
    rules = load_rules()
    assert len(rules) >= 20


def test_rule_scoring_triggers_expected_programs() -> None:
    scores, triggered, abstentions = score_rules(
        {
            "interest_technology": 5,
            "interest_social": 3,
            "communication": 3,
            "empathy": 3,
            "logical_reasoning": 5,
            "interest_data": 4,
            "numerical_skill": 4,
            "organization": 4,
        }
    )
    assert scores["ingenieria-de-sistemas"] > 0
    assert scores["ciencia-de-datos"] > 0
    assert triggered
    assert abstentions == []
