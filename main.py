import os
import time
import json
import hashlib
import secrets
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import tempfile

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chave_padrao_insegura')
CORS(app)

# Configuração do banco - FORÇAR SQLITE EM MEMÓRIA
database_url = 'sqlite:///:memory:'
print(" Usando SQLite em memória (dados não persistem entre restarts)")

# Só usar environment se for um caminho válido
env_db_url = os.getenv('DATABASE_URL')
if env_db_url:
    if env_db_url.startswith('postgres://'):
        print("  PostgreSQL detectado, mantendo SQLite em memória")
    elif env_db_url == 'sqlite:///:memory:':
        database_url = env_db_url
        print("  Usando SQLite em memória do ambiente")
    else:
        print(f"  DATABASE_URL inválido ignorado: {env_db_url}")
        print("  Mantendo SQLite em memória")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do Pixel
class TikTokPixel(db.Model):
    __tablename__ = 'tiktok_pixels'
    
    id = db.Column(db.Integer, primary_key=True)
    id_gestor = db.Column(db.String(50), unique=True, nullable=False)
    pixel_id = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    nome_pixel = db.Column(db.String(200))
    chave_seguranca = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.chave_seguranca:
            self.chave_seguranca = secrets.token_hex(32)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_gestor': self.id_gestor,
            'pixel_id': self.pixel_id,
            'nome_pixel': self.nome_pixel,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ativo': self.ativo
        }

# Modelo de Log de Eventos
class EventLog(db.Model):
    __tablename__ = 'event_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    pixel_id = db.Column(db.String(100), nullable=False)
    stripe_event_id = db.Column(db.String(100), nullable=False)
    stripe_event_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, error
    error_message = db.Column(db.Text)
    tiktok_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pixel_id': self.pixel_id,
            'stripe_event_id': self.stripe_event_id,
            'stripe_event_type': self.stripe_event_type,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Classe para integração TikTok
class TikTokEventsAPI:
    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3/pixel/track/"
    PIXEL_LIST_URL = "https://business-api.tiktok.com/open_api/v1.3/pixel/list/"
    
    def __init__(self, access_token, pixel_id):
        self.access_token = access_token
        self.pixel_id = pixel_id
        self.headers = {
            'Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        self.event_source_id = None
    
    def get_valid_event_source_id(self, advertiser_id):
        """Obtém o event_source_id válido via API do TikTok"""
        try:
            params = {
                'advertiser_id': advertiser_id
            }
            response = requests.get(
                self.PIXEL_LIST_URL,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            print(f"Pixel list response ({response.status_code}):", response.text)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and data.get('data', {}).get('list'):
                    for pixel in data['data']['list']:
                        if pixel.get('pixel_id') == self.pixel_id:
                            print(f"Pixel encontrado: {pixel}")
                            return pixel.get('pixel_id')  # Retorna o pixel_id válido
            
            return self.pixel_id  # fallback
        except Exception as e:
            print(f"Erro ao obter event_source_id: {e}")
            return self.pixel_id  # fallback
    
    def _hash_data(self, value):
        """Hash dados do usuário com SHA256"""
        if not value:
            return ""
        return hashlib.sha256(str(value).lower().strip().encode('utf-8')).hexdigest()
    
    def _format_value_for_tiktok(self, value, currency='BRL'):
        """Formatar valor para padrão TikTok"""
        try:
            # Converter para float e garantir 2 casas decimais
            formatted_value = round(float(value), 2)
            
            # TikTok espera valores mínimos diferentes por moeda
            min_values = {
                'BRL': 0.01,  # R$ 0,01
                'USD': 0.01,  # $0.01
                'EUR': 0.01,  # €0.01
            }
            
            min_value = min_values.get(currency.upper(), 0.01)
            
            # Garantir valor mínimo
            if formatted_value < min_value:
                formatted_value = min_value
                
            return formatted_value
        except (ValueError, TypeError):
            return 0.01  # Valor padrão seguro
    
    def send_purchase_event(self, event_data):
        """Envia evento de compra para TikTok - Formato EXATO do exemplo oficial"""
        try:
            # Preparar dados do usuário (hasheados conforme TikTok)
            user_data = {}
            if event_data.get('email'):
                user_data['email'] = self._hash_data(event_data['email'])
            if event_data.get('phone'):
                user_data['phone_number'] = self._hash_data(event_data['phone'])
            if event_data.get('external_id'):
                user_data['external_id'] = self._hash_data(str(event_data['external_id']))
            
            # Formato EXATO do exemplo oficial TikTok
            payload = {
                'pixel_code': self.pixel_id,
                'event': 'Purchase',
                'event_id': f"stripe_{event_data.get('stripe_event_id', '')}",
                'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'context': {
                    'page': {
                        'url': event_data.get('page_url', 'https://example.com/checkout')
                    },
                    'user': user_data
                },
                'properties': {
                    'content_type': 'product',
                    'currency': str(event_data.get('currency', 'BRL')).upper(),
                    'value': self._format_value_for_tiktok(
                        event_data.get('value', 0), 
                        event_data.get('currency', 'BRL')
                    )
                }
            }
            
            print("Enviando para TikTok:", json.dumps(payload, indent=2, ensure_ascii=False))
            
            # Fazer requisição para TikTok
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            print(f"Resposta TikTok ({response.status_code}):", json.dumps(result, indent=2, ensure_ascii=False))
            
            if response.status_code == 200 and result.get('code') == 0:
                return {
                    'success': True,
                    'message': 'Evento enviado para TikTok com sucesso',
                    'tiktok_response': result
                }
            else:
                return {
                    'success': False,
                    'error': f"Erro TikTok (Code: {result.get('code')}): {result.get('message', 'Erro desconhecido')}",
                    'tiktok_response': result
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Erro de rede: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro inesperado: {str(e)}'
            }

# Rotas da API
@app.route('/api/pixels', methods=['GET'])
def list_pixels():
    pixels = TikTokPixel.query.filter_by(ativo=True).all()
    return jsonify({
        'success': True,
        'pixels': [p.to_dict() for p in pixels],
        'total': len(pixels)
    })

@app.route('/api/pixels', methods=['POST'])
def create_pixel():
    # Tenta obter JSON
    data = request.get_json(silent=True)
    
    # Fallback: aceita form-urlencoded/multipart
    if not data:
        form_data = request.form.to_dict() if request.form else {}
        if form_data:
            data = form_data
            app.logger.info("create_pixel: usando dados de formulário (form-urlencoded/multipart)")
        else:
            # Última tentativa: tentar carregar o raw body como JSON
            try:
                if request.data:
                    data = json.loads(request.data)
                    app.logger.info("create_pixel: JSON carregado a partir do raw body")
            except Exception:
                data = None
    
    if not data:
        app.logger.warning(
            f"create_pixel: corpo ausente ou inválido. Content-Type={request.content_type}, raw_body={request.data}"
        )
        return jsonify({'success': False, 'error': 'Corpo inválido ou ausente. Envie JSON (Content-Type: application/json) ou form (application/x-www-form-urlencoded).'}), 400
    
    if not data.get('id_gestor') or not data.get('pixel_id') or not data.get('access_token'):
        return jsonify({'success': False, 'error': 'Dados obrigatórios faltando'}), 400
    
    # Verificar se já existe
    existing = TikTokPixel.query.filter_by(id_gestor=data['id_gestor']).first()
    if existing:
        return jsonify({'success': False, 'error': 'ID do gestor já existe'}), 409
    
    pixel = TikTokPixel(
        id_gestor=data['id_gestor'],
        pixel_id=data['pixel_id'],
        access_token=data['access_token'],
        nome_pixel=data.get('nome_pixel', f"Pixel {data['id_gestor']}")
    )
    
    db.session.add(pixel)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Pixel criado com sucesso',
        'pixel': pixel.to_dict(),
        'chave_seguranca': pixel.chave_seguranca
    }), 201

@app.route('/api/pixels/<id_gestor>', methods=['PUT'])
def update_pixel(id_gestor):
    """Atualizar pixel existente"""
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({'success': False, 'error': 'JSON obrigatório'}), 400
    
    pixel = TikTokPixel.query.filter_by(id_gestor=id_gestor, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': 'Pixel não encontrado'}), 404
    
    # Atualizar campos se fornecidos
    if data.get('access_token'):
        pixel.access_token = data['access_token']
    if data.get('pixel_id'):
        pixel.pixel_id = data['pixel_id']
    if data.get('nome_pixel'):
        pixel.nome_pixel = data['nome_pixel']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Pixel atualizado com sucesso',
        'pixel': pixel.to_dict()
    })

@app.route('/api/pixels/<id_gestor>/test-connectivity', methods=['POST'])
def test_pixel_connectivity(id_gestor):
    """Testar conectividade com TikTok API"""
    pixel = TikTokPixel.query.filter_by(id_gestor=id_gestor, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': 'Pixel não encontrado'}), 404
    
    tiktok_api = TikTokEventsAPI(pixel.access_token, pixel.pixel_id)
    
    # Teste 1: Payload mínimo
    test_payload = {
        'pixel_code': pixel.pixel_id,
        'data': [{
            'event': 'Purchase',
            'event_time': int(time.time()),
            'event_id': 'test_connectivity_123',
            'properties': {
                'value': 1.00,
                'currency': 'USD'
            }
        }]
    }
    
    try:
        response = requests.post(
            tiktok_api.BASE_URL,
            headers=tiktok_api.headers,
            json=test_payload,
            timeout=30
        )
        
        return jsonify({
            'success': True,
            'test_payload': test_payload,
            'response_status': response.status_code,
            'response_body': response.json() if response.content else {},
            'headers_sent': dict(tiktok_api.headers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'test_payload': test_payload,
            'headers_sent': dict(tiktok_api.headers)
        })

@app.route('/api/pixels/<id_gestor>/logs', methods=['GET'])
def get_pixel_logs(id_gestor):
    """Obter logs de eventos de um pixel"""
    pixel = TikTokPixel.query.filter_by(id_gestor=id_gestor, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': 'Pixel não encontrado'}), 404
    
    logs = EventLog.query.filter_by(pixel_id=pixel.pixel_id).order_by(EventLog.created_at.desc()).limit(50).all()
    
    return jsonify({
        'success': True,
        'logs': [log.to_dict() for log in logs],
        'total': len(logs)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas gerais"""
    total_pixels = TikTokPixel.query.filter_by(ativo=True).count()
    total_events = EventLog.query.count()
    success_events = EventLog.query.filter_by(status='success').count()
    
    success_rate = round((success_events / total_events * 100) if total_events > 0 else 0, 1)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_pixels': total_pixels,
            'total_events': total_events,
            'success_rate': success_rate
        }
    })

@app.route('/webhook/stripe/test', methods=['POST'])
def test_webhook():
    """Teste de simulação - NÃO envia para TikTok"""
    data = request.get_json(silent=True)
    
    if not data:
        app.logger.warning(
            f"test_webhook: JSON ausente ou inválido. Content-Type={request.content_type}, raw_body={request.data}"
        )
        return jsonify({'success': False, 'error': 'JSON obrigatório'}), 400
    
    # Extrair ID do gestor dos metadados
    metadata = data.get('data', {}).get('object', {}).get('metadata', {})
    manager_id = metadata.get('utm_term')
    
    if not manager_id:
        return jsonify({'success': False, 'error': 'utm_term não encontrado'}), 400
    
    # Buscar pixel
    pixel = TikTokPixel.query.filter_by(id_gestor=manager_id, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': f'Pixel não encontrado para gestor {manager_id}'}), 404
    
    return jsonify({
        'success': True,
        'message': 'Teste de webhook processado com sucesso',
        'event_id': data.get('id'),
        'manager_id': manager_id,
        'pixel_id': pixel.pixel_id,
        'test_mode': True
    })

@app.route('/webhook/stripe/test-real', methods=['POST'])
def test_webhook_real():
    """Teste que REALMENTE envia para TikTok"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'JSON obrigatório'}), 400
    
    # Extrair ID do gestor
    metadata = data.get('data', {}).get('object', {}).get('metadata', {})
    manager_id = metadata.get('utm_term')
    
    # Se não houver utm_term, usar pixel padrão
    if not manager_id:
        manager_id = 'prod-1'  # Pixel padrão
        print(f"utm_term não encontrado, usando pixel padrão: {manager_id}")
    
    # Buscar pixel
    pixel = TikTokPixel.query.filter_by(id_gestor=manager_id, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': f'Pixel não encontrado para gestor {manager_id}'}), 404
    
    # Criar cliente TikTok
    tiktok_client = TikTokEventsAPI(pixel.access_token, pixel.pixel_id)
    
    # Preparar dados do evento
    event_obj = data.get('data', {}).get('object', {})
    event_data = {
        'stripe_event_id': data.get('id'),
        'value': event_obj.get('amount', 9999) / 100,  # Converter centavos
        'currency': event_obj.get('currency', 'brl'),
        'external_id': event_obj.get('customer', 'test_customer'),
        'email': metadata.get('customer_email', 'test@example.com')
    }
    
    # ENVIAR PARA TIKTOK DE VERDADE
    result = tiktok_client.send_purchase_event(event_data)
    
    # Salvar log
    log = EventLog(
        pixel_id=pixel.pixel_id,
        stripe_event_id=data.get('id'),
        stripe_event_type=data.get('type'),
        status='success' if result['success'] else 'error',
        error_message=result.get('error'),
        tiktok_response=json.dumps(result.get('tiktok_response', {}))
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': result['success'],
        'message': result.get('message', result.get('error')),
        'event_id': data.get('id'),
        'manager_id': manager_id,
        'pixel_id': pixel.pixel_id,
        'tiktok_result': result,
        'real_send': True
    })

def validate_stripe_signature(payload, signature, endpoint_secret):
    """Valida assinatura do webhook Stripe"""
    try:
        import hmac
        import hashlib
        
        if not signature or not endpoint_secret:
            return False
            
        # Extrair timestamp e assinatura
        elements = signature.split(',')
        timestamp = None
        signatures = []
        
        for element in elements:
            key, value = element.split('=', 1)
            if key == 't':
                timestamp = value
            elif key == 'v1':
                signatures.append(value)
        
        if not timestamp or not signatures:
            return False
            
        # Criar payload para verificação
        signed_payload = f"{timestamp}.{payload}"
        
        # Verificar assinatura
        expected_signature = hmac.new(
            endpoint_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)
    except Exception as e:
        print(f"Erro na validação da assinatura: {e}")
        return False

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Webhook real do Stripe com validação de assinatura"""
    try:
        # Obter payload raw para validação de assinatura
        payload = request.get_data(as_text=True)
        signature = request.headers.get('Stripe-Signature', '')
        
        # Validar assinatura Stripe (em produção)
        stripe_endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')
        if stripe_endpoint_secret and not validate_stripe_signature(payload, signature, stripe_endpoint_secret):
            app.logger.warning("Assinatura Stripe inválida")
            return jsonify({'success': False, 'error': 'Assinatura inválida'}), 400
        
        # Parse JSON após validação
        data = request.get_json(silent=True)
        
        if not data:
            app.logger.warning(
                f"stripe_webhook: JSON ausente ou inválido. Content-Type={request.content_type}"
            )
            return jsonify({'success': False, 'error': 'JSON obrigatório'}), 400
    except Exception as e:
        app.logger.error(f"Erro no webhook Stripe: {e}")
        return jsonify({'success': False, 'error': 'Erro interno'}), 500
    
    # Processar apenas eventos de pagamento bem-sucedidos
    if data.get('type') not in ['payment_intent.succeeded', 'checkout.session.completed']:
        return jsonify({'success': True, 'message': 'Evento ignorado'}), 200
    
    # Extrair ID do gestor
    metadata = data.get('data', {}).get('object', {}).get('metadata', {})
    manager_id = metadata.get('utm_term')
    
    # Se não houver utm_term, usar pixel padrão
    if not manager_id:
        manager_id = 'prod-1'  # Pixel padrão
        print(f"utm_term não encontrado, usando pixel padrão: {manager_id}")
    
    # Buscar pixel
    pixel = TikTokPixel.query.filter_by(id_gestor=manager_id, ativo=True).first()
    if not pixel:
        return jsonify({'success': False, 'error': f'Pixel não encontrado para gestor {manager_id}'}), 404
    
    # Criar cliente TikTok
    tiktok_client = TikTokEventsAPI(pixel.access_token, pixel.pixel_id)
    
    # Preparar dados do evento com extração melhorada
    event_obj = data.get('data', {}).get('object', {})
    
    # Extrair dados do cliente de múltiplas fontes
    customer_email = (
        metadata.get('customer_email') or 
        event_obj.get('receipt_email') or
        event_obj.get('billing_details', {}).get('email') or
        event_obj.get('customer_details', {}).get('email')  # Para checkout.session
    )
    
    customer_phone = (
        metadata.get('customer_phone') or
        event_obj.get('billing_details', {}).get('phone') or
        event_obj.get('customer_details', {}).get('phone')  # Para checkout.session
    )
    
    # Extrair nome do cliente
    customer_name = (
        event_obj.get('customer_details', {}).get('name') or
        event_obj.get('billing_details', {}).get('name')
    )
    
    # Para checkout.session.completed, buscar customer details
    customer_id = event_obj.get('customer') or event_obj.get('payment_intent')
    
    # Determinar valor correto baseado no tipo de evento
    if data.get('type') == 'checkout.session.completed':
        amount = event_obj.get('amount_total', 0)
    else:
        amount = event_obj.get('amount', 0)
    
    event_data = {
        'stripe_event_id': data.get('id'),
        'value': amount / 100,  # Converter centavos
        'currency': event_obj.get('currency', 'brl'),
        'external_id': customer_id,
        'email': customer_email,
        'phone': customer_phone,
        'customer_name': customer_name,
        'page_url': event_obj.get('success_url', 'https://checkout.stripe.com/success')
    }
    
    print(f"Dados extraídos do Stripe: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
    
    # Enviar para TikTok
    result = tiktok_client.send_purchase_event(event_data)
    
    # Salvar log
    log = EventLog(
        pixel_id=pixel.pixel_id,
        stripe_event_id=data.get('id'),
        stripe_event_type=data.get('type'),
        status='success' if result['success'] else 'error',
        error_message=result.get('error'),
        tiktok_response=json.dumps(result.get('tiktok_response', {}))
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': result['success'],
        'message': result.get('message', result.get('error')),
        'event_id': data.get('id'),
        'manager_id': manager_id,
        'pixel_id': pixel.pixel_id
    })

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Criar Payment Intent para teste"""
    try:
        data = request.get_json()
        
        # Simular criação de Payment Intent (você precisa usar sua Stripe Secret Key real)
        return jsonify({
            'client_secret': 'pi_test_1234567890_secret_fake',
            'message': 'Use sua própria implementação Stripe aqui'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/webhook-info', methods=['GET'])
def webhook_info():
    """Informações para configurar webhook do Stripe"""
    base_url = request.host_url.rstrip('/')
    
    return jsonify({
        'webhook_url': f"{base_url}/webhook/stripe",
        'events_to_listen': [
            'payment_intent.succeeded',
            'checkout.session.completed'
        ],
        'instructions': {
            'step_1': 'Acesse o Stripe Dashboard → Developers → Webhooks',
            'step_2': f'Adicione endpoint: {base_url}/webhook/stripe',
            'step_3': 'Selecione eventos: payment_intent.succeeded, checkout.session.completed',
            'step_4': 'Copie o Signing Secret e configure STRIPE_ENDPOINT_SECRET no servidor',
            'step_5': 'Adicione utm_term=<pixel_id> nos metadata dos pagamentos'
        },
        'metadata_required': {
            'utm_term': 'ID do pixel (ex: prod-1)',
            'customer_email': 'Email do cliente (opcional)',
            'customer_phone': 'Telefone do cliente (opcional)'
        }
    })

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
