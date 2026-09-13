"""
Serviço para gerenciamento de gastos
"""
from database.db import execute_query
from datetime import datetime, date
import uuid
import logging
import re

def normalize_date_format(date_str):
    """
    Normaliza o formato da data para ISO (YYYY-MM-DD)
    Aceita formatos: DD/MM/YYYY, YYYY-MM-DD, YYYY/MM/DD
    """
    if not date_str:
        return None

    # Se já estiver no formato ISO, retorna como está
    if isinstance(date_str, date):
        return date_str.isoformat()

    date_str = str(date_str).strip()

    # Se já estiver no formato YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # Se estiver no formato DD/MM/YYYY, converte para YYYY-MM-DD
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            # Verifica se está no formato DD/MM/YYYY
            if len(parts[2]) == 4:  # Ano com 4 dígitos
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
            # Se estiver no formato YYYY/MM/DD
            elif len(parts[0]) == 4:
                return f"{parts[0]}-{parts[1]}-{parts[2]}"

    return date_str

logger = logging.getLogger(__name__)

class ExpenseService:
    """Serviço para operações com gastos"""
    
    @staticmethod
    def create_expense(expense_data):
        """
        Cria um novo gasto no banco de dados
        
        Args:
            expense_data: Dicionário com dados do gasto
            
        Returns:
            dict: Gasto criado
        """
        try:
            expense_id = str(uuid.uuid4())
            gasto_pai_id = expense_data.get('gasto_pai_id')
            
            # Se for parcelado e não tiver gasto_pai_id, cria um novo
            if expense_data.get('tipo') == 'parcelado' and not gasto_pai_id:
                gasto_pai_id = expense_id
            
            query = """
                INSERT INTO gastos (id, gasto_pai_id, data, cartao_id, cartao_nome, 
                                   categoria, descricao, valor_parcela, tipo, 
                                   parcela_atual, total_parcelas, origem, observacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            
            params = (
                expense_id,
                gasto_pai_id,
                normalize_date_format(expense_data['data']),
                expense_data.get('cartao_id'),
                expense_data['cartao_nome'],
                expense_data['categoria'],
                expense_data['descricao'],
                expense_data['valor_parcela'],
                expense_data['tipo'],
                expense_data.get('parcela_atual', 1),
                expense_data.get('total_parcelas', 1),
                expense_data['origem'],
                expense_data.get('observacao')
            )
            
            result = execute_query(query, params, fetch=True, commit=True)
            
            if result:
                return dict(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar gasto: {e}")
            raise
    
    @staticmethod
    def get_expenses(page=1, limit=10, search=None, category=None, card=None, month=None, year=None):
        """
        Busca gastos com filtros e paginação
        
        Args:
            page: Número da página
            limit: Limite de itens por página
            search: Termo de busca na descrição
            category: Filtro por categoria
            card: Filtro por cartão
            month: Filtro por mês
            year: Filtro por ano
            
        Returns:
            dict: Lista de gastos com metadados de paginação
        """
        try:
            offset = (page - 1) * limit
            
            # Construir query base
            base_query = "SELECT * FROM gastos WHERE 1=1"
            count_query = "SELECT COUNT(*) as total FROM gastos WHERE 1=1"
            params = []
            
            # Adicionar filtros
            if search:
                base_query += " AND descricao ILIKE %s"
                count_query += " AND descricao ILIKE %s"
                params.append(f"%{search}%")
            
            if category:
                base_query += " AND categoria = %s"
                count_query += " AND categoria = %s"
                params.append(category)
            
            if card:
                base_query += " AND cartao_nome = %s"
                count_query += " AND cartao_nome = %s"
                params.append(card)
            
            if month and year:
                base_query += " AND EXTRACT(MONTH FROM data) = %s AND EXTRACT(YEAR FROM data) = %s"
                count_query += " AND EXTRACT(MONTH FROM data) = %s AND EXTRACT(YEAR FROM data) = %s"
                params.extend([month, year])
            
            # Adicionar ordenação e paginação
            base_query += " ORDER BY data DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            # Executar queries
            items = execute_query(base_query, tuple(params), fetch=True)
            total_result = execute_query(count_query, tuple(params[:-2]), fetch=True)
            
            total = total_result[0]['total'] if total_result else 0
            
            # Converter para formato de resposta
            items_list = [dict(item) for item in items] if items else []
            
            # Converter datas para string ISO
            for item in items_list:
                if item.get('data'):
                    item['data'] = item['data'].isoformat()
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
                if item.get('updated_at'):
                    item['updated_at'] = item['updated_at'].isoformat()
            
            return {
                'items': items_list,
                'total': total,
                'page': page,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar gastos: {e}")
            raise
    
    @staticmethod
    def get_expense_by_id(expense_id):
        """
        Busca um gasto por ID
        
        Args:
            expense_id: ID do gasto
            
        Returns:
            dict: Gasto encontrado ou None
        """
        try:
            query = "SELECT * FROM gastos WHERE id = %s"
            result = execute_query(query, (expense_id,), fetch=True)
            
            if result:
                expense = dict(result[0])
                # Converter datas para string ISO
                if expense.get('data'):
                    expense['data'] = expense['data'].isoformat()
                if expense.get('created_at'):
                    expense['created_at'] = expense['created_at'].isoformat()
                if expense.get('updated_at'):
                    expense['updated_at'] = expense['updated_at'].isoformat()
                return expense
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar gasto por ID: {e}")
            raise
    
    @staticmethod
    def update_expense(expense_id, expense_data):
        """
        Atualiza um gasto existente
        
        Args:
            expense_id: ID do gasto
            expense_data: Dicionário com dados a atualizar
            
        Returns:
            dict: Gasto atualizado
        """
        try:
            # Construir query dinâmica
            update_fields = []
            params = []
            
            for field, value in expense_data.items():
                if value is not None:
                    # Normalizar formato de data se for o campo 'data'
                    if field == 'data':
                        value = normalize_date_format(value)
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return None
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(expense_id)
            
            query = f"""
                UPDATE gastos 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            result = execute_query(query, tuple(params), fetch=True, commit=True)
            
            if result:
                expense = dict(result[0])
                # Converter datas para string ISO
                if expense.get('data'):
                    expense['data'] = expense['data'].isoformat()
                if expense.get('created_at'):
                    expense['created_at'] = expense['created_at'].isoformat()
                if expense.get('updated_at'):
                    expense['updated_at'] = expense['updated_at'].isoformat()
                return expense
            return None
            
        except Exception as e:
            logger.error(f"Erro ao atualizar gasto: {e}")
            raise
    
    @staticmethod
    def delete_expense(expense_id):
        """
        Deleta um gasto por ID
        
        Args:
            expense_id: ID do gasto
            
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            query = "DELETE FROM gastos WHERE id = %s"
            execute_query(query, (expense_id,), fetch=False)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar gasto: {e}")
            raise
    
    @staticmethod
    def get_installments_by_parent(gasto_pai_id):
        """
        Busca todas as parcelas de um gasto pai
        
        Args:
            gasto_pai_id: ID do gasto pai
            
        Returns:
            list: Lista de parcelas
        """
        try:
            query = """
                SELECT * FROM gastos 
                WHERE gasto_pai_id = %s OR id = %s
                ORDER BY data ASC
            """
            result = execute_query(query, (gasto_pai_id, gasto_pai_id), fetch=True)
            
            if result:
                items = [dict(item) for item in result]
                # Converter datas para string ISO
                for item in items:
                    if item.get('data'):
                        item['data'] = item['data'].isoformat()
                    if item.get('created_at'):
                        item['created_at'] = item['created_at'].isoformat()
                    if item.get('updated_at'):
                        item['updated_at'] = item['updated_at'].isoformat()
                return items
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar parcelas: {e}")
            raise
