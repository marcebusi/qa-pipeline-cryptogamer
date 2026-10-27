# qa-pipeline-cryptogamer

![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions)
![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-Pipeline-0078D7?logo=azuredevops)
![CI](https://github.com/marcebusi/qa-pipeline-cryptogamer/actions/workflows/qa-master.yml/badge.svg)

Proyecto 6 del portfolio de QA — **Pipeline de integración** que orquesta todas las suites de test sobre [cryptogamer-ecommerce](https://github.com/marcebusi/cryptogamer-ecommerce) usando **GitHub Actions** y **Azure DevOps**.

---

## Arquitectura del pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    TRIGGER                              │
│   push/PR a main · Cron diario 6AM · Manual dispatch   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 1 — Setup Backend                               │
│  • Clone cryptogamer-ecommerce                         │
│  • npm ci + prisma migrate + prisma db seed            │
│  • Publica dev.db como artifact compartido             │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  JOB 1       │ │  JOB 2       │ │  JOB 3       │
│  🎭 E2E      │ │  🔌 API      │ │  🗄️ Data     │
│  Playwright  │ │  Playwright  │ │  Quality     │
│  @smoke tags │ │  41 tests    │ │  pytest      │
│              │ │              │ │  46 tests    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                        │  (solo en push a main)
                        ▼
          ┌─────────────────────────┐
          │  JOB 4 — ⚡ Performance │
          │  k6 smoke test          │
          │  1 VU · 15 checks       │
          └─────────────────────────┘
                        │
                        ▼
          ┌─────────────────────────┐
          │  JOB 5 — 📊 Summary     │
          │  GitHub Step Summary    │
          │  Artifacts combinados   │
          └─────────────────────────┘
```

---

## Jobs en detalle

| Job | Herramienta | Tests | Cuándo corre |
|---|---|---|---|
| Setup Backend | Node.js + Prisma | — | Siempre |
| E2E Tests | Playwright (TypeScript) | Smoke suite | Siempre |
| API Tests | Playwright (TypeScript) | 41 tests | Siempre |
| Data Quality | pytest + pandas | 46 tests | Siempre |
| Performance Smoke | k6 | 15 checks | Solo en push a `main` |
| Summary | Bash + artifacts | — | Siempre (al final) |

---

## GitHub Actions — Características clave

### Paralelismo
Los jobs 1, 2 y 3 corren **en paralelo** — `needs: setup-backend` garantiza que el backend esté listo, pero las suites no se esperan entre sí. Esto reduce el tiempo total del pipeline ~3x.

### Artifact compartido
La DB (`dev.db`) se genera una sola vez en Setup y se comparte via `upload-artifact` / `download-artifact` para evitar regenerarla en cada job.

### Concurrency
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
Si se pushea dos veces seguido, el run anterior se cancela automáticamente.

### Dispatch manual con selector de suite
```yaml
workflow_dispatch:
  inputs:
    suite:
      type: choice
      options: [all, e2e, api, data-quality, performance]
```
Permite correr solo la suite que necesitás sin esperar el pipeline completo.

### Step Summary
El job final genera una tabla de resultados visible directamente en la UI de GitHub Actions, sin entrar a los artifacts.

---

## Azure DevOps — Características clave

### Stages y dependencias
```
Setup → Tests (paralelo) → Performance (solo main)
```

### PublishTestResults
```yaml
- task: PublishTestResults@2
  inputs:
    testResultsFormat: JUnit
    testResultsFiles: '**/*.xml'
```
Integra los resultados en la vista nativa de Azure DevOps Test Plans — no hace falta abrir reportes HTML.

### Artifacts tipados
```yaml
- publish: path/to/report
  artifact: APIReport
```
Cada suite publica su reporte como artifact nombrado, descargable desde el pipeline.

---

## Scripts de utilidad

### `scripts/check-health.sh`
Espera que el backend esté disponible antes de correr los tests:
```bash
./scripts/check-health.sh http://localhost:3001 30
```

### `scripts/generate-summary.py`
Consolida todos los archivos JUnit XML en un reporte HTML unificado:
```bash
python scripts/generate-summary.py --reports-dir all-reports --output summary.html
```

---

## Conceptos CI/CD demostrados

| Concepto | Implementación |
|---|---|
| **Paralelismo de jobs** | 3 suites corren al mismo tiempo |
| **Artifact sharing** | DB generada una vez, compartida entre jobs |
| **Concurrency control** | Cancela runs duplicados |
| **Scheduled runs** | Cron diario a las 6AM UTC |
| **Manual dispatch** | Selector de suite por parámetro |
| **Conditional execution** | Performance solo en `main` |
| **Step Summary** | Reporte inline en GitHub UI |
| **Multi-platform CI** | GitHub Actions + Azure DevOps |
| **Health check** | Script que espera que el backend responda |

---

## Proyectos relacionados

| # | Proyecto | Repo |
|---|---|---|
| 1 | E2E con Playwright + TypeScript | [qa-playwright-cryptogamer](https://github.com/marcebusi/qa-playwright-cryptogamer) |
| 2 | API Testing con Playwright + Newman | [qa-api-testing-cryptogamer](https://github.com/marcebusi/qa-api-testing-cryptogamer) |
| 3 | E2E con Robot Framework | [qa-robot-framework-cryptogamer](https://github.com/marcebusi/qa-robot-framework-cryptogamer) |
| 4 | Performance Testing con k6 | [qa-performance-cryptogamer](https://github.com/marcebusi/qa-performance-cryptogamer) |
| 5 | Data Quality con Python + Streamlit | [qa-data-quality-cryptogamer](https://github.com/marcebusi/qa-data-quality-cryptogamer) |
| 6 | Pipeline integrado (GitHub Actions + Azure DevOps) | ← este repo |

---

## Autor

**Marcelo Busignani** — QA Engineer  
[LinkedIn](https://www.linkedin.com/in/marcelo-busignani/) · [GitHub](https://github.com/marcebusi)
