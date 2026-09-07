"""
Rotas para upload de faturas
"""
from flask import Blueprint, request, jsonify, current_app
from services.ocr_service import OCRService
from services.expense_service import ExpenseService
from config import Config
import os
import uuid
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/invoices/upload', methods=['POST'])
def upload_invoice():
    """
    Faz upload de uma fatura de cartão de crédito em PDF
    
    Form data:
        - file: Arquivo PDF
        - card: Nome do cartão
        - month: Mês da fatura (1-12)
        - year: Ano da fatura
    """
    try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        card = request.form.get('card')
        month = request.form.get('month')
        year = request.form.get('year')
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Validar extensão do arquivo
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Apenas arquivos PDF são aceitos'}), 400
        
        # Validar tamanho do arquivo (10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 10 * 1024 * 1024:
            return jsonify({'error': 'Arquivo maior que 10MB'}), 400
        
        # Usar pasta de uploads correta para o ambiente
        upload_folder = Config.get_upload_folder()
        
        # Salvar arquivo temporariamente
        filename = f"{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        logger.info(f"Arquivo salvo: {file_path}")
        
        # Processar OCR
        extracted_data = OCRService.extract_invoice_data(file_path, card or 'Desconhecido')
        
        # Fazer matching com transações existentes
        transactions, matched_count = OCRService.match_with_existing_transactions(
            extracted_data['transactions']
        )
        
        extracted_data['transactions'] = transactions
        extracted_data['matched_count'] = matched_count
        extracted_data['new_count'] = len(transactions) - matched_count
        
        # Deletar arquivo temporário
        try:
            os.remove(file_path)
            logger.info(f"Arquivo temporário removido: {file_path}")
        except:
            logger.warning(f"Não foi possível remover arquivo temporário: {file_path}")
        
        return jsonify(extracted_data), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar upload: {e}")
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/invoices/confirm', methods=['POST'])
def confirm_invoice():
    """
    Confirma e salva as transações extraídas da fatura
    
    Body:
        - processing_id: ID do processamento
        - transactions: Lista de transações a serem salvas
    """
    try:
        data = request.get_json()
        processing_id = data.get('processing_id')
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({'error': 'Nenhuma transação para salvar'}), 400
        
        saved_expenses = []
        
        for transaction in transactions:
            # Preparar dados para salvar
            expense_data = {
                'data': transaction.get('data'),  # Precisa ser fornecido pelo frontend
                'cartao_nome': transaction.get('cartao_nome', 'Desconhecido'),
                'categoria': transaction.get('categoria'),
                'descricao': transaction.get('descricao'),
                'valor_parcela': transaction.get('valor_parcela'),
                'tipo': transaction.get('tipo'),
                'parcela_atual': transaction.get('parcela_atual', 1),
                'total_parcelas': transaction.get('total_parcelas', 1),
                'origem': 'fatura',
                'gasto_pai_id': transaction.get('matched_gasto_pai_id')
            }
            
            saved_expense = ExpenseService.create_expense(expense_data)
            if saved_expense:
                saved_expenses.append(saved_expense)
        
        return jsonify({
            'processing_id': processing_id,
            'saved_count': len(saved_expenses),
            'expenses': saved_expenses
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao confirmar fatura: {e}")
        return jsonify({'error': str(e)}), 500
