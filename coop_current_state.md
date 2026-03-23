CURRENT STATE
repo: coop
updated: 2026-03-23

Vad som faktiskt finns och fungerar i main:

FUNGERAR
- ScriptRunner         kör bash-script, emittar typade events
- BaseAgent           Python-klass att ärva för att bygga en agent
- BaseHandler         Python-klass att ärva för att konsumera events
- ApiHandler          samlar events som JSON eller streamar SSE (FastAPI-redo)
- TerminalHandler     renderar events till stdout
- Registry            registrerar och slår upp handlers/agents vid runtime
- Manifest            laddar och validerar agent.json
- Events              typade event-typer: start, output, data, error, exit

SAKNAS (PENDING)
- ShellRunner        icke-interaktiv shell, returnerar stdout/returncode
- Config              debug-toggle, log-path (läser coop.config.json)
- DB                  SQLModel + SQLite, session-hantering
- Files               fil-IO utilities
- Debug               Pydantic-baserad debug-logging till konfigurerbar path
- Dependencies        pyproject.toml har inga dependencies — pydantic, fastapi, sqlmodel saknas

BRANCHES — alla är v0.1 skelett, ingen implementation
- mod/database        README only
- mod/restapi         README only
- port/bash           README only
- mod/io-files        README only
- mod/io-disks        README only
- mod/io-fs           README only
- port/api-surface    README only
- exp/*               experiment, ej canonical

URSPRUNG
ScriptRunner skapades först i projektet iKommand — en bash-portning med målet
att ge bash ett visuellt lager. coop extraherades ur iKommand som ett
återanvändbart ramverk. Shell-körning är inte ett tillägg — det är hela poängen.

ARKITEKTUR I DIREKTORU_2.0
Swift (topplager / UI) → coop ScriptRunner (runtime) → bash-scripts (SRC/)
Swift-appen är ett gränssnitt. coop är hjärtat. Swift ShellRunner är en
äldre prototyp från innan coop fanns — den är inte gällande.

NOTERA
Branches ser ut som framsteg men innehåller bara README.md med "v0.1 init".
Dra inga slutsatser om funktionalitet från branch-namn — läs denna fil.
