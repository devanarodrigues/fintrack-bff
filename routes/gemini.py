from flask import Blueprint, request, jsonify
import os
import requests

gemini_bp = Blueprint('gemini', __name__)

@gemini_bp.route('/generate-suggestion', methods=['POST', 'OPTIONS'])
def generate_suggestion():
    """
    Gera sugestões de economia usando a API do Gemini
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Obter a API key da variável de ambiente
        api_key = os.getenv('GEMINI_API_KEY')
        
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
        url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
        
        headers = {
            'x-goog-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if not response.ok:
            error_data = response.json()
            return jsonify({
                'error': f'Erro na API Gemini: {error_data.get("error", {}).get("message", "Erro desconhecido")}'
            }), response.status_code
        
        result = response.json()
        ai_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not ai_response:
            return jsonify({
                'error': 'Resposta vazia da API Gemini'
            }), 500
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao gerar sugestão: {str(e)}'
        }), 500
