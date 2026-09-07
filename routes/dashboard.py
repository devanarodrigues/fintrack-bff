"""
Rotas para o dashboard
"""
from flask import Blueprint, request, jsonify
from services.dashboard_service import DashboardService
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """
    Retorna o resumo do dashboard
    
    Query params:
        - month: Mês (1-12, default: mês atual)
        - year: Ano (default: ano atual)
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        summary = DashboardService.get_summary(month=month, year=year)
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo do dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/cards', methods=['GET'])
def get_cards_summary():
    """
    Retorna o resumo por cartão
    
    Query params:
        - month: Mês (1-12, default: mês atual)
        - year: Ano (default: ano atual)
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        cards_summary = DashboardService.get_cards_summary(month=month, year=year)
        
        return jsonify({'items': cards_summary}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo por cartão: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/categories', methods=['GET'])
def get_categories_summary():
    """
    Retorna o resumo por categoria
    
    Query params:
        - month: Mês (1-12, default: mês atual)
        - year: Ano (default: ano atual)
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        categories_summary = DashboardService.get_categories_summary(month=month, year=year)
        
        return jsonify({'items': categories_summary}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo por categoria: {e}")
        return jsonify({'error': str(e)}), 500
