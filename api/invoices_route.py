"""
Rota para processamento de faturas PDF
Integra o módulo invoice_parser à API Flask
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from invoice_parser import processar_fatura_pdf, formatar_resultado_texto

# Criar blueprint
invoices_bp = Blueprint('invoices', __name__)

# Configurações
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    """Retorna o diretório para upload (usa /tmp no Vercel)"""
    upload_folder = '/tmp'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder


@invoices_bp.route('/invoices/process', methods=['POST'])
def processar_fatura():
    """
    Endpoint para processar fatura PDF
    
    Espera:
    - POST multipart/form-data com arquivo PDF
    
    Retorna:
    - JSON com dados extraídos da fatura
    
    Exemplo de uso:
    curl -X POST -F "file=@fatura.pdf" http://localhost:5000/api/v1/invoices/process
    """
    
    # Validar se há arquivo na requisição
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'erro': 'Nenhum arquivo foi enviado. Use o campo "file".'
        }), 400

    file = request.files['file']

    # Validar se o arquivo foi selecionado
    if file.filename == '':
        return jsonify({
            'success': False,
            'erro': 'Nenhum arquivo foi selecionado.'
        }), 400

    # Validar extensão
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'erro': 'Apenas arquivos PDF são permitidos.'
        }), 400

    # Validar tamanho
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({
            'success': False,
            'erro': f'Arquivo muito grande. Máximo permitido: {MAX_FILE_SIZE / (1024*1024):.0f} MB'
        }), 413

    try:
        # Ler arquivo em bytes
        arquivo_bytes = file.read()

        # Processar fatura
        resultado = processar_fatura_pdf(arquivo_bytes)

        # Adicionar informações do arquivo
        resultado['arquivo_original'] = secure_filename(file.filename)

        return jsonify(resultado), 200 if resultado.get('success') else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'erro': f'Erro ao processar requisição: {str(e)}'
        }), 500


@invoices_bp.route('/invoices/process/debug', methods=['POST'])
def processar_fatura_debug():
    """
    Endpoint de debug que retorna também a formatação em texto
    
    Útil para testes e visualização em formato legível
    """
    
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'erro': 'Nenhum arquivo foi enviado. Use o campo "file".'
        }), 400

    file = request.files['file']

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'erro': 'Arquivo inválido. Envie um PDF.'
        }), 400

    try:
        arquivo_bytes = file.read()
        resultado = processar_fatura_pdf(arquivo_bytes)
        resultado['arquivo_original'] = secure_filename(file.filename)
        
        # Adicionar versão formatada em texto
        resultado['texto_formatado'] = formatar_resultado_texto(resultado)

        return jsonify(resultado), 200 if resultado.get('success') else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'erro': f'Erro ao processar requisição: {str(e)}'
        }), 500


@invoices_bp.route('/invoices/health', methods=['GET'])
def health():
    """Health check para o serviço de faturas"""
    return jsonify({
        'status': 'healthy',
        'service': 'invoice-processor',
        'version': '1.0.0',
        'suporta': ['MERCADO_PAGO', 'ITAU']
    }), 200
