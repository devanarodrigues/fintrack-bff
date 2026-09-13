"""
Rotas para upload de faturas
"""
from flask import Blueprint, request, jsonify, current_app
from api.invoice_parser import processar_fatura_pdf
from services.expense_service import ExpenseService
from config import Config
import os
import uuid
import logging
import re

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
        
        # Ler arquivo como bytes
        arquivo_bytes = file.read()
        
        logger.info(f"Processando fatura do cartão: {card}")

        # Converter year e month para int se fornecido
        year_int = int(year) if year else None
        month_int = int(month) if month else None

        # Processar fatura usando o novo parser
        resultado = processar_fatura_pdf(arquivo_bytes, year_int, month_int)
        
        if not resultado.get('success'):
            logger.error(f"Erro ao processar fatura: {resultado.get('erro')}")
            return jsonify({'error': resultado.get('erro')}), 400
        
        # Converter movimentações para o formato esperado pelo sistema
        transactions = []
        temp_id_counter = 1
        
        for mov in resultado['movimentacoes']:
            # Parsear valor
            try:
                valor_str = mov['valor'].replace('.', '').replace(',', '.')
                valor = float(valor_str)
            except:
                valor = 0.0
            
            # Parsear parcela
            parcela_info = mov['parcela']
            if parcela_info == '-':
                tipo = 'normal'
                parcela_atual = 1
                total_parcelas = 1
            else:
                tipo = 'parcelado'
                try:
                    parcela_parts = parcela_info.split('/')
                    parcela_atual = int(parcela_parts[0])
                    total_parcelas = int(parcela_parts[1])
                except:
                    tipo = 'normal'
                    parcela_atual = 1
                    total_parcelas = 1
            
            # Inferir categoria baseada no estabelecimento
            categoria = _infer_category(mov['estabelecimento'])
            
            transaction = {
                'temp_id': f"tmp-{temp_id_counter:03d}",
                'descricao': mov['estabelecimento'],
                'categoria': categoria,
                'valor_parcela': valor,
                'tipo': tipo,
                'parcela_atual': parcela_atual,
                'total_parcelas': total_parcelas,
                'data': mov['data'],  # Data da transação
                'cartao_nome': card or resultado['tipo_fatura'],
                'mapping_status': 'NEW',
                'matched_gasto_pai_id': None
            }
            
            transactions.append(transaction)
            temp_id_counter += 1
        
        # Fazer matching com transações existentes
        transactions, matched_count = _match_with_existing_transactions(transactions)
        
        extracted_data = {
            'processing_id': f"proc-{uuid.uuid4().hex[:8]}",
            'cartao_identificado': resultado['tipo_fatura'],
            'transactions': transactions,
            'total_count': len(transactions),
            'matched_count': matched_count,
            'new_count': len(transactions) - matched_count
        }
        
        logger.info(f"Processamento concluído: {len(transactions)} transações extraídas")
        
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


def _infer_category(descricao):
    """
    Infere a categoria baseada na descrição da transação
    
    Args:
        descricao: Descrição da transação
        
    Returns:
        str: Categoria inferida
    """
    descricao_lower = descricao.lower()
    
    # Mapeamento de palavras-chave para categorias
    category_mapping = {
        'supermercado': 'Alimentação',
        'mercado': 'Alimentação',
        'restaurante': 'Alimentação',
        'lanchonete': 'Alimentação',
        'farmacia': 'Saúde',
        'drogaria': 'Saúde',
        'hospital': 'Saúde',
        'posto': 'Transporte',
        'gasolina': 'Transporte',
        'uber': 'Transporte',
        '99': 'Transporte',
        'loja': 'Vestuário',
        'roupa': 'Vestuário',
        'sapato': 'Vestuário',
        'celular': 'Eletrônicos',
        'notebook': 'Eletrônicos',
        'computador': 'Eletrônicos',
        'tv': 'Eletrônicos',
        'netflix': 'Entretenimento',
        'spotify': 'Entretenimento',
        'cinema': 'Entretenimento',
        'internet': 'Contas Fixas',
        'luz': 'Contas Fixas',
        'água': 'Contas Fixas',
        'aluguel': 'Contas Fixas',
    }
    
    for keyword, category in category_mapping.items():
        if keyword in descricao_lower:
            return category
    
    return 'Outros'


def _match_with_existing_transactions(transactions):
    """
    Tenta fazer match de transações extraídas com gastos existentes no banco
    
    Args:
        transactions: Lista de transações extraídas
        
    Returns:
        list: Transações com status de matching atualizado
    """
    try:
        from database.db import execute_query
        
        matched_count = 0
        
        for transaction in transactions:
            if transaction['tipo'] == 'parcelado':
                # Buscar gastos parcelados similares
                query = """
                    SELECT id, gasto_pai_id, descricao, parcela_atual, total_parcelas
                    FROM gastos 
                    WHERE descricao ILIKE %s 
                    AND tipo = 'parcelado'
                    AND total_parcelas = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                
                results = execute_query(
                    query, 
                    (f"%{transaction['descricao']}%", transaction['total_parcelas']),
                    fetch=True
                )
                
                if results:
                    # Verificar se alguma parcela próxima existe
                    for result in results:
                        existing_parcela = result['parcela_atual']
                        target_parcela = transaction['parcela_atual']
                        
                        # Se a parcela existente é anterior à atual e do mesmo gasto pai
                        if existing_parcela < target_parcela:
                            transaction['mapping_status'] = 'MATCHED'
                            transaction['matched_gasto_pai_id'] = str(result['gasto_pai_id'] or result['id'])
                            matched_count += 1
                            break
        
        return transactions, matched_count
        
    except Exception as e:
        logger.error(f"Erro ao fazer match de transações: {e}")
        return transactions, 0
