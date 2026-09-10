"""
Schemas Pydantic para validação de dados de upload
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

class ExtractedTransaction(BaseModel):
    """Schema para transação extraída do PDF"""
    temp_id: str
    descricao: str
    categoria: str
    valor_parcela: Decimal
    tipo: str
    parcela_atual: int
    total_parcelas: int
    mapping_status: str = Field(..., regex="^(MATCHED|NEW|PENDING)$")
    matched_gasto_pai_id: Optional[str] = None

class UploadResponse(BaseModel):
    """Schema para resposta do upload"""
    processing_id: str
    cartao_identificado: str
    transactions: List[ExtractedTransaction]
    total_count: int
    matched_count: int
    new_count: int

class UploadStatus(BaseModel):
    """Schema para status do processamento"""
    processing_id: str
    phase: str
    progress: int
    message: Optional[str] = None
    count: Optional[int] = None
