# FinTrack BFF - Backend for Frontend

API Flask para gerenciamento financeiro com suporte a OCR de faturas e parcelamento de compras.

**Agora com suporte para deploy na Vercel! 🚀**

## 📋 Visão Geral

O BFF (Backend for Frontend) é uma API Python construída com Flask que serve como intermediário entre o frontend Angular e o banco de dados PostgreSQL. Ele é responsável por:

- Gerenciar operações CRUD de gastos
- Processar OCR de faturas de cartão de crédito
- Calcular métricas do dashboard
- Gerar relatórios em PDF
- Projetar parcelas futuras na linha do tempo

## 🌟 Modos de Execução

### 1. Desenvolvimento Local (Tradicional)

```bash
cd bff
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### 2. Deploy na Vercel (Serverless) ✨ NOVO

```bash
# Push para GitHub
git add .
git commit -m "Deploy Vercel"
git push origin main

# Deploy via Vercel CLI ou interface web
# Veja DEPLOY_VERCEL.md para instruções detalhadas
```

**Vantagens do deploy na Vercel:**
- ✅ Servidor serverless (paga apenas pelo uso)
- ✅ Deploy automático via GitHub
- ✅ HTTPS automático
- ✅ CDN global
- ✅ Domínio gratuito
- ✅ Logs e monitoramento integrados

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
cd bff

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

Siga as instruções em `../banco de dados/config_database.txt` para configurar o PostgreSQL.

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar o arquivo .env com suas credenciais
notepad .env
```

Preencha as seguintes variáveis:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fintrack
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

### 4. Iniciar a API

```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
bff/
├── app.py                    # Aplicação principal Flask
├── config.py                 # Configurações e variáveis de ambiente
├── requirements.txt          # Dependências Python
├── .env.example             # Exemplo de configuração
├── database/                # Camada de banco de dados
│   └── db.py                # Conexão e operações PostgreSQL
├── routes/                  # Rotas da API
│   ├── expenses.py          # CRUD de gastos
│   ├── dashboard.py         # Dashboard e KPIs
│   ├── upload.py            # Upload e OCR de faturas
│   ├── analytics.py         # Analytics e timeline
│   └── reports.py           # Relatórios PDF
├── services/                # Lógica de negócio
│   ├── expense_service.py   # Serviço de gastos
│   ├── dashboard_service.py # Serviço de dashboard
│   └── ocr_service.py       # Serviço OCR
├── schemas/                 # Schemas Pydantic
│   ├── expense.py           # Schema de gastos
│   ├── dashboard.py         # Schema de dashboard
│   └── upload.py            # Schema de upload
└── docs/                    # Documentação
    ├── spec/001.md          # Especificação funcional
    ├── plan/001.md          # Plano de arquitetura
    └── task/001.md          # Lista de tarefas
```

## 🔌 Endpoints da API

### Gastos

#### Listar Gastos
```http
GET /api/v1/expenses?page=1&limit=10&search=&category=&card=&month=9&year=2026
```

**Query Params:**
- `page`: Número da página (default: 1)
- `limit`: Itens por página (default: 10)
- `search`: Busca por descrição
- `category`: Filtro por categoria
- `card`: Filtro por cartão
- `month`: Filtro por mês (1-12)
- `year`: Filtro por ano

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "gasto_pai_id": "uuid",
      "data": "2026-09-06",
      "cartao_nome": "Nubank",
      "categoria": "Alimentação",
      "descricao": "Supermercado",
      "valor_parcela": 450.00,
      "tipo": "normal",
      "parcela_atual": 1,
      "total_parcelas": 1,
      "origem": "manual"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### Criar Gasto
```http
POST /api/v1/expenses
Content-Type: application/json

{
  "data": "2026-09-06",
  "cartao_nome": "Nubank",
  "categoria": "Alimentação",
  "descricao": "Supermercado",
  "valor_parcela": 450.00,
  "tipo": "normal",
  "parcela_atual": 1,
  "total_parcelas": 1,
  "origem": "manual"
}
```

#### Atualizar Gasto
```http
PUT /api/v1/expenses/:id
Content-Type: application/json

{
  "descricao": "Supermercado Semanal",
  "valor_parcela": 500.00
}
```

#### Deletar Gasto
```http
DELETE /api/v1/expenses/:id
```

#### Buscar Parcelas
```http
GET /api/v1/expenses/:id/installments
```

### Dashboard

#### Resumo do Dashboard
```http
GET /api/v1/dashboard/summary?month=9&year=2026
```

**Response:**
```json
{
  "total_month": 1500.00,
  "top_card": "Nubank",
  "top_card_pct": 65.5,
  "biggest_expense": {
    "id": "uuid",
    "descricao": "Notebook",
    "valor_parcela": 500.00,
    "data": "2026-09-01",
    "cartao_nome": "Nubank",
    "categoria": "Eletrônicos"
  },
  "future_installments": 2000.00,
  "fixed_expenses": 500.00,
  "next_month_forecast": 1500.00,
  "total_expenses_count": 15,
  "active_installments_count": 3
}
```

#### Resumo por Cartão
```http
GET /api/v1/dashboard/cards?month=9&year=2026
```

#### Resumo por Categoria
```http
GET /api/v1/dashboard/categories?month=9&year=2026
```

### Upload de Faturas

#### Upload de PDF
```http
POST /api/v1/invoices/upload
Content-Type: multipart/form-data

file: [arquivo PDF]
card: Nubank
month: 9
year: 2026
```

**Response:**
```json
{
  "processing_id": "proc-abc123",
  "cartao_identificado": "Nubank",
  "transactions": [
    {
      "temp_id": "tmp-001",
      "descricao": "Notebook",
      "categoria": "Eletrônicos",
      "valor_parcela": 250.00,
      "tipo": "parcelado",
      "parcela_atual": 3,
      "total_parcelas": 10,
      "mapping_status": "MATCHED",
      "matched_gasto_pai_id": "uuid"
    }
  ],
  "total_count": 1,
  "matched_count": 1,
  "new_count": 0
}
```

#### Confirmar Transações
```http
POST /api/v1/invoices/confirm
Content-Type: application/json

{
  "processing_id": "proc-abc123",
  "transactions": [
    {
      "data": "2026-09-06",
      "cartao_nome": "Nubank",
      "categoria": "Eletrônicos",
      "descricao": "Notebook",
      "valor_parcela": 250.00,
      "tipo": "parcelado",
      "parcela_atual": 3,
      "total_parcelas": 10,
      "matched_gasto_pai_id": "uuid"
    }
  ]
}
```

### Analytics

#### Linha do Tempo
```http
GET /api/v1/analytics/timeline?months=6
```

**Response:**
```json
{
  "items": [
    {
      "month": 9,
      "year": 2026,
      "month_name": "September",
      "total": 1500.00,
      "installments": [
        {
          "id": "uuid",
          "descricao": "Notebook",
          "valor_parcela": 250.00,
          "parcela_atual": 3,
          "total_parcelas": 10,
          "cartao_nome": "Nubank"
        }
      ]
    }
  ]
}
```

#### Tendência Mensal
```http
GET /api/v1/analytics/monthly-trend?months=12
```

### Relatórios

#### Gerar PDF
```http
GET /api/v1/reports/expenses-pdf?month=9&year=2026&card=Nubank
```

Retorna um arquivo PDF para download.

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| DB_HOST | Host do PostgreSQL | localhost |
| DB_PORT | Porta do PostgreSQL | 5432 |
| DB_NAME | Nome do banco | fintrack |
| DB_USER | Usuário do PostgreSQL | postgres |
| DB_PASSWORD | Senha do PostgreSQL | - |
| API_HOST | Host da API | 0.0.0.0 |
| API_PORT | Porta da API | 5000 |
| DEBUG | Modo debug | True |
| UPLOAD_FOLDER | Pasta de uploads | ./uploads |
| OCR_ENABLED | Habilitar OCR | True |

## 🧪 Testes

### Testar Conexão com Banco
```python
from database.db import get_db_connection

try:
    conn = get_db_connection()
    print("✅ Conexão OK")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

### Testar Endpoints
```bash
# Health check
curl http://localhost:5000/

# Listar gastos
curl http://localhost:5000/api/v1/expenses

# Dashboard
curl http://localhost:5000/api/v1/dashboard/summary
```

## 🛠️ Troubleshooting

### Erro: "Conexão com banco de dados falhou"
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no .env
- Teste: `psql -U postgres -d fintrack`

### Erro: "Extensão uuid-ossp não existe"
- Verifique a versão do PostgreSQL (deve ser 12+)
- Habilite: `CREATE EXTENSION "uuid-ossp";`

### Erro: "Módulo não encontrado"
- Ative o venv: `venv\Scripts\activate`
- Reinstale: `pip install -r requirements.txt`

### OCR não funciona
- Verifique se pdfplumber está instalado
- Confirme que OCR_ENABLED=True no .env
- Teste com um PDF simples

## 📚 Serviços

### ExpenseService
Gerencia operações CRUD de gastos com suporte a parcelamento.

### DashboardService
Calcula métricas e KPIs para o dashboard.

### OCRService
Processa PDFs de faturas usando pdfplumber para extrair transações automaticamente.

## 🔐 Segurança

- ⚠️ Nunca commitar o arquivo .env
- ⚠️ Use senhas fortes
- ⚠️ Em produção, desabilite DEBUG
- ⚠️ Configure firewall para o banco

## 📝 Desenvolvimento

### Adicionar Novo Endpoint

1. Criar rota em `routes/`
2. Criar serviço em `services/`
3. Criar schema em `schemas/`
4. Registrar blueprint em `app.py`

### Estrutura de Rota

```python
from flask import Blueprint, request, jsonify

bp = Blueprint('nome', __name__)

@bp.route('/endpoint', methods=['GET'])
def endpoint():
    try:
        # Lógica
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 📖 Documentação Relacionada

- [README Principal](../README.md) - Visão geral do projeto
- [Configuração do Banco](../banco de dados/config_database.txt) - Guia PostgreSQL
- [Especificação Funcional](docs/spec/001.md) - Requisitos detalhados
- [Plano de Arquitetura](docs/plan/001.md) - Decisões técnicas

---

**Desenvolvido com Flask + PostgreSQL + pdfplumber**
