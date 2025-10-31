# Asenna ja Käynnistä Coding Agent

## 🔧 Asennus

### 1. Siirry server-hakemistoon

```bash
cd server
```

### 2. Asenna riippuvuudet

```bash
# Windows/macOS/Linux
pip3 install -r requirements.txt

# Tai jos sinulla on virtuaaliympäristö
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# tai: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Luo .env-tiedosto (valinnainen)

```bash
cp env.example .env
```

**Huom:** Tämä ei ole pakollista ensimmäiselle testille! Mock-moodi toimii ilman API-avaimia.

## ▶️ Käynnistäminen

### Yksinkertaisin tapa

```bash
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Vaihtoehtoiset portit

```bash
# Portti 3000
python3 -m uvicorn api.main:app --reload --port 3000

# Portti 5000
python3 -m uvicorn api.main:app --reload --port 5000
```

## 🌐 Avaa selaimessa

Kun näet viestin:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Avaa selain ja mene osoitteeseen:

### 📖 API Dokumentaatio (Swagger)
```
http://localhost:8000/api/docs
```

### 📘 Toinen API Näkymä (ReDoc)
```
http://localhost:8000/api/redoc
```

### ✅ Health Check
```
http://localhost:8000/api/health
```

## 🧪 Nopea testi selaimessa

1. Avaa: **http://localhost:8000/api/docs**
2. Etsi: **POST /api/analyze/code**
3. Klikkaa: **"Try it out"**
4. Syötä testidata:
```json
{
  "code": "def hello(): return 'world'",
  "language": "python"
}
```
5. Klikkaa: **"Execute"**
6. Katso vastaus!

## 🐳 Vaihtoehtoisesti: Käytä Dockeria

Jos sinulla on Docker asennettuna:

```bash
cd ..  # Takaisin projektin juureen
docker-compose up -d
```

## ⚠️ Yleisiä ongelmia

### "ModuleNotFoundError: No module named 'fastapi'"

**Ratkaisu:**
```bash
pip3 install fastapi uvicorn
# tai
pip install -r requirements.txt
```

### "Address already in use"

**Ratkaisu:** Käytä eri porttia
```bash
python3 -m uvicorn api.main:app --reload --port 8001
```

### Import-virheet

**Ratkaisu:** Varmista että olet server-hakemistossa
```bash
pwd  # Pitäisi näyttää: .../coding-agent/server
```

## ✅ Onnistunut käynnistys?

Jos näet alla olevan, kaikki toimii:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
Coding Agent API started successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🎯 Mitä seuraavaksi?

1. ✅ Tutustu API-dokumentaatioon: http://localhost:8000/api/docs
2. 📖 Lue [PRODUCTION_README.md](PRODUCTION_README.md)
3. 🧪 Testaa eri endpointteja
4. 🔧 Tutustu koodiin
5. 🚀 Deployaa tuotantoon!

---

**Nauti kokeilusta! 🎉**

