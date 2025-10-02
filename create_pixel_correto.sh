#!/bin/bash

echo "🎯 Criando pixel com campos corretos..."

curl -X POST https://track.bxsdur.easypanel.host/api/pixels \
  -H "Content-Type: application/json" \
  --data '{
    "id_gestor": "prod-1",
    "pixel_id": "D38TGMRC77UB9GL65CL0",
    "access_token": "b8f9be6eb3e61b9d6cd68db14b4ec7afe16ecd14",
    "nome_pixel": "Pixel Produção Principal",
    "ativo": true
  }' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "📋 Verificando se foi criado..."

curl https://track.bxsdur.easypanel.host/api/pixels \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "📊 Testando logs..."

curl https://track.bxsdur.easypanel.host/api/pixels/prod-1/logs \
  -w "\nStatus: %{http_code}\n"
