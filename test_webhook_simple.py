#!/usr/bin/env python3

import requests
import json

def test_webhook():
    """Testar webhook Stripe com POST"""
    
    url = "https://track.bxsdur.easypanel.host/webhook/stripe"
    
    print("🧪 Testando webhook Stripe com POST")
    print(f"🎯 URL: {url}")
    print()
    
    # Teste 1: POST simples
    print("📡 Teste 1: POST básico...")
    try:
        response = requests.post(url, 
            json={"test": "connectivity"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print()
    
    # Teste 2: POST com evento Stripe
    print("📡 Teste 2: Evento Stripe simulado...")
    
    stripe_event = {
        "id": "evt_test_python",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_python",
                "amount_total": 1500,
                "currency": "brl",
                "customer_details": {
                    "email": "python@teste.com",
                    "name": "TESTE PYTHON"
                },
                "payment_intent": "pi_test_python",
                "success_url": "https://teste.com/success",
                "metadata": {
                    "utm_term": "prod-1"
                }
            }
        }
    }
    
    try:
        response = requests.post(url,
            json=stripe_event,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "t=1234567890,v1=fake_signature"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print()
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    test_webhook()
