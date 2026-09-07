"""
Módulo para extrair dados de faturas de cartão de crédito (Itaú e Mercado Pago)
Adaptado de p.py para funcionar como módulo na API Flask
"""
import re
import unicodedata
from io import BytesIO
from typing import Dict, List, Tuple, Optional
import pdfplumber


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e espaços extras"""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip()


def detectar_tipo_fatura(texto_norm: str) -> str:
    """Detecta se é fatura do Mercado Pago ou Itaú"""
    if "CARTAO VISA [************5105]" in texto_norm or "PARCELE A FATURA DO SEU CARTAO DE CREDITO MERCADO PAGO" in texto_norm:
        return "MERCADO_PAGO"
    return "ITAU"


def extrair_bloco_transacoes(linhas: List[str], tipo_fatura: str) -> str:
    """Extrai o bloco de transações do texto da fatura"""
    bloco_util = []
    dentro = False

    for line in linhas:
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

    return "\n".join(bloco_util)


def limpar_estabelecimento(estab_limpo: str, tipo_fatura: str, match_mp_parc) -> str:
    """Remove informações de parcela e limpeza de resíduos do estabelecimento"""
    # Remove "Parcela X de Y" do nome do estabelecimento
    if match_mp_parc:
        estab_limpo = re.sub(
            r"\s*\bPARCELA\s+\d{1,2}\s+DE\s+\d{1,2}\b",
            "",
            estab_limpo,
            flags=re.IGNORECASE
        ).strip()

    # Limpeza de resíduos de cidades/categorias no Itaú
    if tipo_fatura == "ITAU":
        estab_limpo = re.sub(
            r"\s+(OUTROS|VESTUARIO|CASA|TRANSPORTE|SUPERMERCADO|RESTAURANTE|SAUDE|LAZER|SAO PAULO|OSASCO|COTIA|FRANCA|SOROCABA|HORTOLANDIA|POA|FERRAZ DE VAS|SALTO DE PIRA)\b.*",
            "",
            estab_limpo,
            flags=re.IGNORECASE
        ).strip()

    return estab_limpo


def extrair_transacoes(texto_filtrado: str, tipo_fatura: str) -> List[Dict]:
    """Extrai transações do texto filtrado"""
    # RegEx para capturar data, estabelecimento, parcela e valor
    padrao_transacao = re.compile(
        r"(\d{2}/\d{2}|\d{2}\s+[A-Za-z]{3})\s+([A-Za-z0-9\*\.\s\-\/\&\(\)]+?)(?:\s+(\d{2}/\d{2}))?\s+(-?\s*(?:R\$\s*)?\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE
    )

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

        # 1. Tratamento para padrão Mercado Pago: "Parcela X de Y"
        match_mp_parc = re.search(r"\bPARCELA\s+(\d{1,2})\s+DE\s+(\d{1,2})\b", estab_limpo, re.IGNORECASE)
        if match_mp_parc:
            p_atual, p_total = match_mp_parc.groups()
            parcela_str = f"{int(p_atual):02d}/{int(p_total):02d}"

        # 2. Tratamento para padrão Itaú: "XX/YY"
        elif parcela_padrao:
            parcela_str = parcela_padrao

        # Limpar estabelecimento
        estab_limpo = limpar_estabelecimento(estab_limpo, tipo_fatura, match_mp_parc)

        # Limpar valor
        valor_limpo = valor.replace("R$", "").replace(" ", "").strip()

        # Evitar duplicatas
        chave_unica = f"{dt}|{estab_limpo}|{parcela_str}|{valor_limpo}"
        if chave_unica not in vistos:
            vistos.add(chave_unica)
            movimentacoes.append({
                "data": dt,
                "estabelecimento": estab_limpo,
                "parcela": parcela_str,
                "valor": valor_limpo
            })

    return movimentacoes


def processar_fatura_pdf(arquivo_bytes: bytes) -> Dict:
    """
    Processa uma fatura em PDF (recebida como bytes)
    Retorna um dicionário com os dados extraídos

    Args:
        arquivo_bytes: Conteúdo do arquivo PDF em bytes

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

        # Normalizar e converter para maiúscula para análise
        texto_norm = normalizar_texto(texto_completo).upper()

        # Detectar tipo de fatura
        tipo_fatura = detectar_tipo_fatura(texto_norm)

        # Extrair bloco de transações
        linhas = texto_completo.split("\n")
        texto_filtrado = extrair_bloco_transacoes(linhas, tipo_fatura)

        if not texto_filtrado.strip():
            return {
                "success": False,
                "tipo_fatura": tipo_fatura,
                "erro": "Não foi possível localizar o bloco de transações na fatura."
            }

        # Extrair transações
        movimentacoes = extrair_transacoes(texto_filtrado, tipo_fatura)

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


def formatar_resultado_texto(resultado: Dict) -> str:
    """Formata o resultado como texto para debug/exportação"""
    if not resultado.get("success"):
        return f"ERRO: {resultado.get('erro', 'Erro desconhecido')}"

    linhas = [
        f"=== MOVIMENTACOES ({resultado['tipo_fatura']}) ===",
        "DATA   | ESTABELECIMENTO                            | PARCELA | VALOR",
        "-" * 77
    ]

    for mov in resultado["movimentacoes"]:
        linha = f"{mov['data']:<6} | {mov['estabelecimento']:<42} | {mov['parcela']:^7} | R$ {mov['valor']}"
        linhas.append(linha)

    linhas.append(f"\nTotal de lançamentos encontrados: {resultado['total_lancamentos']}")

    return "\n".join(linhas)
