# coop · project-init

## Vad
Ett Python-ramverk som är en defensiv perimeter för AI-moduler — ramverket hanterar allt generiskt så modulen bara behöver göra det unika.

## Status
branch:   main (stabil kärna) · feature/sweden-api-search (live pipeline, validerad)
nuläge:   Event-kontrakt, manifest, runner, BaseHandler, BaseAgent, Registry är klara.
          Sweden-pipeline (fetch → normalize → score → search) är validerad mot dataportal.se.
pending:
  - Kontraktsbrott: input-validering stubbad, timeout ignoreras, stderr droppas, constraints ej enforced
  - Kompositionslager: fan-out/fan-in, typed handoff — ej byggt, se-search gör manuell subprocess-chaining
  - Publisher-namnupplösning: org-ID URIs behöver Bolagsverket-integration
  - ApiHandler: stub, behöver FastAPI

förslag från direktoru-analys (ej implementerade — kan göras oberoende):
  - sessions/latest.md-mönster: coop saknar en alltid-aktuell nulägesfil per projekt.
    direktoru löser detta med sessions/latest.md — en session skriver dit innan den stängs.
    Förslag: coop definierar ett standardformat för project-status.md som varje projekt äger.
  - Beteendemässiga constraints: manifest.constraints täcker timeout/network/admin men inte
    "fråga ägaren innan du kör X". direktoru har en explicit förbudslist i AGENT.md.
    Förslag: manifest får ett valfritt "guardrails"-fält med named forbidden operations,
    t.ex. guardrails: ["no_delete", "confirm_before_write"] — enforced av runner.
  - Generaliseringsförslag från direktoru (prejudikat-kandidater — Gustaf avgör):
    · preflight: direktoru kör miljö- och beroendekoll innan varje session.
      Generaliserat: coop runner kör en preflight-hook innan worker startar —
      kontrollerar att beroenden finns, miljö stämmer, constraints kan enforças.
      Gäller alla projekt, inte bara direktoru.
    · dedup: hash-baserad duplikatdetektering mot scannad metadata.
      Generaliserat: en coop-worker "file-dedup" som tar metadata-ström och
      returnerar duplikatrapport. Inget projektspecifikt — återanvändbar i
      valfritt projekt som hanterar filer.
    · file-classifier: ext → kategori-mappning (Documents/Code/Images/etc).
      Generaliserat: en coop-worker "file-classifier" med konfigurerbar
      kategori-tabell. direktoru hårdkodar den — ramverket kan göra den
      injicerbar via manifest input.
    · route-data: benchmarkar hastigheter och planerar optimal datamigrering.
      Generaliserat: ett routing-koncept där ramverket känner till workers
      kapabilitet och väljer optimal exekveringsväg. Kräver kompositionslagret.

  - Blob-konceptet (idé, ej förslag): direktoru's blob.sh är projektspecifik — kartlägger en
    diskflotta. Men konceptet "varje nod bär en fullständig bild av systemet" kan vara
    ramverksmaterial om det generaliseras. Tänkbar variant: RAID-liknande redundans där
    varje worker eller nod känner till hela systemets topologi. Gustaf avgör om det är
    ett prejudikat värt att formalisera.

## Ingångspunkter
src/coop/runner.py        · laddar manifest, validerar handshake, exekverar worker
src/coop/sdk/agent.py     · BaseAgent — Python-alternativ till script-workers
src/coop/sdk/handler.py   · BaseHandler — livscykelkrokar för event-stream
docs/contracts/           · manifest- och handshake-standard
docs/director/            · session-log, skills-inventory
examples/sweden/          · aktiv pipeline med fyra workers och contracts
