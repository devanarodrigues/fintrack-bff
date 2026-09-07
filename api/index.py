"""
FinTrack BFF - Backend for Frontend (Vercel Serverless)
API Flask para gerenciamento financeiro com suporte a parcelamento e OCR de faturas
Adaptado para funcionar como função serverless na Vercel
"""
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.expenses import expenses_bp
from routes.dashboard import dashboard_bp
from routes.upload import upload_bp
from routes.analytics import analytics_bp
from routes.reports import reports_bp
from database.db import init_db

app = Flask(__name__)
CORS(app)

# Configuração
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = '/tmp'  # Vercel usa /tmp para arquivos temporários

# Registrar blueprints (rotas)
app.register_blueprint(expenses_bp, url_prefix='/api/v1')
app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
app.register_blueprint(upload_bp, url_prefix='/api/v1')
app.register_blueprint(analytics_bp, url_prefix='/api/v1')
app.register_blueprint(reports_bp, url_prefix='/api/v1')

# Inicializar banco de dados (apenas se não estiver em ambiente de teste)
try:
    with app.app_context():
        init_db()
except Exception as e:
    print(f"Aviso: Não foi possível inicializar o banco de dados: {e}")
    print("Isso é normal em ambiente de build/teste da Vercel")

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FinTrack BFF',
        'version': '1.0.0',
        'environment': 'vercel-serverless'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Handler para Vercel
def handler(environ, start_response):
    """Handler para funcionar como função serverless na Vercel"""
    return app(environ, start_response)

# Expor o app para a Vercel
# Isso é necessário para que a Vercel consiga importar e executar a aplicação
__all__ = ['app', 'handler']

# NOTA: Não incluímos app.run() porque a Vercel gerencia a execução
# Em ambiente local, você pode usar: python -c "from api.index import app; app.run(debug=True)"
