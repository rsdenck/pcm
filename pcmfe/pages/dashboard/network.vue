<template>
  <div class="p-6 md:p-8 w-full">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-[#000000] mb-1">Network</h1>
      <p class="text-sm text-[#666666]">Gerenciamento de redes e SDN</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-globe-alt" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Redes</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0</div>
        <div class="text-xs text-[#666666] mt-1">Total de Redes</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-signal" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">VLANs</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0</div>
        <div class="text-xs text-[#666666] mt-1">VLANs Configuradas</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-shield-check" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Firewall</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0</div>
        <div class="text-xs text-[#666666] mt-1">Regras Ativas</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Tráfego</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0 GB</div>
        <div class="text-xs text-[#666666] mt-1">Últimas 24h</div>
      </div>
    </div>

    <div class="bg-white rounded-lg border border-[#e5e5e5] p-16 text-center">
      <div class="w-16 h-16 rounded-full bg-[#fafafa] flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-globe-alt" class="text-[#999999] text-3xl" />
      </div>
      <h3 class="text-lg font-semibold text-[#000000] mb-2">Funcionalidade em Desenvolvimento</h3>
      <p class="text-[#666666] max-w-md mx-auto">
        O gerenciamento de network estará disponível em breve
      </p>
    </div>
  </div>
</template>
