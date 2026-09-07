"""
Versão simplificada para teste na Vercel
Apenas para verificar se o setup básico está funcionando
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint simples"""
    return jsonify({
        'status': 'healthy',
        'service': 'FinTrack BFF Test',
        'version': '1.0.0-test',
        'message': 'Setup básico funcionando!'
    })

@app.route('/test')
def test_endpoint():
    """Endpoint de teste"""
    return jsonify({
        'test': 'success',
        'message': 'Endpoint de teste funcionando'
    })

# Handler para Vercel
def handler(environ, start_response):
    """Handler para funcionar como função serverless na Vercel"""
    return app(environ, start_response)

# Expor o app para a Vercel
__all__ = ['app', 'handler']
