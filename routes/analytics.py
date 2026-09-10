"""
Rotas para analytics e linha do tempo
"""
from flask import Blueprint, request, jsonify
from database.db import execute_query
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/timeline', methods=['GET'])
def get_timeline():
    """
    Retorna a linha do tempo de gastos com projeção de parcelas futuras
    
    Query params:
        - months: Número de meses para projetar (default: 6)
    """
    try:
        months = int(request.args.get('months', 6))
        
        # Buscar todos os gastos parcelados ativos
        query = """
            SELECT * FROM gastos 
            WHERE tipo = 'parcelado' 
            AND parcela_atual < total_parcelas
            ORDER BY data ASC
        """
        
        active_installments = execute_query(query, fetch=True)
        
        if not active_installments:
            return jsonify({'items': []}), 200
        
        # Projetar parcelas futuras
        timeline = []
        current_date = datetime.now()
        
        for month_offset in range(months):
            target_date = current_date + timedelta(days=30 * month_offset)
            target_month = target_date.month
            target_year = target_date.year
            
            month_data = {
                'month': target_month,
                'year': target_year,
                'month_name': target_date.strftime('%B'),
                'total': 0.0,
                'installments': []
            }
            
            for installment in active_installments:
                parcela_atual = installment['parcela_atual']
                total_parcelas = installment['total_parcelas']
                
                # Calcular qual parcela cairá neste mês
                months_diff = (target_year - installment['data'].year) * 12 + (target_month - installment['data'].month)
                projected_installment = parcela_atual + months_diff
                
                if projected_installment <= total_parcelas:
                    month_data['installments'].append({
                        'id': str(installment['id']),
                        'descricao': installment['descricao'],
                        'valor_parcela': float(installment['valor_parcela']),
                        'parcela_atual': projected_installment,
                        'total_parcelas': total_parcelas,
                        'cartao_nome': installment.get('cartao_nome', '')
                    })
                    month_data['total'] += float(installment['valor_parcela'])
            
            timeline.append(month_data)
        
        return jsonify({'items': timeline}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar linha do tempo: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/monthly-trend', methods=['GET'])
def get_monthly_trend():
    """
    Retorna a tendência mensal de gastos
    
    Query params:
        - months: Número de meses para buscar (default: 12)
    """
    try:
        months = int(request.args.get('months', 12))
        
        query = """
            SELECT 
                EXTRACT(YEAR FROM data) as year,
                EXTRACT(MONTH FROM data) as month,
                SUM(valor_parcela) as total,
                COUNT(*) as count
            FROM gastos 
            WHERE data >= NOW() - INTERVAL '%s months'
            GROUP BY year, month
            ORDER BY year DESC, month DESC
        """
        
        results = execute_query(query, (months,), fetch=True)
        
        if not results:
            return jsonify({'items': []}), 200
        
        trend = []
        for result in results:
            trend.append({
                'year': int(result['year']),
                'month': int(result['month']),
                'month_name': datetime(int(result['year']), int(result['month']), 1).strftime('%B'),
                'total': float(result['total']),
                'count': result['count']
            })
        
        return jsonify({'items': trend}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar tendência mensal: {e}")
        return jsonify({'error': str(e)}), 500
