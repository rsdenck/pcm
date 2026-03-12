<template>
  <div class="p-6 md:p-8 w-full">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-[#000000] mb-1">Configurações</h1>
      <p class="text-sm text-[#666666]">Configurações gerais do sistema</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Sistema -->
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-cog-6-tooth" class="text-[#E57000] text-xl" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-[#000000]">Sistema</h3>
            <p class="text-xs text-[#666666]">Configurações gerais</p>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Versão</p>
              <p class="text-xs text-[#666666]">PCM v1.0.0</p>
            </div>
          </div>
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Ambiente</p>
              <p class="text-xs text-[#666666]">Development</p>
            </div>
          </div>
        </div>
      </div>

      <!-- API -->
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-code-bracket" class="text-[#E57000] text-xl" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-[#000000]">API</h3>
            <p class="text-xs text-[#666666]">Configurações de API</p>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Endpoint</p>
              <p class="text-xs text-[#666666]">http://localhost:8000/api/v1</p>
            </div>
          </div>
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Documentação</p>
              <p class="text-xs text-[#666666]">/docs</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Segurança -->
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-shield-check" class="text-[#E57000] text-xl" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-[#000000]">Segurança</h3>
            <p class="text-xs text-[#666666]">Configurações de segurança</p>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Autenticação</p>
              <p class="text-xs text-[#666666]">JWT Token</p>
            </div>
          </div>
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">SSL/TLS</p>
              <p class="text-xs text-[#666666]">Configurável</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Observabilidade -->
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-chart-bar" class="text-[#E57000] text-xl" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-[#000000]">Observabilidade</h3>
            <p class="text-xs text-[#666666]">Métricas e logs</p>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">OpenTelemetry</p>
              <p class="text-xs text-[#666666]">Habilitado</p>
            </div>
          </div>
          <div class="flex items-center justify-between py-3 border-b border-[#e5e5e5]">
            <div>
              <p class="text-sm font-medium text-[#000000]">Prometheus</p>
              <p class="text-xs text-[#666666]">Porta 9090</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
