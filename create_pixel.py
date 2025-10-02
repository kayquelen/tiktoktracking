#!/usr/bin/env python3

import requests
import json

def create_pixel():
    """Criar pixel padrão prod-1"""
    
    url = "https://track.bxsdur.easypanel.host/api/pixels"
    
    pixel_data = {
        "manager_id": "prod-1",
        "pixel_id": "D38TGMRC77UB9GL65CL0",
        "access_token": "b8f9be6eb3e61b9d6cd68db14b4ec7afe16ecd14",
        "nome_pixel": "Pixel Produção Principal",
        "ativo": True
    }
    
    print("🎯 Criando pixel padrão...")
    print(f"URL: {url}")
    print(f"Dados: {json.dumps(pixel_data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=pixel_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Pixel criado com sucesso!")
        else:
            print("❌ Erro ao criar pixel")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def list_pixels():
    """Listar pixels existentes"""
    
    url = "https://track.bxsdur.easypanel.host/api/pixels"
    
    print("\n📋 Listando pixels existentes...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def check_logs():
    """Verificar logs do pixel"""
    
    url = "https://track.bxsdur.easypanel.host/api/pixels/prod-1/logs"
    
    print("\n📊 Verificando logs do pixel prod-1...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    print("🚀 Configuração do Pixel TikTok")
    print("=" * 40)
    
    # 1. Listar pixels atuais
    list_pixels()
    
    # 2. Criar pixel padrão
    create_pixel()
    
    # 3. Listar novamente para confirmar
    list_pixels()
    
    # 4. Verificar logs
    check_logs()
    
    print("\n✅ Configuração concluída!")
