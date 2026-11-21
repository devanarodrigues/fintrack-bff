"""
FinTrack BFF - Backend for Frontend (Vercel Serverless)
API Flask para gerenciamento financeiro com suporte a parcelamento e OCR de faturas
Adaptado para funcionar como função serverless na Vercel
"""
import sys
import os
import traceback

# Adicionar o diretório pai ao path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"DEBUG: Current directory: {current_dir}")
print(f"DEBUG: Parent directory: {parent_dir}")
print(f"DEBUG: Python path: {sys.path[:3]}")

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    print("DEBUG: Flask imports successful")
except ImportError as e:
    print(f"ERROR: Failed to import Flask: {e}")
    print(f"ERROR: Traceback: {traceback.format_exc()}")
    raise

# Tentar importar as rotas com tratamento de erro
try:
    from routes.expenses import expenses_bp
    from routes.dashboard import dashboard_bp
    from routes.upload import upload_bp
    from routes.analytics import analytics_bp
    from routes.reports import reports_bp
    from routes.gemini import gemini_bp
    from database.db import init_db
    print("DEBUG: Route imports successful")
    print(f"DEBUG: gemini_bp imported: {gemini_bp}")
except ImportError as e:
    print(f"ERROR: Failed to import routes: {e}")
    print(f"ERROR: Traceback: {traceback.format_exc()}")
    # Continuar sem as rotas para permitir health check
    expenses_bp = None
    dashboard_bp = None
    upload_bp = None
    analytics_bp = None
    reports_bp = None
    gemini_bp = None
    init_db = None

# Nota: O processamento de faturas foi integrado diretamente no routes/upload
# Não precisamos mais do blueprint separado de invoices

app = Flask(__name__)
CORS(app)

# Configuração
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = '/tmp'  # Vercel usa /tmp para arquivos temporários
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB máximo

# Registrar blueprints (rotas) apenas se importaram com sucesso
if expenses_bp:
    try:
        app.register_blueprint(expenses_bp, url_prefix='/api/v1')
        print("DEBUG: expenses_bp registered")
    except Exception as e:
        print(f"ERROR: Failed to register expenses_bp: {e}")

if dashboard_bp:
    try:
        app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
        print("DEBUG: dashboard_bp registered")
    except Exception as e:
        print(f"ERROR: Failed to register dashboard_bp: {e}")

if upload_bp:
    try:
        app.register_blueprint(upload_bp, url_prefix='/api/v1')
        print("DEBUG: upload_bp registered")
    except Exception as e:
        print(f"ERROR: Failed to register upload_bp: {e}")

if analytics_bp:
    try:
        app.register_blueprint(analytics_bp, url_prefix='/api/v1')
        print("DEBUG: analytics_bp registered")
    except Exception as e:
        print(f"ERROR: Failed to register analytics_bp: {e}")

if reports_bp:
    try:
        app.register_blueprint(reports_bp, url_prefix='/api/v1')
        print("DEBUG: reports_bp registered")
    except Exception as e:
        print(f"ERROR: Failed to register reports_bp: {e}")

if gemini_bp:
    try:
        app.register_blueprint(gemini_bp, url_prefix='/api/v1')
        print("DEBUG: gemini_bp registered successfully")
        print(f"DEBUG: gemini_bp url_prefix: /api/v1")
    except Exception as e:
        print(f"ERROR: Failed to register gemini_bp: {e}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
else:
    print("WARNING: gemini_bp is None, not registering")

# Inicializar banco de dados (apenas se não estiver em ambiente de teste)
if init_db:
    try:
        with app.app_context():
            init_db()
            print("DEBUG: Database initialized successfully")
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}")
        print(f"WARNING: Traceback: {traceback.format_exc()}")
        print("WARNING: This is normal in Vercel build/test environment")

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FinTrack BFF',
        'version': '1.0.0',
        'environment': 'vercel-serverless',
        'routes_registered': {
            'expenses': bool(expenses_bp),
            'dashboard': bool(dashboard_bp),
            'upload': bool(upload_bp),
            'analytics': bool(analytics_bp),
            'reports': bool(reports_bp),
            'gemini': bool(gemini_bp)
        }
    })

@app.route('/debug')
def debug_info():
    """Debug endpoint para verificar configuração"""
    return jsonify({
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'path': sys.path,
        'environment': dict(os.environ),
        'flask_config': {k: str(v) for k, v in app.config.items() if k.isupper()},
        'routes': [str(rule) for rule in app.url_map.iter_rules()]
    })

@app.route('/debug/routes')
def debug_routes():
    """Debug endpoint para listar todas as rotas disponíveis"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify({
        'total_routes': len(routes),
        'routes': routes
    })

@app.route('/api/v1/health')
def api_health():
    """Health check para a API v1"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'endpoints': {
            '/api/v1/invoices/upload': 'POST - Upload e processamento de fatura PDF',
            '/api/v1/invoices/confirm': 'POST - Confirmar e salvar transações extraídas',
            '/api/v1/gemini/generate-suggestion': 'POST - Gerar sugestões com IA'
        }
    })

# Rotas diretas para Gemini (bypass do blueprint para garantir funcionamento na Vercel)
@app.route('/api/v1/gemini/test', methods=['GET', 'OPTIONS'])
def gemini_test():
    """Endpoint de teste para Gemini"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        'status': 'ok',
        'message': 'Gemini endpoint is working (direct route)',
        'gemini_api_key_configured': bool(os.getenv('GEMINI_API_KEY')),
        'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
    })

@app.route('/api/v1/gemini/generate-suggestion', methods=['POST', 'OPTIONS'])
def gemini_generate_suggestion():
    """Gera sugestões de economia usando a API do Gemini (rota direta)"""
    print(f"DEBUG: gemini_generate_suggestion called - Method: {request.method}")
    print(f"DEBUG: Request path: {request.path}")
    print(f"DEBUG: Request URL: {request.url}")
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        print("DEBUG: Handling OPTIONS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Obter a API key da variável de ambiente
        api_key = os.getenv('GEMINI_API_KEY')
        model = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
        
        print(f"DEBUG: API Key configured: {bool(api_key)}")
        print(f"DEBUG: Model: {model}")
        
        if not api_key:
            return jsonify({
                'error': 'GEMINI_API_KEY não configurada nas variáveis de ambiente'
            }), 500
        
        # Obter o prompt do request
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({
                'error': 'Prompt não fornecido'
            }), 400
        
        # Fazer requisição para a API do Gemini
        url = 'https://generativelanguage.googleapis.com/v1/interactions'
        
        headers = {
            'x-goog-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'input': prompt
        }
        
        print(f"DEBUG: Sending request to Gemini API")
        print(f"DEBUG: URL: {url}")
        print(f"DEBUG: Model: {model}")
        
        import requests
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"DEBUG: Gemini API response status: {response.status_code}")
        
        if not response.ok:
            error_data = response.json()
            print(f"DEBUG: Gemini API error: {error_data}")
            return jsonify({
                'error': f'Erro na API Gemini: {error_data.get("error", {}).get("message", "Erro desconhecido")}'
            }), response.status_code
        
        result = response.json()
        
        # Extract response from steps array
        ai_response = ''
        if 'steps' in result and len(result['steps']) > 0:
            for step in result['steps']:
                if step.get('type') == 'model_output' and 'content' in step:
                    for content in step['content']:
                        if content.get('type') == 'text':
                            ai_response += content.get('text', '')
        
        if not ai_response:
            return jsonify({
                'error': 'Resposta vazia da API Gemini'
            }), 500
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        print(f"ERROR: Exception in gemini_generate_suggestion: {str(e)}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Erro ao gerar sugestão: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"ERROR: Internal server error: {error}")
    print(f"ERROR: Traceback: {traceback.format_exc()}")
    return jsonify({'error': 'Erro interno do servidor', 'details': str(error)}), 500

# Handler para Vercel
def handler(environ, start_response):
    """Handler para funcionar como função serverless na Vercel"""
    try:
        return app(environ, start_response)
    except Exception as e:
        print(f"ERROR: Handler error: {e}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        # Retornar resposta de erro
        status = '500 Internal Server Error'
        response_body = b'{"error": "Internal Server Error"}'
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]

# Expor o app para a Vercel
# Isso é necessário para que a Vercel consiga importar e executar a aplicação
__all__ = ['app', 'handler']

print("DEBUG: api/index.py loaded successfully")
print("DEBUG: Flask app created and configured")
print("DEBUG: Invoice processing integrated via upload route")

# NOTA: Não incluímos app.run() porque a Vercel gerencia a execução
# Em ambiente local, você pode usar: python -c "from api.index import app; app.run(debug=True)"
