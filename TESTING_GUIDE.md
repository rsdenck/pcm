# PCM Testing Guide - Login & Tenant Creation Flow

## 🎯 Objetivo
Testar o fluxo completo de autenticação e criação de tenants no PCM.

---

## ✅ Teste 1: Acesso à Raiz (http://192.168.130.10:9000/)

### Cenário 1.1: Usuário Não Autenticado
1. Abra `http://192.168.130.10:9000/` em um navegador
2. **Resultado Esperado**: Deve redirecionar automaticamente para `/login`
3. **Tela Esperada**: Tela de login com campos de email e senha

### Cenário 1.2: Usuário Autenticado
1. Faça login com credenciais válidas
2. Abra `http://192.168.130.10:9000/` em uma nova aba
3. **Resultado Esperado**: Deve redirecionar automaticamente para `/dashboard`
4. **Tela Esperada**: Dashboard principal

---

## ✅ Teste 2: Tela de Login

### Cenário 2.1: Login com Credenciais Válidas
1. Acesse `http://192.168.130.10:9000/login`
2. Preencha:
   - Email: `admin@pcm.local`
   - Senha: `Admin@123456`
3. Clique em "Sign In"
4. **Resultado Esperado**: 
   - Deve fazer login com sucesso
   - Redirecionar para `/dashboard`
   - Exibir nome do usuário no menu superior

### Cenário 2.2: Login com Credenciais Inválidas
1. Acesse `http://192.168.130.10:9000/login`
2. Preencha com credenciais inválidas
3. Clique em "Sign In"
4. **Resultado Esperado**: 
   - Exibir mensagem de erro
   - Permanecer na página de login

### Cenário 2.3: Forgot Password
1. Acesse `http://192.168.130.10:9000/login`
2. Clique em "Forgot?"
3. **Resultado Esperado**: 
   - Redirecionar para `/forgot-password`
   - Exibir formulário de recuperação de senha

---

## ✅ Teste 3: Criação de Tenant

### Cenário 3.1: Acessar Página de Tenants
1. Faça login com sucesso
2. No sidebar, clique em "Tenants"
3. **Resultado Esperado**: 
   - Exibir lista de tenants (pode estar vazia)
   - Botão "Novo Tenant" visível no topo

### Cenário 3.2: Clicar no Botão "Novo Tenant"
1. Na página de tenants, clique no botão "Novo Tenant"
2. **Resultado Esperado**: 
   - Redirecionar para `/dashboard/tenants/new`
   - Exibir formulário de criação de tenant
   - Exibir templates pré-configurados

### Cenário 3.3: Aplicar Template
1. Na página de criação, clique em um template (ex: "Padrão")
2. **Resultado Esperado**: 
   - Preencher automaticamente os campos de quota
   - Exibir toast de sucesso "Template Aplicado"
   - Fechar a seção de templates

### Cenário 3.4: Criar Tenant com Dados Válidos
1. Preencha os campos obrigatórios:
   - Nome: `Tenant Teste`
   - Organização: `Empresa Teste`
   - Proprietário: `João Silva`
2. Preencha quotas (opcional, pode usar template)
3. Clique em "Criar Tenant"
4. **Resultado Esperado**: 
   - Exibir toast de sucesso
   - Redirecionar para `/dashboard/tenants`
   - Novo tenant aparecer na lista

### Cenário 3.5: Validação de Campos Obrigatórios
1. Deixe campos obrigatórios em branco
2. Clique em "Criar Tenant"
3. **Resultado Esperado**: 
   - Exibir mensagem de erro específica
   - Não enviar formulário
   - Permanecer na página

---

## 🔍 Verificações de Console

### Abra o DevTools (F12) e verifique:

1. **Network Tab**:
   - POST `/api/v1/tenants/` deve retornar 201 (Created)
   - Resposta deve conter dados do tenant criado

2. **Console Tab**:
   - Não deve haver erros vermelhos
   - Deve exibir logs de navegação
   - Deve exibir dados enviados ao servidor

3. **Application Tab**:
   - Token JWT deve estar armazenado
   - Cookies de sessão devem estar presentes

---

## 🐛 Troubleshooting

### Problema: Botão "Novo Tenant" não funciona
**Solução**:
- Verifique se está autenticado
- Abra DevTools e verifique console para erros
- Verifique se a rota `/dashboard/tenants/new` existe

### Problema: Formulário não envia
**Solução**:
- Verifique se todos os campos obrigatórios estão preenchidos
- Abra DevTools > Network e verifique a requisição
- Verifique se o backend está respondendo

### Problema: Redireciona para login após criar tenant
**Solução**:
- Verifique se o token JWT está válido
- Verifique se a sessão não expirou
- Faça login novamente

### Problema: Erro 401 ao criar tenant
**Solução**:
- Token expirou, faça login novamente
- Verifique se o header Authorization está sendo enviado

### Problema: Erro 403 ao criar tenant
**Solução**:
- Usuário não tem permissão para criar tenants
- Verifique as permissões do usuário no banco de dados

---

## 📊 Checklist de Testes

- [ ] Acesso à raiz redireciona corretamente
- [ ] Login funciona com credenciais válidas
- [ ] Login rejeita credenciais inválidas
- [ ] Forgot password funciona
- [ ] Página de tenants carrega
- [ ] Botão "Novo Tenant" navega corretamente
- [ ] Templates carregam e aplicam
- [ ] Formulário valida campos obrigatórios
- [ ] Tenant é criado com sucesso
- [ ] Novo tenant aparece na lista
- [ ] Mensagens de erro são claras
- [ ] Não há erros no console

---

## 🚀 Próximos Passos

Após validar este fluxo:
1. Testar edição de tenant
2. Testar exclusão de tenant
3. Testar filtros e busca
4. Testar permissões de acesso
5. Testar performance com múltiplos tenants

