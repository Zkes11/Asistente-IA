# FINAL_REPORT

## Implementado

- Monorepo modular con frontend Next.js y API FastAPI.
- Registro, login y perfil.
- Cuestionario vocacional versionado con respuestas parciales.
- Motor hibrido con:
  - reglas YAML,
  - scorer ML demo entrenado con datos sinteticos,
  - scorer de grafo simplificado,
  - calculo de confianza y abstencion.
- Resultados explicables con puntaje de compatibilidad, reglas activadas, factores favorables y de desarrollo.
- Catalogo demo de programas y universidades.
- Plan de accion editable.
- Chat determinista sin proveedor externo.
- Ontologia OWL, exportacion Prolog y dataset sintetico.

## Decisiones clave

- Monolito modular en lugar de microservicios.
- LLM fuera del camino de decision principal.
- Datos sinteticos para entrenamiento y demostracion.
- Validacion local con Python 3.11 por compatibilidad binaria; Python 3.14 no era viable para el stack cientifico en Windows.

## Como iniciar hoy

### Local

- Web: `http://127.0.0.1:3000`
- API: `http://127.0.0.1:8000/api/v1`

Comandos:

```bash
npm install
cd apps/api
py -3.11 -m pip install -e .[dev]
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
npm run dev --workspace web -- --hostname 127.0.0.1 --port 3000
```

### Docker

Existe `docker-compose.yml`, pero en esta sesion no pudo validarse porque Docker Desktop no tenia engine activo.

## Credenciales demo locales

- No se dejaron credenciales hardcodeadas.
- El flujo verificado crea usuarios desde la pantalla de registro.

## Resultados de pruebas

- Frontend:
  - `npm run typecheck --workspace web`: pasa
  - `npm run build --workspace web`: pasa
  - `npm run lint --workspace web`: pasa
  - `npm run test --workspace web`: pasa
- Backend:
  - `py -3.11 -m pytest`: 4 pruebas, todas pasan
  - `py -3.11 -m ruff check app tests`: pasa
  - `py -3.11 -m mypy app`: pasa

## Cobertura

- No se genero reporte de cobertura agregado en esta iteracion.

## Metricas del modelo

- Modelo seleccionado en la corrida demo: `logreg`
- Artefacto generado: `intelligence/models/artifacts/approved_model.joblib`
- Metricas: `intelligence/evaluation/output/metrics.json`

## Riesgos conocidos

- El pipeline Docker no fue validado por indisponibilidad del engine local.
- Neo4j y Redis aun no estan cubiertos por pruebas de integracion reales.
- La administracion completa sigue pendiente.

## Limitaciones

- El catalogo es de demostracion y no usa fuentes externas verificadas.
- El grafo de conocimiento usa un scorer simplificado para la ejecucion local.
- El panel administrativo y el reporte PDF completo aun no estan cerrados.

## Funcionalidades pendientes reales

- CRUD administrativo completo.
- E2E con Playwright.
- Integracion verificada con PostgreSQL, Redis y Neo4j bajo Docker.
- Reporte PDF formal.

## Evidencia de datos autorizados

- El dataset de ML es sintetico y se genera localmente en `intelligence/datasets/generate_synthetic_dataset.py`.
- Las universidades y programas se marcan como `Datos de demostracion`.
