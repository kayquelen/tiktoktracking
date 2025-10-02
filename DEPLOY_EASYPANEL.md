# 🚀 Deploy no EasyPanel

## Pré-requisitos

1. ✅ **Conta no EasyPanel** configurada
2. ✅ **Projeto Supabase** criado e funcionando
3. ✅ **Chaves do Stripe** (opcional, para webhooks)

## Passos para Deploy

### 1. **Criar Aplicação no EasyPanel**
- Acesse seu painel do EasyPanel
- Clique em **"Create Application"**
- Escolha **"Docker"** como tipo
- Nome: `tiktok-stripe-integration`

### 2. **Configurar Repository**
- **Source**: GitHub/GitLab (ou upload do código)
- **Branch**: `main` ou `master`
- **Dockerfile**: `Dockerfile` (já está pronto)

### 3. **Configurar Variáveis de Ambiente**
No EasyPanel, adicione estas variáveis:

```bash
# App
APP_ENV=production
FLASK_SECRET_KEY=sua-chave-secreta-super-segura-aqui
HOST=0.0.0.0
PORT=5000
DEBUG=false

# Supabase
SUPABASE_URL=https://joybyklcujhdfxljsmhb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpveWJ5a2xjdWpoZGZ4bGpzbWhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzNzMwNjAsImV4cCI6MjA3NDk0OTA2MH0.nMUBjsKjDPhgL-4WvsdI3ujHELKS9EbkGPoCg6tduWU
DATABASE_URL=postgresql://postgres:maquinameia@db.joybyklcujhdfxljsmhb.supabase.co:5432/postgres

# Stripe (configure com suas chaves reais)
STRIPE_SECRET_KEY=sk_live_sua_chave_stripe
STRIPE_ENDPOINT_SECRET=whsec_sua_chave_webhook
```

### 4. **Configurar Porta**
- **Port**: `5000` (já configurado no Dockerfile)
- **Health Check**: `/health`

### 5. **Deploy**
- Clique em **"Deploy"**
- Aguarde o build e deploy
- Teste a aplicação

## Pós-Deploy

### 1. **Testar Aplicação**
- Acesse a URL fornecida pelo EasyPanel
- Verifique se a interface carrega
- Teste o cadastro de um pixel

### 2. **Configurar Webhook do Stripe**
- Copie a URL da aplicação (ex: `https://sua-app.easypanel.host`)
- No Stripe Dashboard → Webhooks
- Adicione endpoint: `https://sua-app.easypanel.host/webhook/stripe`
- Eventos: `payment_intent.succeeded`, `checkout.session.completed`

### 3. **Verificar Logs**
- No EasyPanel, monitore os logs
- Verifique se a conexão com Supabase está funcionando

## Troubleshooting

### Problema: Erro de conexão com Supabase
- Verifique se as variáveis `SUPABASE_URL` e `DATABASE_URL` estão corretas
- Confirme que o projeto Supabase está ativo

### Problema: Webhook não funciona
- Verifique se `STRIPE_ENDPOINT_SECRET` está configurado
- Confirme que a URL do webhook está correta no Stripe

### Problema: Interface não carrega
- Verifique se o arquivo `static/index.html` existe
- Confirme que a porta 5000 está exposta

## URLs Importantes

- **Aplicação**: `https://sua-app.easypanel.host`
- **Health Check**: `https://sua-app.easypanel.host/health`
- **API Info**: `https://sua-app.easypanel.host/api`
- **Webhook**: `https://sua-app.easypanel.host/webhook/stripe`

## Monitoramento

- **Logs**: EasyPanel Dashboard → Logs
- **Métricas**: EasyPanel Dashboard → Metrics
- **Supabase**: Dashboard do Supabase para monitorar banco
