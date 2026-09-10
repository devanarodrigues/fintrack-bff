"""
Schemas Pydantic para validação de dados do dashboard
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class DashboardSummary(BaseModel):
    """Schema para resumo do dashboard"""
    total_month: Decimal
    top_card: str
    top_card_pct: float
    biggest_expense: Optional[dict] = None
    future_installments: Decimal
    fixed_expenses: Decimal
    next_month_forecast: Decimal
    total_expenses_count: int
    active_installments_count: int

class CardSummary(BaseModel):
    """Schema para resumo por cartão"""
    card_name: str
    total_spent: Decimal
    transaction_count: int
    percentage: float

class CategorySummary(BaseModel):
    """Schema para resumo por categoria"""
    category: str
    total_spent: Decimal
    transaction_count: int
    percentage: float
