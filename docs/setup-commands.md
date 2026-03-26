# Setup-Befehle: NVIDIA AI Blueprint × Shopware 6

Alle Befehle die beim Setup des Projekts verwendet wurden, chronologisch mit Erklärung.

---

## 1. System-Voraussetzungen prüfen

```bash
# Docker Version prüfen (mind. 20.10+)
docker --version

# Docker Compose Plugin prüfen
docker compose version

# RAM prüfen (mind. 8GB frei empfohlen)
free -h

# Festplattenspeicher prüfen
df -h /
```

## 2. Docker Context reparieren

```bash
# Problem: Docker suchte den Desktop-Socket statt den Standard-Daemon
# Welche Contexts sind konfiguriert? (* = aktiv)
docker context ls

# Auf Standard-Docker-Daemon wechseln (statt Docker Desktop)
docker context use default
```

**Warum?** Wenn Docker Desktop mal installiert war, bleibt der Context auf `desktop-linux` stehen.
Der Standard-Daemon läuft unter `/var/run/docker.sock`.

## 3. Docker Credential Helper reparieren

```bash
# Problem: "docker-credential-desktop" not found
# Die Datei ~/.docker/config.json enthielt "credsStore": "desktop"
# Fix: credsStore leeren (Docker Desktop ist nicht mehr installiert)
```

**Datei:** `~/.docker/config.json`
```json
{
  "credsStore": ""   // war "desktop" → leer setzen
}
```

**Warum?** Docker versuchte Credentials über Docker Desktop zu laden, das nicht installiert ist.

## 4. Repository klonen

```bash
cd /home/m3mo/Projekte/webseiten/memotech/

# NVIDIA Blueprint als Basis klonen
git clone https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant.git nvidia-shopware-assistant

cd nvidia-shopware-assistant
```

## 5. API Keys konfigurieren

```bash
# .env aus Template erstellen
cp .env.example .env
```

**WICHTIG: Zwei verschiedene API-Key-Systeme!**

| Key | Quelle | Zweck |
|-----|--------|-------|
| NGC Key | ngc.nvidia.com → API Keys | Container Registry, NGC Catalog |
| Build Key | build.nvidia.com → Settings → API Keys | LLM Inference (integrate.api.nvidia.com) |

**Datei:** `.env`
```bash
# NGC Key (ngc.nvidia.com) — für Container Registry
NGC_API_KEY=nvapi-XXXX

# Build Key (build.nvidia.com) — für LLM Cloud Endpoints
# DIESER Key wird für die KI-Antworten gebraucht!
LLM_API_KEY=nvapi-YYYY
EMBED_API_KEY=nvapi-YYYY
RAIL_API_KEY=nvapi-YYYY

# Cloud-Modus aktivieren (kein GPU nötig)
CONFIG_OVERRIDE=config-build.yaml
```

## 6. Alle Container starten

```bash
# Alle Services im Cloud-Modus bauen und starten
# --build: Images neu bauen
# -d: Detached (im Hintergrund)
docker compose up -d --build
```

**Was passiert?** Docker baut 5 Images (chain-server, catalog-retriever, memory-retriever, guardrails, frontend) und startet 10 Container:

| Container | Port | Funktion |
|-----------|------|----------|
| nginx-proxy | 3000 | Eingangs-Proxy, leitet UI + API |
| shopping-frontend | - | React UI (nur intern via nginx) |
| chain-server | 8009 | LangGraph Agent-Orchestrierung |
| catalog-retriever | 8010 | Produkt-Suche + Embeddings |
| memory-retriever | 8011 | User-Kontext + Warenkorb (SQLite) |
| rails | 8012 | NeMo Guardrails (Content Safety) |
| milvus-standalone | 19530 | Vektor-Datenbank für Similarity Search |
| milvus-etcd | 2379 | Key-Value Store für Milvus |
| milvus-minio | 9000 | Object Storage für Milvus |
| shopware | 8888 | Shopware 6 Demo-Shop (dockware) |

## 7. Shopware Sales Channel Domain fixen

```bash
# Problem: Shopware erwartet "http://localhost" (Port 80), aber wir mappen auf Port 8888
# → SalesChannelMappingException: "Unable to find a matching sales channel"

# Domain in der Datenbank aktualisieren
# -h 127.0.0.1: TCP-Verbindung statt Unix-Socket (Socket hat Permission-Problem)
docker exec shopware bash -c "mysql -h 127.0.0.1 -u root -proot shopware \
  -e \"UPDATE sales_channel_domain SET url='http://localhost:8888' WHERE url='http://localhost';\""

# Shopware Cache leeren (nötig nach DB-Änderung)
docker exec shopware bash -c "bin/console cache:clear"
```

**Warum?** Dockware konfiguriert die Domain auf `http://localhost` (Port 80).
Da wir Port 8888 nach aussen mappen, muss die Domain angepasst werden.

## 8. Health Checks

```bash
# Alle Services prüfen — alle sollten HTTP 200 zurückgeben
curl -sS -o /dev/null -w "%{http_code}" http://localhost:3000      # UI
curl -sS -o /dev/null -w "%{http_code}" http://localhost:8009/health # Chain Server
curl -sS -o /dev/null -w "%{http_code}" http://localhost:8010/health # Catalog Retriever
curl -sS -o /dev/null -w "%{http_code}" http://localhost:8011/health # Memory Retriever
curl -sS -o /dev/null -w "%{http_code}" http://localhost:8888/       # Shopware
```

## 9. LLM API Key testen

```bash
# API Key direkt gegen NVIDIA Endpoint testen (ohne Docker)
curl -sS https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer nvapi-DEIN_BUILD_KEY" \
  -d '{
    "model": "meta/llama-3.1-70b-instruct",
    "messages": [{"role":"user","content":"Hello"}],
    "max_tokens": 50
  }'
```

**Erwartete Antwort:** JSON mit `choices[0].message.content`
**403 Forbidden?** → Falscher Key (NGC statt Build) oder Key nicht aktiviert

## 10. Container mit neuen Env-Vars neu erstellen

```bash
# WICHTIG: "docker compose restart" lädt KEINE neuen .env-Werte!
# "docker compose up -d" erkennt .env-Änderungen und recreated betroffene Container
docker compose up -d chain-server rails catalog-retriever
```

**Warum nicht `restart`?** Docker Compose cached Umgebungsvariablen beim ersten `up`.
Ein `restart` startet den Prozess im Container neu, aber mit den alten Env-Vars.
Nur `up -d` liest die `.env` neu und erstellt Container bei Bedarf neu.

## 11. Shopping Assistant testen

```bash
# Query direkt an den Chain Server senden (SSE Stream)
curl -sS http://localhost:8009/query/stream \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me some dresses","user_id":12345}'
```

**Erwartete Antwort:** Server-Sent Events mit `type: images` und `type: content`

## 12. Logs prüfen

```bash
# Chain Server Logs (letzte 20 Zeilen)
docker logs chain-server --tail 20

# Shopware Logs
docker logs shopware --tail 20

# Alle Container Status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 13. Container stoppen / aufräumen

```bash
# Alle Container stoppen (Daten bleiben erhalten)
docker compose stop

# Alle Container stoppen UND entfernen (Volumes bleiben)
docker compose down

# Alles entfernen inkl. Volumes (ACHTUNG: löscht Milvus-Daten!)
docker compose down -v
```

---

## Shopware Store API testen

```bash
# Shopware Store API Access Key finden
docker exec shopware bash -c "bin/console sales-channel:list --output=json" | python3 -m json.tool

# Produkte abrufen (Default dockware Access Key)
curl -sS http://localhost:8888/store-api/product \
  -X POST \
  -H "Content-Type: application/json" \
  -H "sw-access-key: SWSCBHFSNTVMAWNZDNFKSHLAYW" \
  -d '{"limit": 5}'
```

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| `docker-credential-desktop not found` | `~/.docker/config.json` → `"credsStore": ""` |
| `dial unix .../docker.sock: no such file` | `docker context use default` |
| `403 Forbidden` bei LLM API | Build-Key statt NGC-Key verwenden |
| `SalesChannelMappingException` | Domain in DB auf `localhost:8888` updaten |
| `restart` lädt keine neuen Env-Vars | `docker compose up -d` statt `restart` |
| Container startet nicht | `docker logs <name> --tail 50` prüfen |
