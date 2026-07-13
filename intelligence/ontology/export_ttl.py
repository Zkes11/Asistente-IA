from pathlib import Path

from rdflib import Graph


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    owl_path = base_dir / "orientaia.owl"
    ttl_path = base_dir / "orientaia.ttl"
    graph = Graph()
    graph.parse(owl_path)
    graph.serialize(ttl_path, format="turtle")
    print(f"Exportado: {ttl_path}")


if __name__ == "__main__":
    main()
