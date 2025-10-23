#!/bin/bash

# 🚀 Coding Agent Web UI - Render Deploy Script
# This script helps you deploy to Render.com

echo "🚀 Coding Agent Web UI - Render Deploy Helper"
echo "=============================================="

echo ""
echo "📋 Seuraavat vaiheet:"
echo ""

echo "1. 🌐 Mene Renderiin:"
echo "   https://render.com"
echo ""

echo "2. 🔐 Kirjaudu sisään:"
echo "   - Klikkaa 'Get Started' tai 'Sign In'"
echo "   - Käytä GitHub-tiliäsi"
echo ""

echo "3. 🆕 Luo Web Service:"
echo "   - Klikkaa 'New +' → 'Web Service'"
echo "   - Yhdistä repository: mxxx222/coding-agent"
echo ""

echo "4. ⚙️  Konfiguroi palvelu:"
echo "   Name: coding-agent-web"
echo "   Environment: Node"
echo "   Build Command: npm install && npm run build"
echo "   Start Command: npm start"
echo ""

echo "5. 🔧 Ympäristömuuttujat:"
echo "   NODE_ENV=production"
echo "   NEXT_PUBLIC_API_URL=https://coding-agent-api.onrender.com"
echo "   NEXT_PUBLIC_APP_NAME=Coding Agent"
echo "   NEXT_PUBLIC_APP_VERSION=1.0.0"
echo ""

echo "6. 🚀 Deploy:"
echo "   - Klikkaa 'Create Web Service'"
echo "   - Odota 2-5 minuuttia"
echo "   - Sait URL:n: https://coding-agent-web.onrender.com"
echo ""

echo "📊 Vaihtoehtoiset deploy-tavat:"
echo ""
echo "🎯 Render Blueprint (helppo):"
echo "   - Klikkaa 'New +' → 'Blueprint'"
echo "   - Valitse repository: mxxx222/coding-agent"
echo "   - Render lukee automaattisesti render.yaml -tiedoston"
echo ""

echo "🐳 Docker Deploy:"
echo "   - Valitse 'Docker' environment"
echo "   - Render käyttää automaattisesti Dockerfile -tiedostoa"
echo ""

echo "📚 Täydelliset ohjeet:"
echo "   https://github.com/mxxx222/coding-agent/blob/main/DEPLOY_RENDER.md"
echo ""

echo "🔗 Linkit:"
echo "   Repository: https://github.com/mxxx222/coding-agent"
echo "   Render: https://dashboard.render.com"
echo ""

echo "✅ Valmis deployaamaan!"
echo "   Web UI on täysin valmis Renderiin!"

