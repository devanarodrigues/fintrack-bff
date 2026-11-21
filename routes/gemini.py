from flask import Blueprint, request, jsonify
import os
import requests
import traceback

gemini_bp = Blueprint('gemini', __name__)

@gemini_bp.route('/test', methods=['GET'])
def test_gemini():
    """
    Endpoint de teste para verificar se o blueprint está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Gemini blueprint is working',
        'gemini_api_key_configured': bool(os.getenv('GEMINI_API_KEY')),
        'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
    })

@gemini_bp.route('/generate-suggestion', methods=['POST', 'OPTIONS'])
def generate_suggestion():
    """
    Gera sugestões de economia usando a API do Gemini
    """
    print(f"DEBUG: generate_suggestion called - Method: {request.method}")
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
        model = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')  # Default value
        
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
        print(f"ERROR: Exception in generate_suggestion: {str(e)}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Erro ao gerar sugestão: {str(e)}'
        }), 500
