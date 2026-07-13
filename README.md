# OrientaIA

OrientaIA es una plataforma de orientacion vocacional exploratoria con un motor hibrido verificable. Combina cuestionario versionado, reglas expertas, clasificacion supervisada sobre datos sinteticos, explicaciones trazables, plan de accion y un asistente conversacional desacoplado del motor de recomendacion.

## Stack

- `apps/web`: Next.js App Router, React, TypeScript, Tailwind, React Query, React Hook Form, Zod, Recharts, Vitest.
- `apps/api`: FastAPI, SQLAlchemy async, Pydantic, Argon2id, JWT, pytest, Ruff, mypy.
- `intelligence/`: reglas YAML, exportacion Prolog, ontologia OWL, dataset sintetico, entrenamiento y artefactos.

## Estructura

- `apps/web`
- `apps/api`
- `packages/contracts`
- `packages/ui`
- `intelligence`
- `docs`

## Inicio local

### Requisitos

- Node.js 22+
- Python 3.11
- Docker Desktop opcional para la ruta con contenedores

### Instalar

```bash
npm install
cd apps/api
py -3.11 -m pip install -e .[dev]
```

### Ejecutar local

API:

```bash
cd apps/api
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Web:

```bash
npm run dev --workspace web -- --hostname 127.0.0.1 --port 3000
```

### Dataset y modelo demo

```bash
py -3.11 intelligence/datasets/generate_synthetic_dataset.py
py -3.11 intelligence/training/train_models.py
```

## Verificacion ejecutada

- `npm run typecheck --workspace web`
- `npm run build --workspace web`
- `npm run lint --workspace web`
- `npm run test --workspace web`
- `py -3.11 -m pytest`
- `py -3.11 -m ruff check app tests`
- `py -3.11 -m mypy app`

## Limites actuales

- El panel administrativo completo no esta terminado.
- La ruta Docker Compose no se pudo validar en esta sesion porque Docker Desktop no tenia engine activo.
- Neo4j y Redis estan modelados en arquitectura y configuracion, pero la ejecucion verificada en esta iteracion fue local con SQLite async.

Consulta [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) y [FINAL_REPORT.md](FINAL_REPORT.md) para el estado real de la implementacion.
