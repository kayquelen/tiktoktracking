#!/bin/bash

echo "🚀 Deploy final da integração Stripe → TikTok"

# Fazer commit de todas as mudanças
git add .
git status
git commit -m "Deploy final: health check + webhook stripe completo"
git push origin main

echo "✅ Deploy enviado para EasyPanel!"
echo "🔄 Aguarde 1-2 minutos para redeploy automático"
echo ""
echo "🎯 URLs para testar após deploy:"
echo "   Health: https://track.bxsdur.easypanel.host/health"
echo "   Home: https://track.bxsdur.easypanel.host/"
echo "   Webhook: https://track.bxsdur.easypanel.host/webhook/stripe"
echo "   Pixels: https://track.bxsdur.easypanel.host/api/pixels"
