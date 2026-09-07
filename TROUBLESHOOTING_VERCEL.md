# 🔧 Troubleshooting - Erro 500 na Vercel

## ❌ Erro: 500 INTERNAL_SERVER_ERROR

Se você está recebendo este erro ao fazer deploy na Vercel, siga estes passos para diagnosticar e corrigir o problema.

## 🚀 Passo 1: Testar Versão Simplificada

### 1.1 Renomear arquivo de configuração temporariamente
```bash
cd bff
# Backup do arquivo original
copy vercel.json vercel.json.backup
# Usar versão de teste
copy vercel.test.json vercel.json
```

### 1.2 Modificar o entry point temporariamente
```bash
# Backup do arquivo original
copy api\index.py api\index.py.backup
# Usar versão de teste
copy api\test.py api\index.py
```

### 1.3 Fazer deploy da versão de teste
```bash
git add .
git commit -m "Test: Deploy versão simplificada"
git push origin main
```

### 1.4 Verificar se a versão de teste funciona
- Acesse a URL da Vercel
- Deve retornar: `{"status":"healthy","service":"FinTrack BFF Test",...}`

### 1.5 Se funcionar, o problema está nas importações/rotas
- Volte para a versão original
- Siga os passos abaixo

## 🔍 Passo 2: Verificar Logs na Vercel

### 2.1 Acessar Logs
1. Vá ao painel da Vercel
2. Clique no seu projeto
3. Vá em "Deployments"
4. Clique no deployment mais recente
5. Vá em "Function Logs"

### 2.2 Procurar erros específicos
 procure por mensagens como:
- `ImportError: No module named 'flask'`
- `ModuleNotFoundError: No module named 'routes'`
- `Database connection failed`
- `Timeout error`

## 🛠️ Passo 3: Corrigir Problemas Comuns

### Problema 1: Importações Falhando

**Sintoma:** `ModuleNotFoundError` nos logs

**Solução:**
```python
# No api/index.py, verifique se o path está correto
import sys
import os

# Deve adicionar o diretório pai ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
```

### Problema 2: Dependências Faltando

**Sintoma:** `ImportError: No module named 'flask'`

**Solução:**
1. Verifique se `requirements.txt` está na raiz do projeto
2. Verifique se todas as dependências estão listadas:
```txt
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pdfplumber==0.10.3
reportlab==4.0.7
pydantic==2.5.0
colorlog==6.8.0
```

### Problema 3: Banco de Dados Não Conecta

**Sintoma:** Erros de conexão PostgreSQL nos logs

**Solução:**
1. Verifique variáveis de ambiente na Vercel:
   - Vá em Settings > Environment Variables
   - Confirme que `DATABASE_URL` ou variáveis individuais estão configuradas
2. Teste a connection string:
```bash
# Teste local
psql "postgresql://user:password@host:port/database"
```

### Problema 4: Timeout de Função

**Sintoma:** `Function execution timeout` nos logs

**Solução:**
1. Operações OCR podem demorar mais de 10s (limite gratuito Vercel)
2. Considere:
   - Limitar tamanho de arquivos no frontend
   - Processar OCR em partes
   - Usar serviço externo para OCR

### Problema 5: Permissões de Arquivo

**Sintoma:** `Permission denied` ao tentar salvar arquivos

**Solução:**
```python
# Use sempre /tmp na Vercel
UPLOAD_FOLDER = '/tmp'  # Vercel usa /tmp
```

## 🧪 Passo 4: Debug com Endpoint Debug

O código atual inclui um endpoint `/debug` que mostra informações do ambiente:

```bash
# Após fazer deploy, acesse
curl https://sua-url.vercel.app/debug
```

Isso mostrará:
- Versão do Python
- Diretório de trabalho
- Variáveis de ambiente
- Configuração do Flask

## 🔄 Passo 5: Reverter para Versão de Teste

Se nada funcionar, use a versão de teste:

```bash
cd bff
# Reverter arquivos
del api\index.py
copy api\test.py api\index.py
del vercel.json
copy vercel.test.json vercel.json

# Commit e deploy
git add .
git commit -m "Revert to test version"
git push origin main
```

## 📊 Passo 6: Verificar Estrutura de Arquivos

A estrutura deve ser exatamente esta:

```
bff/
├── api/
│   ├── index.py          # Entry point principal
│   └── test.py           # Versão de teste
├── routes/               # Rotas da API
│   ├── expenses.py
│   ├── dashboard.py
│   ├── upload.py
│   ├── analytics.py
│   └── reports.py
├── services/             # Lógica de negócio
├── schemas/              # Schemas Pydantic
├── database/             # Conexão com banco
│   └── db.py
├── config.py             # Configurações
├── requirements.txt      # Dependências (na raiz!)
├── vercel.json          # Configuração Vercel (na raiz!)
└── app.py               # Versão local (não usada na Vercel)
```

## 🔐 Passo 7: Verificar Variáveis de Ambiente

Na Vercel, vá em Settings > Environment Variables e confirme:

```
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

Ou variáveis individuais:
```
DB_HOST=db.[project].supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[seu-password]
OCR_ENABLED=True
```

## 📝 Passo 8: Logs Detalhados

Adicione mais logging temporariamente:

```python
# No api/index.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Adicione logs em pontos críticos
@app.route('/')
def health_check():
    logging.info("Health check endpoint called")
    return jsonify({'status': 'healthy'})
```

## 🎯 Passo 9: Checklist de Diagnóstico

- [ ] Versão de teste (`api/test.py`) funciona?
- [ ] `requirements.txt` está na raiz do projeto?
- [ ] Todas as dependências estão listadas?
- [ ] Variáveis de ambiente configuradas na Vercel?
- [ ] Connection string do banco está correta?
- [ ] Estrutura de pastas está correta?
- [ ] `vercel.json` está na raiz do projeto?
- [ ] Logs mostram algum erro específico?

## 🆘 Passo 10: Pedir Ajuda

Se nada funcionar:

1. **Cole os logs da Vercel** (Function Logs)
2. **Cole a estrutura de arquivos** (`tree /F` no Windows)
3. **Cole o conteúdo do vercel.json**
4. **Cole as variáveis de ambiente** (sem senhas)

## 🔄 Restaurar Versão Original

Após diagnosticar, restaure a versão original:

```bash
cd bff
# Restaurar arquivos
del api\index.py
copy api\index.py.backup api\index.py
del vercel.json
copy vercel.json.backup vercel.json

# Commit e deploy
git add .
git commit -m "Restore original version with fixes"
git push origin main
```

## 📚 Recursos Adicionais

- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Vercel Function Logs](https://vercel.com/docs/deployments/overview#logs)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)

---

**Se ainda tiver problemas, compartilhe os logs da Vercel para análise mais detalhada.**
