"""
Rotas para gerenciamento de gastos
"""
from flask import Blueprint, request, jsonify
from services.expense_service import ExpenseService
import logging

logger = logging.getLogger(__name__)

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """
    Busca gastos com filtros e paginação
    
    Query params:
        - page: Número da página (default: 1)
        - limit: Limite de itens por página (default: 10)
        - search: Termo de busca na descrição
        - category: Filtro por categoria
        - card: Filtro por cartão
        - month: Filtro por mês (1-12)
        - year: Filtro por ano
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search')
        category = request.args.get('category')
        card = request.args.get('card')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        result = ExpenseService.get_expenses(
            page=page,
            limit=limit,
            search=search,
            category=category,
            card=card,
            month=month,
            year=year
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar gastos: {e}")
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Busca um gasto por ID
    """
    try:
        expense = ExpenseService.get_expense_by_id(expense_id)
        
        if expense:
            return jsonify(expense), 200
        else:
            return jsonify({'error': 'Gasto não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar gasto: {e}")
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses', methods=['POST'])
def create_expense():
    """
    Cria um novo gasto
    
    Body:
        - data: Data do gasto (YYYY-MM-DD)
        - cartao_nome: Nome do cartão
        - categoria: Categoria do gasto
        - descricao: Descrição do gasto
        - valor_parcela: Valor da parcela
        - tipo: Tipo (normal, parcelado, fixo)
        - parcela_atual: Número da parcela atual (default: 1)
        - total_parcelas: Total de parcelas (default: 1)
        - origem: Origem (manual, fatura)
        - observacao: Observação (opcional)
    """
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['data', 'cartao_nome', 'categoria', 'descricao', 'valor_parcela', 'tipo', 'origem']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        expense = ExpenseService.create_expense(data)
        
        if expense:
            return jsonify(expense), 201
        else:
            return jsonify({'error': 'Erro ao criar gasto'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar gasto: {e}")
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    Atualiza um gasto existente
    """
    try:
        data = request.get_json()
        
        expense = ExpenseService.update_expense(expense_id, data)
        
        if expense:
            return jsonify(expense), 200
        else:
            return jsonify({'error': 'Gasto não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao atualizar gasto: {e}")
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Deleta um gasto por ID
    """
    try:
        success = ExpenseService.delete_expense(expense_id)
        
        if success:
            return jsonify({'message': 'Gasto deletado com sucesso'}), 200
        else:
            return jsonify({'error': 'Gasto não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao deletar gasto: {e}")
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<expense_id>/installments', methods=['GET'])
def get_installments(expense_id):
    """
    Busca todas as parcelas de um gasto
    """
    try:
        installments = ExpenseService.get_installments_by_parent(expense_id)
        return jsonify({'items': installments}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar parcelas: {e}")
        return jsonify({'error': str(e)}), 500
