<template>
  <div class="p-6 md:p-8 w-full">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-[#000000] mb-1">Storage</h1>
      <p class="text-sm text-[#666666]">Gerenciamento de armazenamento e volumes</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-circle-stack" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Total</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0 TB</div>
        <div class="text-xs text-[#666666] mt-1">Capacidade Total</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-chart-pie" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Usado</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0 TB</div>
        <div class="text-xs text-[#666666] mt-1">Em Uso</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-check-circle" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Disponível</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0 TB</div>
        <div class="text-xs text-[#666666] mt-1">Livre</div>
      </div>

      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
            <UIcon name="i-heroicons-server" class="text-[#E57000] text-2xl" />
          </div>
          <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Pools</span>
        </div>
        <div class="text-3xl font-bold text-[#000000]">0</div>
        <div class="text-xs text-[#666666] mt-1">Storage Pools</div>
      </div>
    </div>

    <div class="bg-white rounded-lg border border-[#e5e5e5] p-16 text-center">
      <div class="w-16 h-16 rounded-full bg-[#fafafa] flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-circle-stack" class="text-[#999999] text-3xl" />
      </div>
      <h3 class="text-lg font-semibold text-[#000000] mb-2">Funcionalidade em Desenvolvimento</h3>
      <p class="text-[#666666] max-w-md mx-auto">
        O gerenciamento de storage estará disponível em breve
      </p>
    </div>
  </div>
</template>
