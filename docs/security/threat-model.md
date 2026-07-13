# Threat Model

- Riesgo: acceso a recursos de otro usuario por IDOR.
  Mitigacion: todas las consultas principales filtran por `user_id`.
- Riesgo: fuga de respuestas sensibles en logs.
  Mitigacion: logs estructurados sin respuestas completas.
- Riesgo: LLM como decisor.
  Mitigacion: proveedor determinista por defecto y proveedor externo opcional desacoplado.
- Riesgo: inyeccion en consultas.
  Mitigacion: SQLAlchemy parametrizado y ausencia de ejecucion dinamica.
