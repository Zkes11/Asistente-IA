from pathlib import Path


def main() -> None:
    metrics = Path(__file__).resolve().parents[1] / "evaluation" / "output" / "metrics.json"
    if metrics.exists():
        print(metrics.read_text(encoding="utf-8"))
    else:
        print("No existe metrics.json. Ejecuta train_models.py primero.")


if __name__ == "__main__":
    main()
