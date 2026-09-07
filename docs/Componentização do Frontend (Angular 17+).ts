// src/app/core/models/expense.model.ts
export interface Expense {
  id: string;
  gastoPaiId?: string;
  data: string;
  cartaoNome: string;
  categoria: string;
  descricao: string;
  valorParcela: number;
  tipo: 'normal' | 'parcelado' | 'fixo';
  parcelaAtual: number;
  totalParcelas: number;
  origem: 'manual' | 'fatura';
}