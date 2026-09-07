"""
Rotas para geração de relatórios em PDF
"""
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from database.db import execute_query
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/expenses-pdf', methods=['GET'])
def generate_expenses_pdf():
    """
    Gera um relatório PDF de gastos
    
    Query params:
        - month: Mês (1-12, default: mês atual)
        - year: Ano (default: ano atual)
        - card: Filtro por cartão (opcional)
        - category: Filtro por categoria (opcional)
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        card = request.args.get('card')
        category = request.args.get('category')
        
        # Usar mês atual se não fornecido
        if month is None or year is None:
            now = datetime.now()
            month = now.month if month is None else month
            year = now.year if year is None else year
        
        # Buscar gastos do período
        query = """
            SELECT * FROM gastos 
            WHERE EXTRACT(MONTH FROM data) = %s 
            AND EXTRACT(YEAR FROM data) = %s
        """
        params = [month, year]
        
        if card:
            query += " AND cartao_nome = %s"
            params.append(card)
        
        if category:
            query += " AND categoria = %s"
            params.append(category)
        
        query += " ORDER BY data ASC"
        
        expenses = execute_query(query, tuple(params), fetch=True)
        
        if not expenses:
            expenses = []
        
        # Gerar PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=20
        )
        
        # Construir conteúdo do PDF
        story = []
        
        # Título
        month_name = datetime(year, month, 1).strftime('%B')
        title = f"Relatório de Gastos - {month_name} {year}"
        story.append(Paragraph(title, title_style))
        
        # Subtítulo com filtros
        subtitle_parts = []
        if card:
            subtitle_parts.append(f"Cartão: {card}")
        if category:
            subtitle_parts.append(f"Categoria: {category}")
        
        if subtitle_parts:
            subtitle = " | ".join(subtitle_parts)
            story.append(Paragraph(subtitle, subtitle_style))
        
        story.append(Spacer(1, 0.2 * inch))
        
        # Tabela de gastos
        table_data = [
            ['Data', 'Descrição', 'Categoria', 'Cartão', 'Tipo', 'Parcela', 'Valor']
        ]
        
        total_value = 0.0
        
        for expense in expenses:
            data_str = expense['data'].strftime('%d/%m/%Y') if expense.get('data') else '-'
            descricao = expense.get('descricao', '-')
            categoria = expense.get('categoria', '-')
            cartao = expense.get('cartao_nome', '-')
            tipo = expense.get('tipo', '-')
            
            # Formatar parcela
            parcela_atual = expense.get('parcela_atual', 1)
            total_parcelas = expense.get('total_parcelas', 1)
            
            if tipo == 'parcelado':
                parcela_str = f"{parcela_atual}/{total_parcelas}"
            else:
                parcela_str = '-'
            
            valor_str = f"R$ {expense['valor_parcela']:.2f}"
            total_value += float(expense['valor_parcela'])
            
            table_data.append([
                data_str,
                descricao,
                categoria,
                cartao,
                tipo,
                parcela_str,
                valor_str
            ])
        
        # Adicionar linha de total
        table_data.append([
            '',
            '',
            '',
            '',
            'TOTAL',
            '',
            f"R$ {total_value:.2f}"
        ])
        
        # Criar tabela
        table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1.0*inch])
        
        # Estilizar tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
        ]))
        
        story.append(table)
        
        # Construir PDF
        doc.build(story)
        
        # Retornar PDF
        pdf_buffer.seek(0)
        
        filename = f"relatorio_gastos_{month}_{year}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        return jsonify({'error': str(e)}), 500
