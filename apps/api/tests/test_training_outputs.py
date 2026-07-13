from pathlib import Path


def test_training_artifacts_exist() -> None:
    root = Path(__file__).resolve().parents[3]
    assert (root / "intelligence" / "datasets" / "synthetic_vocational_dataset.csv").exists()
    assert (root / "intelligence" / "models" / "artifacts" / "approved_model.joblib").exists()
    assert (root / "intelligence" / "evaluation" / "output" / "metrics.json").exists()
