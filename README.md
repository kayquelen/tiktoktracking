# 🚀 Automação Stripe → TikTok Ads

Automatiza o envio de eventos de conversão do Stripe para a API de Eventos do TikTok.

## ✨ Funcionalidades
- 🎯 Gestão de Pixels: Adicione, edite e remova pixels do TikTok
- 🔄 Webhooks Automáticos: Receba eventos do Stripe automaticamente
- 📊 Interface Web: Dashboard moderno para gerenciar tudo
- 🔒 Segurança: Validação de assinaturas e chaves de segurança
- 📈 Monitoramento: Logs detalhados de todos os eventos

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8+
- PostgreSQL
- Conta Stripe
- Pixel TikTok Ads

### 1) Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/stripe-tiktok-automation.git
cd stripe-tiktok-automation
```

### 2) Instale dependências
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure o banco de dados
```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE tiktok_automation;
CREATE USER tiktok_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE tiktok_automation TO tiktok_user;
```

### 4) Configure variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

Exemplo de variáveis (.env):
```env
# App
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=5000
SECRET_KEY=troque-esta-chave

# Database
DATABASE_URL=postgresql+psycopg2://tiktok_user:sua_senha@localhost:5432/tiktok_automation

# Stripe
STRIPE_SECRET_KEY=sk_live_ou_sk_test_sua_chave
STRIPE_WEBHOOK_SECRET=whsec_sua_chave

# TikTok
TIKTOK_ACCESS_TOKEN=seu_access_token
TIKTOK_PIXEL_ID=seu_pixel_id
TIKTOK_TEST_EVENT_MODE=false
```

### 5) Execute a aplicação
```bash
python src/main.py
```

---

## 🌐 Acesso
- Interface Web: http://localhost:5000
- API: http://localhost:5000/api/
- Webhook Stripe: http://localhost:5000/webhook/stripe

---

## 📋 Como Usar

### 1) Adicionar Pixel TikTok
1. Acesse a interface web
2. Preencha o formulário "Adicionar Pixel"
3. Guarde a chave de segurança gerada

### 2) Configurar Webhook no Stripe
1. Vá para Dashboard Stripe → Webhooks
2. Adicione endpoint: `https://seudominio.com/webhook/stripe`
3. Selecione eventos: `payment_intent.succeeded`, `checkout.session.completed`

### 3) Configurar Links de Checkout
Adicione `utm_term` com o ID do gestor:
```text
https://checkout.stripe.com/pay/cs_...?utm_term=SEU_ID_GESTOR
```

---

## 🔧 Configuração de Produção

### Nginx
```nginx
server {
  listen 80;
  server_name seudominio.com;

  location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### SSL com Let's Encrypt
```bash
sudo certbot --nginx -d seudominio.com
```

### Systemd Service
```bash
sudo cp deploy/tiktok-automation.service /etc/systemd/system/
sudo systemctl enable tiktok-automation
sudo systemctl start tiktok-automation
```

---

## 📊 API Endpoints
- GET `/api/pixels` - Listar pixels
- POST `/api/pixels` - Criar pixel
- PUT `/api/pixels/<id>` - Atualizar pixel
- DELETE `/api/pixels/<id>` - Remover pixel
- GET `/api/pixels/<id>/logs` - Ver logs
- POST `/webhook/stripe` - Webhook do Stripe
- POST `/webhook/stripe/test` - Testar webhook

Estrutura de exemplo (POST `/api/pixels`):
```json
{
  "name": "Meu Pixel",
  "pixel_id": "1234567890",
  "access_token": "tiktok_access_token",
  "secret": "chave_de_seguranca_gerada"
}
```

---

## 🐛 Solução de Problemas

### Webhook não funciona
1. Verifique se a URL está acessível
2. Confirme SSL/HTTPS configurado
3. Verifique logs do Stripe

### Eventos não chegam no TikTok
1. Verifique Access Token
2. Confirme Pixel ID
3. Verifique `utm_term` nos links

---

## 🗂️ Estrutura (sugerida)
```text
.
├── deploy/
│   └── tiktok-automation.service
├── src/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── web/
│   └── db/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📄 Licença
MIT License - veja `LICENSE` para detalhes.

---

## 🤝 Contribuição
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📞 Suporte
- 🐛 Issues: GitHub Issues
- 📖 Docs: em breve
# tiktoktracking
# tiktoktracking
# tiktoktracking
