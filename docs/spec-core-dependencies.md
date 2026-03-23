# coop · spec-core-dependencies · v1.0

## Syfte

Definiera vilka core-beroenden coop skall bära så att projekt som använder
coop via `_framework/` ärver all infrastruktur utan egna beroenden.

---

## Core-beroenden

| Bibliotek | Version | Ansvar |
|-----------|---------|--------|
| `pydantic` | >=2.0 | Datamodeller, validering, kontrakt |
| `pydantic-settings` | >=2.0 | Settings, config, env-vars, .env-filer |
| `fastapi` | >=0.100 | HTTP API-lager, transport mot iOS och externa klienter |
| `sqlmodel` | >=0.0.14 | SQL + Pydantic, lokal datalagring (SQLite default) |

---

## Ansvarsfördelning

**coop äger:**
- Datavalidering (Pydantic)
- Settings och config (pydantic-settings)
- HTTP-transport (FastAPI)
- Lokal persistence (SQLModel + SQLite)
- Fil-IO
- Debug-logging med konfigurerbar log-path

**Projektet äger:**
- Domänlogik
- Handlers: `api`, `terminal`, `shell`
- Projektspecifika Pydantic-modeller

---

## Debug-konfiguration

Coop skall läsa `coop.config.json` vid start:

```json
{
  "debug": false,
  "log_path": "../../_debug/"
}
```

- `debug: true` — coop skriver events och errors till `log_path`
- `debug: false` — tyst körning, inga loggar skrivs
- Agenten kan sätta debug-läge utan att ändra kod

---

## Settings-hierarki (pydantic-settings)

Prioritetsordning (högst vinner):

1. Miljövariabler
2. `.env`-fil i projektroot
3. `coop.config.json`
4. Default-värden i kod

---

## Persistence

- Default: SQLite-fil under `_runtime-files/`
- Path konfigureras via `coop.config.json` eller env-var
- SQLModel-modeller definieras i projektet, coop tillhandahåller engine

---

## Vad som redan finns i coop

| Modul | Status |
|-------|--------|
| `handlers/api.py` — ApiHandler, SSE + JSON collect, FastAPI-redo | ✅ |
| `handlers/terminal.py` — TerminalHandler, stdout rendering | ✅ |
| `sdk/handler.py` — BaseHandler med dispatch | ✅ |
| `sdk/agent.py` — BaseAgent | ✅ |
| `sdk/registry.py` — handler/agent registry | ✅ |
| `runner.py` — execution engine | ✅ |
| `events.py` — typade events | ✅ |
| `manifest.py` — manifest loading | ✅ |

## PENDING implementation

- [ ] Lägg till dependencies i `pyproject.toml` (pydantic, pydantic-settings, fastapi, sqlmodel)
- [ ] `handlers/shell.py` — icke-interaktiv shell, returnerar stdout/returncode
- [ ] `coop/config.py` — läser `coop.config.json`, debug-toggle, log-path
- [ ] `coop/db.py` — SQLModel engine, SQLite, session-hantering
- [ ] `coop/files.py` — fil-IO utilities
- [ ] `coop/debug.py` — Pydantic-baserad debug-logging till konfigurerbar path
- [ ] Tester för varje ny modul
