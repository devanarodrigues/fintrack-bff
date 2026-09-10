"""
Serviço para cálculos do dashboard
"""
from database.db import execute_query
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    """Serviço para operações do dashboard"""
    
    @staticmethod
    def get_summary(month=None, year=None):
        """
        Calcula o resumo do dashboard para um mês específico
        
        Args:
            month: Mês (1-12), usa o mês atual se não fornecido
            year: Ano, usa o ano atual se não fornecido
            
        Returns:
            dict: Resumo do dashboard
        """
        try:
            # Usar mês atual se não fornecido
            if month is None or year is None:
                now = datetime.now()
                month = now.month if month is None else month
                year = now.year if year is None else year
            
            # Buscar gastos do mês
            query = """
                SELECT * FROM gastos 
                WHERE EXTRACT(MONTH FROM data) = %s 
                AND EXTRACT(YEAR FROM data) = %s
            """
            monthly_expenses = execute_query(query, (month, year), fetch=True)
            
            # Buscar todos os gastos para cálculos de fixos e parcelas futuras
            all_expenses_query = "SELECT * FROM gastos"
            all_expenses = execute_query(all_expenses_query, fetch=True)
            
            if not monthly_expenses:
                monthly_expenses = []
            if not all_expenses:
                all_expenses = []
            
            # Calcular total do mês
            total_month = sum(Decimal(str(exp['valor_parcela'])) for exp in monthly_expenses)
            
            # Calcular totais por cartão
            card_totals = {}
            for exp in monthly_expenses:
                card = exp.get('cartao_nome', 'Desconhecido')
                card_totals[card] = card_totals.get(card, Decimal('0')) + Decimal(str(exp['valor_parcela']))
            
            # Encontrar cartão principal
            top_card = max(card_totals.items(), key=lambda x: x[1]) if card_totals else ('—', Decimal('0'))
            top_card_pct = float((top_card[1] / total_month) * 100) if total_month > 0 else 0
            
            # Encontrar maior gasto do mês
            biggest_expense = None
            if monthly_expenses:
                biggest = max(monthly_expenses, key=lambda x: x['valor_parcela'])
                biggest_expense = {
                    'id': str(biggest['id']),
                    'descricao': biggest['descricao'],
                    'valor_parcela': float(biggest['valor_parcela']),
                    'data': biggest['data'].isoformat() if biggest.get('data') else None,
                    'cartao_nome': biggest.get('cartao_nome', ''),
                    'categoria': biggest.get('categoria', '')
                }
            
            # Calcular despesas fixas
            fixed_expenses = sum(
                Decimal(str(exp['valor_parcela'])) 
                for exp in all_expenses 
                if exp.get('tipo') == 'fixo'
            )
            
            # Calcular parcelas ativas (parcelas restantes)
            future_installments = Decimal('0')
            active_installments_count = 0
            
            for exp in all_expenses:
                if exp.get('tipo') == 'parcelado':
                    parcela_atual = exp.get('parcela_atual', 1)
                    total_parcelas = exp.get('total_parcelas', 1)
                    if parcela_atual < total_parcelas:
                        future_installments += Decimal(str(exp['valor_parcela']))
                        active_installments_count += 1
            
            # Previsão próximo mês (fixos + metade das parcelas futuras)
            next_month_forecast = fixed_expenses + (future_installments * Decimal('0.5'))
            
            return {
                'total_month': float(total_month),
                'top_card': top_card[0],
                'top_card_pct': round(top_card_pct, 1),
                'biggest_expense': biggest_expense,
                'future_installments': float(future_installments),
                'fixed_expenses': float(fixed_expenses),
                'next_month_forecast': float(next_month_forecast),
                'total_expenses_count': len(monthly_expenses),
                'active_installments_count': active_installments_count
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo do dashboard: {e}")
            raise
    
    @staticmethod
    def get_cards_summary(month=None, year=None):
        """
        Calcula o resumo por cartão para um mês específico
        
        Args:
            month: Mês (1-12)
            year: Ano
            
        Returns:
            list: Lista de resumos por cartão
        """
        try:
            if month is None or year is None:
                now = datetime.now()
                month = now.month if month is None else month
                year = now.year if year is None else year
            
            query = """
                SELECT cartao_nome, SUM(valor_parcela) as total, COUNT(*) as count
                FROM gastos 
                WHERE EXTRACT(MONTH FROM data) = %s 
                AND EXTRACT(YEAR FROM data) = %s
                GROUP BY cartao_nome
                ORDER BY total DESC
            """
            
            results = execute_query(query, (month, year), fetch=True)
            
            if not results:
                return []
            
            # Calcular total geral
            total_sum = sum(Decimal(str(r['total'])) for r in results)
            
            # Construir resposta
            cards_summary = []
            for result in results:
                cards_summary.append({
                    'card_name': result['cartao_nome'],
                    'total_spent': float(result['total']),
                    'transaction_count': result['count'],
                    'percentage': round(float(result['total'] / total_sum * 100), 1) if total_sum > 0 else 0
                })
            
            return cards_summary
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo por cartão: {e}")
            raise
    
    @staticmethod
    def get_categories_summary(month=None, year=None):
        """
        Calcula o resumo por categoria para um mês específico
        
        Args:
            month: Mês (1-12)
            year: Ano
            
        Returns:
            list: Lista de resumos por categoria
        """
        try:
            if month is None or year is None:
                now = datetime.now()
                month = now.month if month is None else month
                year = now.year if year is None else year
            
            query = """
                SELECT categoria, SUM(valor_parcela) as total, COUNT(*) as count
                FROM gastos 
                WHERE EXTRACT(MONTH FROM data) = %s 
                AND EXTRACT(YEAR FROM data) = %s
                GROUP BY categoria
                ORDER BY total DESC
            """
            
            results = execute_query(query, (month, year), fetch=True)
            
            if not results:
                return []
            
            # Calcular total geral
            total_sum = sum(Decimal(str(r['total'])) for r in results)
            
            # Construir resposta
            categories_summary = []
            for result in results:
                categories_summary.append({
                    'category': result['categoria'],
                    'total_spent': float(result['total']),
                    'transaction_count': result['count'],
                    'percentage': round(float(result['total'] / total_sum * 100), 1) if total_sum > 0 else 0
                })
            
            return categories_summary
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo por categoria: {e}")
            raise
