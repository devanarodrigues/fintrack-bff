# 🔧 Configuração Manual de Variáveis de Ambiente na Vercel

## ❌ Problema
A integração automática Vercel-Supabase está configurando as variáveis de forma incorreta, causando erros de DNS e conexão.

## ✅ Solução: Configuração Manual

### Passo 1: Remover Integração Vercel-Supabase

1. Acesse o painel da Vercel
2. Vá em **Settings** > **Integrations**
3. Encontre a integração **Supabase**
4. Clique em **Remove** ou desabilite a integração

### Passo 2: Configurar Variáveis de Ambiente Manualmente

No painel da Vercel, vá em **Settings** > **Environment Variables** e adicione as seguintes variáveis:

#### Variáveis Obrigatórias

```
DB_HOST=db.iaqseacthbpcygslldjd.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=nWoyqcyvfDZAuVE1
```

#### Variáveis Opcionais (Recomendadas)

```
DEBUG=false
OCR_ENABLED=true
```

### Passo 3: Fazer Deploy das Alterações

```bash
cd bff
git add .
git commit -m "Fix: Adicionar suporte a DATABASE_URL e configurar para uso manual"
git push origin main
```

### Passo 4: Verificar as Variáveis no Debug

Após o deploy, acesse:
```
https://fintrack-bff.vercel.app/debug
```

Verifique se as variáveis estão corretas no ambiente.

### Passo 5: Testar Conexão

```
https://fintrack-bff.vercel.app/api/v1/expenses
```

Deve retornar dados ou um erro diferente de DNS.

## 🔄 Alternativa: Usar DATABASE_URL Completa

Se preferir usar uma única variável de ambiente, configure apenas:

```
DATABASE_URL=postgresql://postgres:nWoyqcyvfDZAuVE1@db.iaqseacthbpcygslldjd.supabase.co:5432/postgres
```

O código foi atualizado para priorizar `DATABASE_URL` se disponível.

## 🎯 Por Que Configuração Manual é Melhor

1. **Controle Total**: Você tem controle exato sobre as variáveis
2. **Sem Conflitos**: Evita conflitos com integrações automáticas
3. **Debugging Mais Fácil**: Mais fácil identificar problemas
4. **Flexibilidade**: Pode facilmente trocar de banco de dados

## 📋 Checklist

- [ ] Integração Vercel-Supabase removida
- [ ] Variáveis de ambiente configuradas manualmente
- [ ] Deploy realizado com sucesso
- [ ] Debug endpoint mostra variáveis corretas
- [ ] Conexão com banco funciona

## 🆘 Se Ainda Tiver Problemas

### Teste 1: Verificar Variáveis no Debug
Acesse `/debug` e confirme que as variáveis estão presentes.

### Teste 2: Testar Conexão Local
```bash
psql "postgresql://postgres:nWoyqcyvfDZAuVE1@db.iaqseacthbpcygslldjd.supabase.co:5432/postgres"
```

### Teste 3: Verificar Configurações do Supabase
- Confirme que o banco permite conexões externas
- Verifique se não há restrições de IP

---

**A configuração manual deve resolver os problemas de DNS e conexão!**
