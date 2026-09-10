"""
FinTrack BFF - Backend for Frontend
API Flask para gerenciamento financeiro com suporte a parcelamento e OCR de faturas
"""
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

# Registrar blueprints (rotas)
app.register_blueprint(expenses_bp, url_prefix='/api/v1')
app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
app.register_blueprint(upload_bp, url_prefix='/api/v1')
app.register_blueprint(analytics_bp, url_prefix='/api/v1')
app.register_blueprint(reports_bp, url_prefix='/api/v1')

# Inicializar banco de dados
with app.app_context():
    init_db()

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FinTrack BFF',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
