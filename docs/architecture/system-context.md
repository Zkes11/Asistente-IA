# System Context

```mermaid
flowchart LR
  Student[Estudiante] --> Web[Frontend Next.js]
  Counselor[Orientador] --> Web
  Admin[Administrador] --> Web
  Web --> API[API FastAPI]
  API --> Postgres[(PostgreSQL + pgvector)]
  API --> Redis[(Redis)]
  API --> Neo4j[(Neo4j)]
  API --> Rules[Reglas YAML]
  API --> Model[Modelo supervisado]
  API --> Owl[Ontologia OWL]
  API --> Prolog[Exportacion Prolog]
```
