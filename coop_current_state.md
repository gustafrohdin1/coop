CURRENT STATE
repo: coop
updated: 2026-03-23

Status: VERIFIED = läst och bekräftad i kod | PENDING VERIFICATION = arkitekturintention, ej verifierad

---

AVSEDD ARKITEKTUR

Swift (view layer)
  → HTTP/SSE
    → FastAPI (ingångspunkt)
      → ScriptRunner (Python, kör bash)
        → bash-scripts (SRC/ i projektet)
          → events tillbaka upp samma väg

Swift hanterar UI och state.
ScriptRunner hanterar exekvering.
Swift anropar aldrig bash direkt.

---

FUNGERAR [VERIFIED]
- ScriptRunner         kör bash-script via subprocess, emittar typade events
- BaseAgent            Python-klass att ärva för att bygga en agent i Python
- BaseHandler          Python-klass att ärva för att konsumera events
- TerminalHandler      renderar events till stdout
- ApiHandler           samlar events som JSON eller streamar SSE
- Registry             registrerar och slår upp handlers/agents vid runtime
- Manifest             laddar och validerar agent.json
- Events               typade event-typer: start, output, data, error, exit

DEPENDENCIES [PENDING VERIFICATION — tillagda i pyproject.toml, ej installationstestade]
- pydantic>=2.0        validering och modeller
- fastapi>=0.110       HTTP / SSE
- uvicorn>=0.29        [optional:api] ASGI-server

FASTAPI-INTEGRATION [PENDING VERIFICATION]
- ApiHandler är skriven för FastAPI (iter_sse returnerar SSE-chunks)
- Ingen FastAPI-app eller route finns än i coop
- Nästa steg: minimal FastAPI-app som exponerar ScriptRunner via HTTP

SWIFT → COOP-BRYGGA [PENDING VERIFICATION]
- Arkitekturintention: Swift pratar HTTP mot lokal FastAPI-server
- Inget byggt än — varken Swift-sidan eller FastAPI-sidan

LOGGNING [PENDING VERIFICATION]
- Audit-loggning finns i direktoru/SRC/audit-log.sh (instansdata, hör till projekt)
- Framework-debug saknas i coop — planeras Pydantic-baserad

SAKNAS (PENDING BUILD)
- ShellRunner          icke-interaktiv shell, returnerar stdout/returncode direkt
- Config               debug-toggle, log-path
- DB                   SQLModel + SQLite
- Files                fil-IO utilities
- Debug                Pydantic-baserad framework-loggning

---

URSPRUNG
ScriptRunner skapades i iKommand — bash-portning med visuellt lager som mål.
coop extraherades ur iKommand. Shell-körning är inte ett tillägg — det är ursprunget.
Swift ShellRunner = äldre prototyp, inte gällande.

---

NOTERA
Branches med "v0.1 init" innehåller bara README. Ingen implementation.
Dra inga slutsatser om funktionalitet från branch-namn — läs denna fil.
