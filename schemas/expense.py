"""
Schemas Pydantic para validação de dados de gastos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date
from decimal import Decimal

class ExpenseBase(BaseModel):
    """Schema base para gastos"""
    data: date
    cartao_nome: str
    categoria: str
    descricao: str
    valor_parcela: Decimal = Field(..., gt=0, description="Valor da parcela deve ser positivo")
    tipo: str = Field(..., regex="^(normal|parcelado|fixo)$")
    parcela_atual: int = Field(default=1, ge=1)
    total_parcelas: int = Field(default=1, ge=1)
    origem: str = Field(..., regex="^(manual|fatura)$")
    observacao: Optional[str] = None
    
    @validator('parcela_atual', 'total_parcelas')
    def validate_installments(cls, v, values):
        """Valida campos de parcelamento"""
        if 'tipo' in values and values['tipo'] == 'parcelado':
            if v < 1:
                raise ValueError('Parcela deve ser maior que 0')
        return v

class ExpenseCreate(ExpenseBase):
    """Schema para criação de gastos"""
    cartao_id: Optional[str] = None
    gasto_pai_id: Optional[str] = None

class ExpenseUpdate(BaseModel):
    """Schema para atualização de gastos"""
    data: Optional[date] = None
    cartao_nome: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor_parcela: Optional[Decimal] = None
    tipo: Optional[str] = None
    parcela_atual: Optional[int] = None
    total_parcelas: Optional[int] = None
    observacao: Optional[str] = None

class ExpenseResponse(BaseModel):
    """Schema para resposta de gastos"""
    id: str
    gasto_pai_id: Optional[str] = None
    data: str
    cartao_id: Optional[str] = None
    cartao_nome: str
    categoria: str
    descricao: str
    valor_parcela: Decimal
    tipo: str
    parcela_atual: int
    total_parcelas: int
    origem: str
    observacao: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExpenseListResponse(BaseModel):
    """Schema para listagem de gastos com paginação"""
    items: List[ExpenseResponse]
    total: int
    page: int
    limit: int
