#!/bin/bash

echo "🧪 Testando webhook Stripe com POST"

# Teste 1: POST simples para verificar se rota existe
echo "📡 Teste 1: POST básico..."
curl -X POST https://track.bxsdur.easypanel.host/webhook/stripe \
  -H "Content-Type: application/json" \
  --data '{"test": "connectivity"}' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "📡 Teste 2: POST com evento Stripe simulado..."

# Teste 2: POST com evento Stripe simulado
curl -X POST https://track.bxsdur.easypanel.host/webhook/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1234567890,v1=fake_signature" \
  --data '{
    "id": "evt_test_webhook",
    "type": "checkout.session.completed",
    "data": {
      "object": {
        "id": "cs_test_webhook",
        "amount_total": 1000,
        "currency": "brl",
        "customer_details": {
          "email": "teste@webhook.com",
          "name": "TESTE WEBHOOK"
        },
        "payment_intent": "pi_test_webhook",
        "success_url": "https://teste.com/success",
        "metadata": {
          "utm_term": "prod-1"
        }
      }
    }
  }' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "✅ Testes concluídos!"
