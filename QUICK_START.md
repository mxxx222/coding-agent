# Coding Agent - Nopea Aloitus

## 🚀 Käynnistä projektin 3 vaiheessa

### Vaihe 1: Asenna riippuvuudet

```bash
cd server
pip install -r requirements.txt
```

### Vaihe 2: Käynnistä serveri

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Vaihe 3: Avaa selaimessa

```
http://localhost:8000/api/docs
```

**Valmis! 🎉**

## 📚 Mitä löytyy?

### API Dokumentaatio (Swagger)
- **URL:** http://localhost:8000/api/docs
- **Testaa kaikkia endpointteja suoraan selaimessa**

### Interactive API (ReDoc)
- **URL:** http://localhost:8000/api/redoc
- **Kaunis dokumentaatio**

### Health Check
```bash
curl http://localhost:8000/api/health
```

## 🧪 Nopea API-testi

### Testaa Code Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze/code" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): return \"world\"",
    "language": "python",
    "context": "Simple greeting function"
  }'
```

### Testaa Integrations

```bash
curl http://localhost:8000/api/integrations/
```

## 🐳 Docker-käyttöönotto

Jos sinulla on Docker:

```bash
docker-compose up -d
```

## ⚠️ Tärkeitä huomioita

1. **Ei API-avainta?** Ei hätää! Projekti toimii mock-moodissa
2. **Tietokanta?** Ei pakollinen ensimmäiselle testille
3. **Redis?** Ei pakollinen ensimmäiselle testille

Kaikki toimii ilman niitä - mock-vastaukset tuottavat testattavissa olevat tulokset!

## 🎯 Seuraavat askeleet

1. ✅ Käynnistä serveri
2. ✅ Testaa API dokumentaatiossa
3. 📖 Lue lisää [PRODUCTION_README.md](PRODUCTION_README.md)
4. 🔧 Tutustu koodiin `server/` hakemistossa

## 📞 Ongelmia?

- Tarkista Python-versio: `python --version` (vähintään 3.9)
- Tarkista että kaikki riippuvuudet on asennettu
- Katso [SETUP.md](SETUP.md) yksityiskohtaiset ohjeet
- Katso [MITÄ_TEHTIIN.md](MITÄ_TEHTIIN.md) mitä tehtiin

---

**Nauti koodauksesta! 🚀**

