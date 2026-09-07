"""
Serviço para OCR de faturas de cartão de crédito
Utiliza pdfplumber para extração de texto e dados de PDFs
"""
import pdfplumber
import re
import uuid
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """Serviço para processamento OCR de faturas"""
    
    @staticmethod
    def extract_invoice_data(pdf_path, card_name):
        """
        Extrai dados de uma fatura de cartão de crédito de um PDF
        
        Args:
            pdf_path: Caminho do arquivo PDF
            card_name: Nome do cartão identificado
            
        Returns:
            dict: Dados extraídos da fatura
        """
        try:
            processing_id = f"proc-{uuid.uuid4().hex[:8]}"
            transactions = []
            
            with pdfplumber.open(pdf_path) as pdf:
                # Extrair texto de todas as páginas
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                logger.info(f"Texto extraído do PDF: {len(full_text)} caracteres")
                
                # Processar linhas para identificar transações
                lines = full_text.split('\n')
                temp_id_counter = 1
                
                for line in lines:
                    # Tentar identificar padrões de transação
                    transaction = OCRService._parse_transaction_line(line, card_name)
                    if transaction:
                        transaction['temp_id'] = f"tmp-{temp_id_counter:03d}"
                        transactions.append(transaction)
                        temp_id_counter += 1
            
            logger.info(f"Transações extraídas: {len(transactions)}")
            
            return {
                'processing_id': processing_id,
                'cartao_identificado': card_name,
                'transactions': transactions,
                'total_count': len(transactions),
                'matched_count': 0,
                'new_count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da fatura: {e}")
            raise
    
    @staticmethod
    def _parse_transaction_line(line, card_name):
        """
        Parseia uma linha de texto para identificar uma transação
        
        Args:
            line: Linha de texto
            card_name: Nome do cartão
            
        Returns:
            dict: Dados da transação ou None
        """
        try:
            # Padrão regex para identificar transações com parcelamento
            # Exemplo: "Notebook 03/10 R$ 250,00" ou "Notebook 3/10 250.00"
            installment_pattern = r'(.+?)\s*(\d{1,2})/(\d{1,2})\s*[R$]?\s*([\d.,]+)'
            match = re.search(installment_pattern, line)
            
            if match:
                descricao = match.group(1).strip()
                parcela_atual = int(match.group(2))
                total_parcelas = int(match.group(3))
                valor_str = match.group(4).replace(',', '.').replace('R$', '').strip()
                
                # Tentar converter valor
                try:
                    valor = Decimal(valor_str)
                except:
                    valor = Decimal('0.00')
                
                # Inferir categoria baseada na descrição
                categoria = OCRService._infer_category(descricao)
                
                return {
                    'descricao': descricao,
                    'categoria': categoria,
                    'valor_parcela': valor,
                    'tipo': 'parcelado',
                    'parcela_atual': parcela_atual,
                    'total_parcelas': total_parcelas,
                    'mapping_status': 'NEW',
                    'matched_gasto_pai_id': None
                }
            
            # Padrão para transações normais
            # Exemplo: "Supermercado R$ 150,00" ou "Supermercado 150.00"
            normal_pattern = r'(.+?)\s*[R$]?\s*([\d.,]+)'
            match = re.search(normal_pattern, line)
            
            if match:
                descricao = match.group(1).strip()
                valor_str = match.group(2).replace(',', '.').replace('R$', '').strip()
                
                # Tentar converter valor
                try:
                    valor = Decimal(valor_str)
                except:
                    valor = Decimal('0.00')
                
                # Verificar se é um valor válido (maior que 0 e menor que 100000)
                if valor > 0 and valor < 100000:
                    categoria = OCRService._infer_category(descricao)
                    
                    return {
                        'descricao': descricao,
                        'categoria': categoria,
                        'valor_parcela': valor,
                        'tipo': 'normal',
                        'parcela_atual': 1,
                        'total_parcelas': 1,
                        'mapping_status': 'NEW',
                        'matched_gasto_pai_id': None
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao parsear linha: {e}")
            return None
    
    @staticmethod
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
    
    @staticmethod
    def match_with_existing_transactions(transactions):
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
