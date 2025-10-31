# Coding Agent - Setup Guide

Tämä ohje auttaa sinua viemään Coding Agent -projektin tuotantovalmiksi.

## Vaatimukset

- Python 3.9+
- Node.js 18+
- Docker (valinnainen, suositeltu)
- PostgreSQL (tai Docker Compose)
- Redis (tai Docker Compose)

## Nopea aloitus (Development)

### 1. Kloonaa repositorio

```bash
git clone https://github.com/your-username/coding-agent.git
cd coding-agent
```

### 2. Asenna backend-riippuvuudet

```bash
cd server
pip install -r requirements.txt
```

### 3. Määritä ympäristömuuttujat

Kopioi `.env.example` tiedosto ja aseta omat arvot:

```bash
cp .env.example .env
nano .env  # tai käytä omaa editoria
```

**Tärkeimmät ympäristömuuttujat:**
- `OPENAI_API_KEY` - Oma OpenAI API-avain (pakollinen tuotannossa)
- `DATABASE_URL` - PostgreSQL-tietokannan osoite
- `REDIS_URL` - Redis-palvelimen osoite
- `JWT_SECRET` - Salainen avain JWT-tokeneille

### 4. Käynnistä Docker Compose (suositeltu)

```bash
cd ..
docker-compose up -d
```

Tämä käynnistää:
- PostgreSQL tietokannan
- Redis välimuistin
- Vapaaehtoiset palvelut

### 5. Käynnistä backend-server

```bash
cd server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Pitäisi nähdä viesti: "Coding Agent API started successfully!"

API dokumentaatio löytyy: http://localhost:8000/api/docs

## Docker käyttöönotto

### Käännä Docker-kuva

```bash
docker build -f server/Dockerfile -t coding-agent:latest .
```

### Käynnistä kontteinereissa

```bash
docker-compose up -d
```

## Tuotantoon vieminen

### Vaihe 1: Tietokannan migraatio

```bash
cd database
python -m alembic upgrade head
```

### Vaihe 2: Määritä tuotantoympäristömuuttujat

Luo `.env.production` tiedosto tuotantoon sopivilla arvoilla:

```bash
ENVIRONMENT=production
DEBUG=false
OPENAI_API_KEY=your_production_key
DATABASE_URL=your_production_database_url
JWT_SECRET=your_secure_jwt_secret
```

### Vaihe 3: Käynnistä tuotantokuva

```bash
docker run -d \
  --name coding-agent \
  --env-file .env.production \
  -p 8000:8000 \
  coding-agent:latest
```

## Tarkista toimivuus

### Health check

```bash
curl http://localhost:8000/api/health
```

Vastauksen pitäisi olla:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "vector_store": "connected",
    "llm": "connected"
  }
}
```

### Testaa API

```bash
curl -X POST http://localhost:8000/api/analyze/code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "code": "def hello(): return \"world\"",
    "language": "python"
  }'
```

## Ongelmatilanteet

### Tietokanta ei yhdistä

1. Tarkista `DATABASE_URL` ympäristömuuttujassa
2. Varmista että PostgreSQL pyörii
3. Tarkista että käyttäjällä on oikeudet tietokantaan

### OpenAI API ei toimi

1. Tarkista että `OPENAI_API_KEY` on asetettu
2. Varmista että API-avain on voimassa
3. Tarkista kuittaukset OpenAI-tililtäsi

### Redis ei toimi

1. Tarkista `REDIS_URL` ympäristömuuttujassa
2. Varmista että Redis-palvelin pyörii
3. Lataa ainoastaan ilman Redis-cachea

## Seuraavat vaiheet

1. **Luo GitHub Actions CI/CD** - Katso `.github/workflows/` hakemisto
2. **Aseta monitoring** - Integroi Sentry tai vastaava
3. **Konfiguroi CDN** - Käytä Cloudflare tai vastaavaa
4. **Aseta backup** - Automaattiset tietokannatietokanta varmuuskopiot
5. **Dokumentoi API** - Täydennä API.md dokumentaatio

## Lisätietoja

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Recipes](docs/RECIPES.md)

## Tuki

Jos sinulla on ongelmia:
1. Tarkista [tunnettu ongelmat](docs/TROUBLESHOOTING.md)
2. Luo GitHub Issue
3. Ota yhteyttä kehittäjiin

