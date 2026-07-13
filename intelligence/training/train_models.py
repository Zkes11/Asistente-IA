from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "synthetic_vocational_dataset.csv"
ARTIFACTS_DIR = ROOT / "models" / "artifacts"
EVAL_DIR = ROOT / "evaluation" / "output"


def ensure_dataset() -> list[dict[str, str]]:
    if not DATASET_PATH.exists():
        from importlib.util import module_from_spec, spec_from_file_location

        generator_path = ROOT / "datasets" / "generate_synthetic_dataset.py"
        spec = spec_from_file_location("generate_synthetic_dataset", generator_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("No fue posible cargar el generador sintetico")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    return load_rows()


def load_rows() -> list[dict[str, str]]:
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def build_preprocessor(feature_order: list[str], numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    numeric_indices = [feature_order.index(column) for column in numeric]
    categorical_indices = [feature_order.index(column) for column in categorical]
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_indices),
            (
                "cat",
                Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                        ]
                ),
                categorical_indices,
            ),
        ]
    )


def build_arrays(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, list[str], list[str], list[str]]:
    categorical = ["work_environment", "preferred_modality"]
    feature_order = [column for column in rows[0].keys() if column != "academic_area_label"]
    numeric = [column for column in feature_order if column not in categorical]
    x_rows: list[list[object]] = []
    y_rows: list[str] = []
    for row in rows:
        x_rows.append([float(row[column]) if column in numeric else row[column] for column in feature_order])
        y_rows.append(row["academic_area_label"])
    return np.array(x_rows, dtype=object), np.array(y_rows), feature_order, numeric, categorical


def evaluate_model(name: str, model: Pipeline, x_train: np.ndarray, x_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray) -> dict[str, object]:
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test) if hasattr(model, "predict_proba") else None
    metrics: dict[str, object] = {
        "accuracy": accuracy_score(y_test, predictions),
        "balanced_accuracy": balanced_accuracy_score(y_test, predictions),
        "f1_macro": f1_score(y_test, predictions, average="macro"),
        "f1_weighted": f1_score(y_test, predictions, average="weighted"),
        "classification_report": classification_report(y_test, predictions, output_dict=True),
    }
    if probabilities is not None:
        metrics["top_3_accuracy"] = top_k_accuracy_score(
            y_test,
            probabilities,
            k=3,
            labels=model.named_steps["model"].classes_,
        )
    return {"name": name, "pipeline": model, "metrics": metrics}


def candidate_score(metrics: dict[str, object]) -> tuple[float, float, float]:
    f1_macro = float(metrics["f1_macro"])
    balanced_accuracy = float(metrics["balanced_accuracy"])
    top_3_accuracy = float(metrics.get("top_3_accuracy", 0.0))
    return (f1_macro, balanced_accuracy, top_3_accuracy)


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    rows = ensure_dataset()
    x, y, feature_order, numeric, categorical = build_arrays(rows)
    preprocessor = build_preprocessor(feature_order, numeric, categorical)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)

    candidates = [
        ("dummy", DummyClassifier(strategy="prior")),
        ("logreg", LogisticRegression(max_iter=2500, random_state=42)),
        ("tree", DecisionTreeClassifier(max_depth=10, random_state=42)),
        ("forest", RandomForestClassifier(n_estimators=260, random_state=42)),
        ("gboost", GradientBoostingClassifier(random_state=42)),
        (
            "mlp",
            MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                alpha=0.0008,
                learning_rate_init=0.008,
                max_iter=900,
                early_stopping=False,
                random_state=42,
            ),
        ),
    ]

    results = []
    for name, estimator in candidates:
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        results.append(evaluate_model(name, pipeline, x_train, x_test, y_train, y_test))

    best = max(results, key=lambda item: candidate_score(item["metrics"]))  # type: ignore[arg-type]
    bundle = {
        "version": f"candidate-2026.2-{best['name']}",
        "model": best["pipeline"],
        "feature_order": feature_order,
        "labels": list(best["pipeline"].named_steps["model"].classes_),
        "trained_at": datetime.now(UTC).isoformat(),
    }
    joblib.dump(bundle, ARTIFACTS_DIR / "approved_model.joblib")

    metrics_payload = {
        "selected_model": best["name"],
        "selected_metrics": best["metrics"],
        "candidates": {item["name"]: item["metrics"] for item in results},
        "feature_sets": {"numeric": numeric, "categorical": categorical},
        "status": "candidate",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    (EVAL_DIR / "metrics.json").write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    (EVAL_DIR / "classification_report.json").write_text(
        json.dumps(best["metrics"]["classification_report"], indent=2), encoding="utf-8"
    )
    (ROOT / "model_cards" / "model_card.md").write_text(
        "# Model Card\n\nModelo candidato entrenado solo con datos sinteticos de demostracion.\n",
        encoding="utf-8",
    )
    (ROOT / "model_cards" / "dataset_card.md").write_text(
        "# Dataset Card\n\nDataset sintetico para desarrollo y pruebas. No contiene datos reales.\n",
        encoding="utf-8",
    )
    (EVAL_DIR / "training_manifest.json").write_text(
        json.dumps({"generated_at": datetime.now(UTC).isoformat(), "dataset_rows": len(rows)}, indent=2),
        encoding="utf-8",
    )
    print(f"Modelo seleccionado: {best['name']}")


if __name__ == "__main__":
    main()
