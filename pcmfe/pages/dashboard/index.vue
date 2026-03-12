<template>
  <div class="p-6 md:p-8 w-full">
    <!-- Header -->
    <header class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-[#000000] mb-1">Dashboard</h1>
        <p class="text-sm text-[#666666]">Visão geral da infraestrutura Proxmox</p>
      </div>
      
      <UButton 
        color="primary" 
        @click="refreshData"
        class="bg-[#E57000] hover:bg-[#CC6600] text-white"
      >
        <UIcon name="i-heroicons-arrow-path" class="mr-2" />
        Sincronizar
      </UButton>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col justify-center items-center h-[50vh] gap-4">
      <div class="relative w-12 h-12">
        <div class="absolute inset-0 border-4 border-[#e5e5e5] rounded-full"></div>
        <div class="absolute inset-0 border-4 border-[#E57000] border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p class="text-[#666666] text-sm">Carregando dados...</p>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Clusters Card -->
        <div class="bg-white rounded-lg border border-[#e5e5e5] p-6 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
              <UIcon name="i-heroicons-server" class="text-[#E57000] text-2xl" />
            </div>
            <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Clusters</span>
          </div>
          <div class="text-3xl font-bold text-[#000000] mb-1">
            {{ stats.online_clusters }}<span class="text-[#999999] text-xl">/{{ stats.total_clusters }}</span>
          </div>
          <div class="text-xs text-[#666666]">Online / Total</div>
        </div>

        <!-- Nodes Card -->
        <div class="bg-white rounded-lg border border-[#e5e5e5] p-6 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
              <UIcon name="i-heroicons-cpu-chip" class="text-[#E57000] text-2xl" />
            </div>
            <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Nodes</span>
          </div>
          <div class="text-3xl font-bold text-[#000000] mb-1">
            {{ stats.online_nodes }}<span class="text-[#999999] text-xl">/{{ stats.total_nodes }}</span>
          </div>
          <div class="text-xs text-[#666666]">Online / Total</div>
        </div>

        <!-- VMs Card -->
        <div class="bg-white rounded-lg border border-[#e5e5e5] p-6 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
              <UIcon name="i-heroicons-cube" class="text-[#E57000] text-2xl" />
            </div>
            <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">VMs</span>
          </div>
          <div class="text-3xl font-bold text-[#000000] mb-1">
            {{ stats.running_vms }}<span class="text-[#999999] text-xl">/{{ stats.total_vms }}</span>
          </div>
          <div class="text-xs text-[#666666]">Running / Total</div>
        </div>

        <!-- Containers Card -->
        <div class="bg-white rounded-lg border border-[#e5e5e5] p-6 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#E57000]/10 flex items-center justify-center">
              <UIcon name="i-heroicons-cube-transparent" class="text-[#E57000] text-2xl" />
            </div>
            <span class="text-xs font-medium text-[#999999] uppercase tracking-wide">Containers</span>
          </div>
          <div class="text-3xl font-bold text-[#000000] mb-1">
            {{ stats.running_containers }}<span class="text-[#999999] text-xl">/{{ stats.total_containers }}</span>
          </div>
          <div class="text-xs text-[#666666]">Running / Total</div>
        </div>
      </div>

      <!-- Clusters Section -->
      <div class="bg-white rounded-lg border border-[#e5e5e5] p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-[#000000]">Clusters Ativos</h2>
          <UButton 
            to="/dashboard/clusters/new" 
            color="gray"
            class="text-[#333333] hover:bg-[#fafafa]"
          >
            <UIcon name="i-heroicons-plus" class="mr-2" />
            Adicionar Cluster
          </UButton>
        </div>

        <!-- Empty State -->
        <div v-if="clusters.length === 0" class="text-center py-16">
          <div class="w-16 h-16 rounded-full bg-[#fafafa] flex items-center justify-center mx-auto mb-4">
            <UIcon name="i-heroicons-server" class="text-[#999999] text-3xl" />
          </div>
          <h3 class="text-lg font-semibold text-[#000000] mb-2">Nenhum Cluster Configurado</h3>
          <p class="text-[#666666] mb-6 max-w-md mx-auto">
            Adicione seu primeiro cluster Proxmox para começar a gerenciar sua infraestrutura
          </p>
          <UButton 
            to="/dashboard/clusters/new" 
            class="bg-[#E57000] hover:bg-[#CC6600] text-white"
          >
            <UIcon name="i-heroicons-plus" class="mr-2" />
            Adicionar Cluster
          </UButton>
        </div>

        <!-- Clusters List -->
        <div v-else class="space-y-3">
          <div 
            v-for="cluster in clusters" 
            :key="cluster.id" 
            class="flex items-center justify-between p-4 rounded-lg border border-[#e5e5e5] hover:border-[#E57000]/30 hover:shadow-sm transition-all"
          >
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-lg bg-[#fafafa] border border-[#e5e5e5] flex items-center justify-center">
                <UIcon name="i-heroicons-server" class="text-[#E57000] text-xl" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-[#000000]">{{ cluster.name }}</h3>
                <p class="text-xs text-[#666666]">{{ cluster.hostname }}:{{ cluster.port }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span 
                class="px-3 py-1 rounded-full text-xs font-medium"
                :class="cluster.status === 'online' 
                  ? 'bg-green-50 text-green-700 border border-green-200' 
                  : 'bg-red-50 text-red-700 border border-red-200'"
              >
                {{ cluster.status === 'online' ? 'Online' : 'Offline' }}
              </span>
              <UButton 
                :to="`/dashboard/clusters/${cluster.id}`" 
                color="gray" 
                size="sm"
                class="text-[#333333] hover:bg-[#fafafa]"
              >
                Ver Detalhes
              </UButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const loading = ref(true)

const stats = ref({
  total_clusters: 0,
  online_clusters: 0,
  total_nodes: 0,
  online_nodes: 0,
  total_vms: 0,
  running_vms: 0,
  total_containers: 0,
  running_containers: 0,
  total_tenants: 0
})

const clusters = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const { data: dashboardData } = await useFetch(`${config.public.apiBase}/dashboard`)
    
    if (dashboardData.value) {
      stats.value = dashboardData.value.stats
      clusters.value = dashboardData.value.clusters || []
    }
  } catch (error) {
    console.error('Failed to fetch data', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>
