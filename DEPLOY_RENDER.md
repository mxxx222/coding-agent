# 🚀 Deploy Coding Agent Web UI to Render

## Vaihe vaiheelta -ohje Renderiin deployaamiseen

### 1. Kirjaudu Renderiin
- Mene https://render.com
- Klikkaa "Get Started" tai "Sign In"
- Kirjaudu sisään GitHub-tililläsi

### 2. Luo uusi Web Service
- Dashboardissa klikkaa "New +" → "Web Service"
- Yhdistä GitHub repository: `mxxx222/coding-agent`

### 3. Konfiguroi palvelu

#### **Perusasetukset:**
```
Name: coding-agent-web
Environment: Node
Region: Oregon (US West)
Branch: main
```

#### **Build & Deploy:**
```
Build Command: npm install && npm run build
Start Command: npm start
```

#### **Ympäristömuuttujat:**
```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://coding-agent-api.onrender.com
NEXT_PUBLIC_APP_NAME=Coding Agent
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 4. Deploy
- Klikkaa "Create Web Service"
- Odota buildin valmistumista (2-5 min)
- Sait URL:n: `https://coding-agent-web.onrender.com`

## 🎯 Vaihtoehtoinen tapa (Render Blueprint)

### 1. Käytä render.yaml -tiedostoa
Repository sisältää `render.yaml` -konfiguraation:

```yaml
services:
  - type: web
    name: coding-agent-web
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_API_URL
        value: https://coding-agent-api.onrender.com
      - key: NEXT_PUBLIC_APP_NAME
        value: Coding Agent
      - key: NEXT_PUBLIC_APP_VERSION
        value: 1.0.0
    healthCheckPath: /
    plan: starter
```

### 2. Deploy Blueprint:lla
- Dashboardissa klikkaa "New +" → "Blueprint"
- Valitse repository: `mxxx222/coding-agent`
- Render lukee automaattisesti `render.yaml` -tiedoston

## 🔧 Docker Deploy (vaihtoehto)

### 1. Käytä Dockerfile:ta
Repository sisältää `Dockerfile`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### 2. Deploy Docker:lla
- Valitse "Docker" environment
- Render käyttää automaattisesti `Dockerfile` -tiedostoa

## 📊 Mitä saat:

- **Live Web UI**: https://coding-agent-web.onrender.com
- **Automaattinen deploy**: GitHub push → Render deploy
- **HTTPS-tuki**: Automaattinen SSL-sertifikaatti
- **Skalautuvuus**: Automaattinen skaalaus
- **Monitoring**: Automaattinen seuranta

## 🔗 Linkit:

- **Repository**: https://github.com/mxxx222/coding-agent
- **Render Dashboard**: https://dashboard.render.com
- **Web UI**: https://coding-agent-web.onrender.com (kun deployattu)

## 🚨 Tärkeää:

1. **API-avain**: Aseta `OPENAI_API_KEY` ympäristömuuttujaksi Renderissä
2. **Tietokanta**: Jos tarvitset, luo Render Postgres
3. **Domain**: Voit lisätä custom domainin myöhemmin

## ✅ Seuraavat vaiheet:

1. Deployaa Web UI Renderiin
2. Testaa toimivuus
3. Aseta custom domain (valinnainen)
4. Konfiguroi CI/CD (valinnainen)

**Coding Agent Web UI on nyt valmis deployaamaan Renderiin!** 🎉

