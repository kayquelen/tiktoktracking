#!/bin/bash

# Script de instalação para Automação Stripe → TikTok
# Compatível com Ubuntu 20.04+ e Debian 11+

set -e

echo "🚀 Iniciando instalação da Automação Stripe → TikTok..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script não deve ser executado como root"
   exit 1
fi

# Atualizar sistema
print_status "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
print_status "Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib curl

# Criar usuário para aplicação (se não existir)
if ! id "tiktok" &>/dev/null; then
    print_status "Criando usuário tiktok..."
    sudo adduser --disabled-password --gecos "" tiktok
    sudo usermod -aG sudo tiktok
fi

# Configurar PostgreSQL
print_status "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE tiktok_automation;" 2>/dev/null || print_warning "Database já existe"
sudo -u postgres psql -c "CREATE USER tiktok_user WITH PASSWORD 'tiktok_password_123';" 2>/dev/null || print_warning "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tiktok_automation TO tiktok_user;" 2>/dev/null || true

# Criar diretório da aplicação
print_status "Configurando diretório da aplicação..."
sudo mkdir -p /opt/stripe-tiktok-automation
sudo chown tiktok:tiktok /opt/stripe-tiktok-automation

# Copiar arquivos (assumindo que estamos no diretório do projeto)
print_status "Copiando arquivos da aplicação..."
sudo cp -r . /opt/stripe-tiktok-automation/
sudo chown -R tiktok:tiktok /opt/stripe-tiktok-automation

# Configurar ambiente virtual Python
print_status "Configurando ambiente virtual Python..."
sudo -u tiktok python3 -m venv /opt/stripe-tiktok-automation/venv
sudo -u tiktok /opt/stripe-tiktok-automation/venv/bin/pip install --upgrade pip
sudo -u tiktok /opt/stripe-tiktok-automation/venv/bin/pip install -r /opt/stripe-tiktok-automation/requirements.txt

# Criar arquivo .env
print_status "Criando arquivo de configuração..."
sudo -u tiktok cp /opt/stripe-tiktok-automation/.env.example /opt/stripe-tiktok-automation/.env

# Configurar systemd service
print_status "Configurando serviço systemd..."
sudo tee /etc/systemd/system/tiktok-automation.service > /dev/null <<EOF
[Unit]
Description=TikTok Automation Flask App
After=network.target postgresql.service

[Service]
Type=simple
User=tiktok
Group=tiktok
WorkingDirectory=/opt/stripe-tiktok-automation
Environment=PATH=/opt/stripe-tiktok-automation/venv/bin
ExecStart=/opt/stripe-tiktok-automation/venv/bin/python src/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
print_status "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/tiktok-automation > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for webhooks
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Ativar site no Nginx
sudo ln -sf /etc/nginx/sites-available/tiktok-automation /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
sudo nginx -t

# Inicializar banco de dados
print_status "Inicializando banco de dados..."
cd /opt/stripe-tiktok-automation
sudo -u tiktok /opt/stripe-tiktok-automation/venv/bin/python -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Banco de dados inicializado com sucesso!')
"

# Habilitar e iniciar serviços
print_status "Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable tiktok-automation
sudo systemctl start tiktok-automation
sudo systemctl restart nginx

# Verificar status dos serviços
sleep 3
if sudo systemctl is-active --quiet tiktok-automation; then
    print_success "Serviço tiktok-automation está rodando"
else
    print_error "Falha ao iniciar serviço tiktok-automation"
    sudo systemctl status tiktok-automation
fi

if sudo systemctl is-active --quiet nginx; then
    print_success "Nginx está rodando"
else
    print_error "Falha ao iniciar Nginx"
    sudo systemctl status nginx
fi

# Mostrar informações finais
print_success "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Informações importantes:"
echo "  • Aplicação rodando em: http://$(hostname -I | awk '{print $1}'):80"
echo "  • Logs da aplicação: sudo journalctl -u tiktok-automation -f"
echo "  • Configuração: /opt/stripe-tiktok-automation/.env"
echo "  • Reiniciar aplicação: sudo systemctl restart tiktok-automation"
echo ""
echo "🔧 Próximos passos:"
echo "  1. Edite /opt/stripe-tiktok-automation/.env com suas configurações"
echo "  2. Configure SSL com: sudo certbot --nginx -d seudominio.com"
echo "  3. Acesse a interface web para adicionar seus pixels"
echo ""
print_warning "IMPORTANTE: Altere a senha do PostgreSQL em produção!"
echo "  sudo -u postgres psql -c \"ALTER USER tiktok_user PASSWORD 'nova_senha_segura';\""

