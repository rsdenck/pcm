# Configuração do DNS na Cloudflare

Para que o SaaS funcione corretamente com isolamento de tenants via subdomínio/domínio, siga estas configurações:

1. **A Record Principal:**
   - Nome: `app.com` (ou seu domínio)
   - Valor: `IP_DA_VM`
   - Proxy: Enabled (Laranja)

2. **Wildcard para Tenants:**
   - Nome: `*.app.com`
   - Valor: `IP_DA_VM`
   - Proxy: Enabled (Laranja)

3. **SSL/TLS:**
   - Modo: `Full (Strict)`
   - Cloudflare Origin CA: Gerar certificado para `*.app.com` e `app.com` para instalar no Nginx do Host.

4. **WAF:**
   - Ativar regras de proteção OWASP.
   - Bloquear acessos diretos ao IP da VM (permitir apenas IPs da Cloudflare).
