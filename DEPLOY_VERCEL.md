# Deploy da BFF na Vercel

Guia completo para hospedar a API FinTrack BFF na plataforma Vercel.

## 📋 Pré-requisitos

- Conta no GitHub (para deploy automático)
- Conta na Vercel (gratuita em vercel.com)
- Banco de dados PostgreSQL (recomendado: Supabase gratuito)

## 🚀 Passo a Passo

### 1. Preparar o Repositório GitHub

```bash
# Adicionar arquivos ao git
cd bff
git add .
git commit -m "Adaptar BFF para deploy na Vercel"

# Push para GitHub
git push origin main
```

### 2. Configurar Banco de Dados (Supabase Recomendado)

#### Opção A: Supabase (Gratuito)

1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita
2. Crie um novo projeto
3. Vá em Settings > Database
4. Copie a connection string:

```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
```

5. Execute o script SQL do FinTrack no Supabase SQL Editor:
   - Abra o SQL Editor no Supabase
   - Copie e execute o conteúdo de `../banco de dados/setup_tables.sql`

#### Opção B: Outro PostgreSQL

Use qualquer serviço PostgreSQL e obtenha a connection string.

### 3. Deploy na Vercel

#### Via Interface Web (Recomendado)

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em "Add New" > "Project"
3. Importe o repositório GitHub do projeto
4. Configure as variáveis de ambiente:

#### Variáveis de Ambiente Necessárias

No painel da Vercel, vá em Settings > Environment Variables e adicione:

```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
```

Ou as variáveis individuais:

```
DB_HOST=db.[PROJECT].supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[seu-password]
OCR_ENABLED=True
```

5. Clique em "Deploy"

#### Via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login na Vercel
vercel login

# Deploy
cd bff
vercel
```

Siga as instruções no terminal.

### 4. Configurar o Frontend

Após o deploy, você receberá uma URL da Vercel (ex: `https://fintrack-bff.vercel.app`).

Atualize o arquivo `front/expense.service.ts`:

```typescript
// Antes
private apiUrl = 'http://localhost:5000/api/v1';

// Depois
private apiUrl = 'https://sua-url-vercel.vercel.app/api/v1';
```

Faça o mesmo em `front/upload.service.ts` e `front/analytics.service.ts`.

## 🏗️ Estrutura do Projeto para Vercel

```
bff/
├── api/
│   └── index.py              # Entry point para Vercel
├── routes/                   # Rotas da API
├── services/                 # Lógica de negócio
├── schemas/                  # Schemas Pydantic
├── database/                 # Conexão com banco
├── config.py                 # Configurações
├── requirements.txt          # Dependências
├── vercel.json              # Configuração Vercel
└── .env.vercel.example      # Exemplo de variáveis de ambiente
```

## 🔧 Configuração do vercel.json

O arquivo `vercel.json` instrui a Vercel sobre como tratar o projeto:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.9"
  }
}
```

## 🧪 Testar Localmente (Simulando Vercel)

```bash
cd bff

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente local
copy .env.example .env
# Edite .env com suas credenciais locais

# Testar localmente (não usa serverless)
python app.py
```

## 📊 Monitoramento e Logs

### Ver Logs na Vercel

1. Acesse o projeto na Vercel
2. Vá em "Deployments"
3. Clique no deployment mais recente
4. Vá em "Function Logs" para ver os logs das requisições

### Debug de Erros

Se tiver erros, verifique:
1. Logs da Vercel (Function Logs)
2. Variáveis de ambiente configuradas corretamente
3. Connection string do banco de dados
4. Versão do Python (3.9+)

## 🔄 Deploy Automático

Com o projeto conectado ao GitHub, a Vercel fará deploy automático sempre que você:

1. Fizer push para a branch principal
2. Abrir um Pull Request (deploy de preview)

## 🌐 Domínio Personalizado (Opcional)

1. Na Vercel, vá em Settings > Domains
2. Adicione seu domínio personalizado
3. Configure o DNS conforme instruções da Vercel

## 🚨 Limitações da Vercel

### Limites do Plano Gratuito

- 100GB bandwidth por mês
- 6 funções serverless simultâneas
- 10 segundos de timeout por função
- 1GB de tamanho de função

### Considerações para o FinTrack

- **Timeout**: Operações OCR podem demorar mais de 10s
- **Upload**: Arquivos grandes podem exceder limites
- **Banco**: Use Supabase gratuito para evitar custos

### Soluções para Limitações

1. **OCR Timeout**: Processar OCR em partes ou usar serviço externo
2. **Upload**: Limitar tamanho de arquivos no frontend
3. **Caching**: Implementar cache para reduzir chamadas ao banco

## 📈 Escalabilidade

Para escalar além dos limites gratuitos:

1. **Vercel Pro**: Aumenta limites de funções e bandwidth
2. **Banco Dedicado**: Use plano pago do Supabase ou outro serviço
3. **CDN**: A Vercel já inclui CDN global

## 🔒 Segurança

### Boas Práticas

1. Nunca commitar `.env` no GitHub
2. Usar variáveis de ambiente da Vercel
3. Senhas fortes para banco de dados
4. Habilitar HTTPS (a Vercel faz automaticamente)
5. Rate limiting para prevenir abuso

### Variáveis Sensíveis

Configure na Vercel, nunca no código:
- `DB_PASSWORD`
- `DATABASE_URL`
- Chaves de API externas

## 🐛 Troubleshooting

### Erro: "Module not found"

**Solução**: Verifique se `requirements.txt` está completo e todas as dependências estão listadas.

### Erro: "Connection timeout"

**Solução**: Verifique a connection string do banco e se o banco permite conexões externas.

### Erro: "Function execution timeout"

**Solução**: Otimize o código ou considere dividir operações longas.

### Erro: "Permission denied"

**Solução**: Verifique permissões no banco de dados e variáveis de ambiente.

## 📚 Recursos Adicionais

- [Documentação Vercel Python](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Documentação Supabase](https://supabase.com/docs)
- [Limites Vercel](https://vercel.com/docs/platform/limits)

## 🎯 Checklist de Deploy

- [ ] Repositório no GitHub configurado
- [ ] Banco de dados PostgreSQL criado e configurado
- [ ] Script SQL executado no banco
- [ ] Variáveis de ambiente configuradas na Vercel
- [ ] `vercel.json` criado e configurado
- [ ] `requirements.txt` completo
- [ ] Deploy inicial realizado com sucesso
- [ ] Frontend atualizado com nova URL da API
- [ ] Testes de integração realizados
- [ ] Monitoramento de logs configurado

---

**Sua API FinTrack BFF está pronta para produção na Vercel! 🚀**
