# Hur man bygger en modul i coop

En modul är två filer: ett manifest och ett script.
Ramverket hanterar allt annat — livscykel, event-kontrakt, validering, execution.

---

## 1. Manifest — `agents/[namn].agent.json`

Deklarerar vem modulen är, vad den tar emot och vad den emitterar.

```json
{
  "id": "[unik-id]",
  "version": "0.1.0",
  "title": "[läsbart namn]",
  "description": "[vad modulen gör — en mening]",
  "script": "../scripts/[namn].py",
  "input_schema": {
    "type": "object",
    "properties": {
      "[param]": {
        "type": "string | integer | boolean",
        "description": "[vad parametern gör]",
        "default": "[defaultvärde]"
      }
    }
  },
  "output_schema": {
    "description": "[vad som emitteras]",
    "event_types": ["start", "data", "output", "error", "exit"]
  },
  "constraints": {
    "timeout": 30,
    "requires_admin": false,
    "network_allowed": false
  }
}
```

`constraints` är inte valfria — de är ramverkets policy. Sätt dem rätt.

---

## 2. Script — `scripts/[namn].py`

Scriptet läser input via `AGENT_INPUT` och emitterar events till stdout.

```python
#!/usr/bin/env python3
import json
import os
import sys

# --- Event helpers ---

def emit(event_type: str, **kwargs):
    payload = {"event": event_type, "agent": "[id]", **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()

def emit_start():   emit("start")
def emit_data(d):   emit("data", **d)
def emit_output(s): emit("output", message=s)
def emit_error(s):  emit("error", message=s)
def emit_exit(code=0): emit("exit", code=code)

# --- Main ---

def main():
    raw = os.environ.get("AGENT_INPUT", "{}")
    input_data = json.loads(raw)

    emit_start()

    try:
        # [gör det unika här]
        result = {}
        emit_data(result)

    except Exception as e:
        emit_error(str(e))
        emit_exit(1)
        return

    emit_exit(0)

if __name__ == "__main__":
    main()
```

Event-ordningen är kontraktet: `start → data* → exit`.
Avvika aldrig från den — ramverket förväntar sig exakt detta.

---

## 3. Kontaktytan mot ramverket — exakt vad som gäller

Ramverket anropar scriptet. Scriptet behöver bara följa tre regler:

**Input** — kommer via miljövariabel, aldrig via argv:
```python
input_data = json.loads(os.environ.get("AGENT_INPUT", "{}"))
```
Argumentparsning, validering och defaultvärden hanteras av ramverket innan scriptet startar.

**Output** — events till stdout som JSON, en per rad:
```
{"event": "start",  "agent": "[id]"}
{"event": "data",   "agent": "[id]", ...payload}
{"event": "output", "agent": "[id]", "message": "..."}
{"event": "error",  "agent": "[id]", "message": "..."}
{"event": "exit",   "agent": "[id]", "code": 0}
```
Ordningen är låst: `start` först, `exit` sist. Skriv aldrig fri text till stdout — det bryter kontraktet.

**Handshake** — hanteras av runner innan scriptet körs. Scriptet deltar inte.
Om handshaken misslyckas körs scriptet aldrig.

Modulen implementerar aldrig: argument-parsning, audit-loggning, error-catch på toppnivå,
exit-kod-hantering. Det är ramverkets ansvar.

---

## 4. Om ramverket saknar något

Gör ändringen i projektet, inte i `coop/main`.
Flagga den som ett förslag till ramverksägaren via commit-meddelandet.
Ramverksägaren avgör om det blir prejudikat.
