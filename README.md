# 🛡️ CrashCatcher

**CrashCatcher** är en säkerhets- och övervakningsplattform byggd för att fånga upp appkrascher, analysera loggar och rapportera säkerhetsincidenter i realtid.  
Systemet är byggt med moderna tekniker: **FastAPI (backend)**, **React/Vite (frontend)**, **PostgreSQL (databas)** och en fristående **Watchdog-agent** för systemövervakning.

---

## 🚀 Funktioner
- 📊 **Dashboard (frontend)** – visa krascher & incidenter i realtid
- 🔐 **Säker backend (FastAPI)** – med API-nyckel och JWT-stöd
- 🗄️ **Databas (Postgres)** – sparar incidenter och loggar
- 🐕 **Watchdog** – övervakar CPU, minne, processer, nätverk och skickar incidentrapporter
- ⚡ **Docker Compose** – startar hela systemet med ett kommando
- 🔒 **Säkerhet** – CORS, API-nyckel, hemligheter i `.env`

---

## 📂 Projektstruktur

```
crashcatcher/
├── backend/             # All FastAPI-kod, models, schemas, main.py
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/            # All React/Vite-kod
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── watchdog/            # Python-scriptet för övervakning
│   ├── watchdog.py
│   └── Dockerfile
│
├── docker-compose.yml   # Dirigenten som startar alla containrar
├── .env.example         # Exempel på miljövariabler (utan hemligheter)
```

## 🛠️ Installation och uppstart

### Förutsättningar

- Docker och Docker Compose
- Git

### Snabb start

1. **Klona projektet**
   ```bash
   git clone <repository-url>
   cd app-root
   ```

2. **Starta alla tjänster**
   ```bash
   docker-compose up -d
   ```

3. **Öppna applikationen**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API-dokumentation: http://localhost:8000/docs

### Utvecklingsmiljö

För utveckling kan du köra tjänsterna separat:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

**Watchdog:**
```bash
cd watchdog
pip install -r requirements.txt
python watchdog.py
```

## 📊 Tjänster

### Backend API (Port 8000)

FastAPI-baserad backend som tillhandahåller:

- `/auth/login` - Användarautentisering
- `/auth/register` - Användarregistrering
- `/incidents/` - Incident CRUD-operationer
- `/health` - Hälsokontroll

### Frontend (Port 3000)

React-baserat webbgränssnitt med:

- **Dashboard** - Översikt över säkerhetsstatus
- **Incident List** - Lista och filtrera incidenter
- **Incident Detail** - Detaljerad vy och statusuppdatering
- **Autentisering** - Säker inloggning

### Watchdog

Python-baserad övervakingstjänst som kontrollerar:

- **Systemresurser** - CPU, minne, diskutrymme
- **Misstänkta processer** - Upptäcker säkerhetsverktyg
- **Nätverksanslutningar** - Övervakar portar och connections
- **Inloggningsförsök** - Analyserar auth.log
- **Portskanning** - Upptäcker misstänkt nätverkstrafik

### Databas (Port 5432)

PostgreSQL-databas som lagrar:

- Användarinformation
- Säkerhetsincidenter
- Systemloggar

## 🔧 Konfiguration

### Miljövariabler

**Backend:**
- `DATABASE_URL` - Databasanslutning
- `SECRET_KEY` - JWT-signeringsnyckel

**Frontend:**
- `REACT_APP_API_URL` - Backend API URL

**Watchdog:**
- `API_URL` - Backend API URL
- `CHECK_INTERVAL` - Kontrollintervall (sekunder)
- `MAX_CPU_USAGE` - CPU-tröskelvärde (%)
- `MAX_MEMORY_USAGE` - Minneströskelvärde (%)
- `SUSPICIOUS_PROCESSES` - Lista över misstänkta processer

## 🔐 Säkerhet

### Autentisering

Systemet använder JWT (JSON Web Tokens) för autentisering:

1. Användare loggar in med användarnamn/lösenord
2. Backend returnerar JWT-token
3. Token inkluderas i alla efterföljande API-anrop
4. Token valideras för varje skyddad endpoint

### Lösenordshantering

- Lösenord hashas med bcrypt
- Säkra lösenordsvalidering
- Token-baserad session management

## 📈 Övervakning och Logging

### Incident-typer

Systemet upptäcker och rapporterar följande typer av incidenter:

- `system_performance` - Prestandaproblem
- `system_storage` - Lagringsproblem
- `suspicious_process` - Misstänkta processer
- `network_connection` - Nätverksanslutningar
- `failed_login` - Misslyckade inloggningar
- `port_scan` - Portskanning

### Allvarlighetsgrader

- `low` - Låg risk
- `medium` - Medel risk
- `high` - Hög risk
- `critical` - Kritisk risk

## 🚀 Produktion

### Säkerhetskonfiguration

För produktionsmiljö, uppdatera följande:

1. **Ändra standardlösenord**
   ```yaml
   # docker-compose.yml
   POSTGRES_PASSWORD: ditt-säkra-lösenord
   SECRET_KEY: din-säkra-signeringsnyckel
   ```

2. **Konfigurera HTTPS**
   - Lägg till SSL-certifikat i `nginx/ssl/`
   - Uppdatera nginx-konfiguration

3. **Nätverk säkerhet**
   - Konfigurera firewall
   - Begränsa åtkomst till databas
   - Använd privata nätverk

### Backup

Regelbunden backup av PostgreSQL-data:

```bash
docker-compose exec db pg_dump -U postgres security_monitor > backup.sql
```

## 🐛 Felsökning

### Vanliga problem

**Backend startar inte:**
```bash
docker-compose logs backend
```

**Frontend kan inte nå backend:**
- Kontrollera att REACT_APP_API_URL är korrekt
- Verifiera att backend körs på port 8000

**Databas anslutningsproblem:**
```bash
docker-compose exec db psql -U postgres -d security_monitor
```

### Health Checks

Kontrollera tjänsternas status:

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Databas
docker-compose exec db pg_isready -U postgres
```

## 🤝 Bidrag

1. Fork projektet
2. Skapa en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dina ändringar (`git commit -m 'Add some AmazingFeature'`)
4. Push till branchen (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request

## 📄 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## 📞 Support

För support eller frågor:

- Skapa en issue på GitHub
- Kontakta utvecklingsteamet

---

**Security Monitor** - Håll koll på din systemsäkerhet 🛡️
