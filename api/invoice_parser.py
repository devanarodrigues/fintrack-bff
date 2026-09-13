"""
Módulo para extrair dados de faturas de cartão de crédito (Itaú e Mercado Pago)
Adaptado de p.py para funcionar como módulo na API Flask
"""
import re
import unicodedata
from io import BytesIO
from typing import Dict, List
import pdfplumber


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e espaços extras"""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip()
def processar_fatura_pdf(arquivo_bytes: bytes, year: int = None, month: int = None) -> Dict:
    """
    Processa uma fatura em PDF (recebida como bytes)
    Retorna um dicionário com os dados extraídos

    Args:
        arquivo_bytes: Conteúdo do arquivo PDF em bytes
        year: Ano da fatura (para completar as datas no formato DD/MM)
        month: Mês da fatura (para garantir que as datas usem o mês correto)

    Returns:
        Dict contendo:
        - success: bool
        - tipo_fatura: str (MERCADO_PAGO ou ITAU)
        - total_lancamentos: int
        - movimentacoes: List[Dict]
        - erro: str (se houver erro)
    """
    try:
        # Abrir PDF a partir dos bytes
        pdf_file = BytesIO(arquivo_bytes)
        
        # Extrair texto do PDF
        texto_completo = ""
        with pdfplumber.open(pdf_file) as pdf:
            for pagina in pdf.pages:
                texto_pag = pagina.extract_text(layout=False)
                if texto_pag:
                    texto_completo += "\n" + texto_pag

        if not texto_completo.strip():
            return {
                "success": False,
                "erro": "Nenhum texto foi extraído do PDF. Verifique se o arquivo é válido."
            }

        texto_norm = normalizar_texto(texto_completo).upper()

        # Detecta o tipo de fatura
        if "CARTAO VISA [************5105]" in texto_norm or "PARCELE A FATURA DO SEU CARTAO DE CREDITO MERCADO PAGO" in texto_norm:
            tipo_fatura = "MERCADO_PAGO"
        else:
            tipo_fatura = "ITAU"

        # Se não foi fornecido o ano, usar o ano atual
        if year is None:
            from datetime import datetime
            year = datetime.now().year

        # Se não foi fornecido o mês, usar o mês atual
        if month is None:
            from datetime import datetime
            month = datetime.now().month

        # RegEx base para capturar data, estabelecimento com/sem parcela colada e valor
        padrao_transacao = re.compile(
            r"(\d{2}/\d{2}|\d{2}\s+[A-Za-z]{3})\s+([A-Za-z0-9\*\.\s\-\/\&\(\)]+?)(?:\s+(\d{2}/\d{2}))?\s+(-?\s*(?:R\$\s*)?\d{1,3}(?:\.\d{3})*,\d{2})",
            re.IGNORECASE
        )

        lines = texto_completo.split("\n")
        bloco_util = []
        dentro = False

        for line in lines:
            line_norm = normalizar_texto(line).upper()

            if tipo_fatura == "MERCADO_PAGO":
                if "CARTAO VISA [************5105]" in line_norm:
                    dentro = True
                    continue
                if "PARCELE A FATURA DO SEU CARTAO DE CREDITO MERCADO PAGO" in line_norm and dentro:
                    break
            else:  # ITAU
                if "LANCAMENTOS: COMPRAS E SAQUES" in line_norm or "LANCAMENTOS DE COMPRAS" in line_norm:
                    dentro = True
                    continue
                if ("LIMITES DE CREDITO" in line_norm or "COMPRAS PARCELADAS - PROXIMAS" in line_norm) and dentro:
                    break

            if dentro:
                bloco_util.append(line.strip())

        texto_filtrado = "\n".join(bloco_util)
        matches = padrao_transacao.findall(texto_filtrado)

        movimentacoes = []
        vistos = set()

        for match in matches:
            dt, estabelecimento, parcela_padrao, valor = match
            estab_limpo = normalizar_texto(estabelecimento)

            # Ignora pagamentos de fatura
            if "PAGAMENTO VIA CONTA" in estab_limpo.upper() or "PAGAMENTO DE FATURA" in estab_limpo.upper():
                continue

            parcela_str = "-"

            # 1. Tratamento para padrão Mercado Pago: "Parcela X de Y" contido no nome
            match_mp_parc = re.search(r"\bPARCELA\s+(\d{1,2})\s+DE\s+(\d{1,2})\b", estab_limpo, re.IGNORECASE)
            if match_mp_parc:
                p_atual, p_total = match_mp_parc.groups()
                parcela_str = f"{int(p_atual):02d}/{int(p_total):02d}"
                # Remove "Parcela X de Y" do nome do estabelecimento
                estab_limpo = re.sub(r"\s*\bPARCELA\s+\d{1,2}\s+DE\s+\d{1,2}\b", "", estab_limpo, flags=re.IGNORECASE).strip()

            # 2. Tratamento para padrão Itaú ou formatos comuns: "XX/YY"
            elif parcela_padrao:
                parcela_str = parcela_padrao

            # Limpeza de resíduos de cidades/categorias no Itaú
            if tipo_fatura == "ITAU":
                estab_limpo = re.sub(
                    r"\s+(OUTROS|VESTUARIO|CASA|TRANSPORTE|SUPERMERCADO|RESTAURANTE|SAUDE|LAZER|SAO PAULO|OSASCO|COTIA|FRANCA|SOROCABA|HORTOLANDIA|POA|FERRAZ DE VAS|SALTO DE PIRA)\b.*",
                    "", estab_limpo, flags=re.IGNORECASE
                ).strip()

            valor_limpo = valor.replace("R$", "").replace(" ", "").strip()

            # Evitar duplicatas
            chave_unica = f"{dt}|{estab_limpo}|{parcela_str}|{valor_limpo}"
            if chave_unica not in vistos:
                vistos.add(chave_unica)

                # Usar o mês/ano informado para todas as datas da fatura
                # Isso garante que as transações sejam atribuídas ao mês/ano correto
                try:
                    if dt and '/' in dt:
                        partes = dt.split('/')
                        dia = partes[0].zfill(2)  # Garantir que o dia tenha 2 dígitos
                        # Usar o mês/ano informado em vez do mês extraído do PDF
                        data_iso = f"{year}-{str(month).zfill(2)}-{dia}"
                    else:
                        # Se não tiver formato de data, usar o primeiro dia do mês/ano informado
                        data_iso = f"{year}-{str(month).zfill(2)}-01"
                except:
                    # Fallback: usar o primeiro dia do mês/ano informado
                    data_iso = f"{year}-{str(month).zfill(2)}-01"

                movimentacoes.append({
                    "data": data_iso,
                    "estabelecimento": estab_limpo,
                    "parcela": parcela_str,
                    "valor": valor_limpo
                })

        return {
            "success": True,
            "tipo_fatura": tipo_fatura,
            "total_lancamentos": len(movimentacoes),
            "movimentacoes": movimentacoes
        }

    except Exception as e:
        return {
            "success": False,
            "erro": f"Erro ao processar PDF: {str(e)}"
        }
