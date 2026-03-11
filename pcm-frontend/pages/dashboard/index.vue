<template>
  <div class="p-4 md:p-8 w-full">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-1.5 h-1.5 rounded-full bg-brand-orange animate-pulse"></div>
          <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Sistema Ativo</span>
        </div>
        <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
          Visão <span class="text-brand-orange">Geral</span>
        </h1>
      </div>
      
      <UButton 
        color="primary" 
        @click="refreshData"
        class="bg-brand-orange hover:bg-brand-orange/90"
      >
        <UIcon name="i-heroicons-arrow-path" class="mr-2" />
        Sincronizar
      </UButton>
    </header>

    <div v-if="loading" class="flex flex-col justify-center items-center h-[50vh] gap-6">
      <div class="relative w-16 h-16">
        <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
        <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Carregando...</p>
    </div>

    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-server" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Clusters</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.total_clusters }}
          </div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-cpu-chip" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Nodes</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.total_nodes }}
          </div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-cube" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">VMs</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.total_vms }}
          </div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-users" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Tenants</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.total_tenants }}
          </div>
        </UCard>
      </div>

      <div class="flex items-center justify-between mb-8">
        <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">
          Clusters Ativos
        </h2>
        <UButton to="/dashboard/clusters/new" color="gray">
          Adicionar Cluster
        </UButton>
      </div>

      <div v-if="clusters.length === 0" class="text-center py-20">
        <UIcon name="i-heroicons-server" class="text-gray-300 dark:text-gray-700 text-6xl mb-4" />
        <h3 class="text-xl font-black text-black dark:text-white mb-2">Nenhum Cluster</h3>
        <p class="text-gray-500 mb-8">Adicione seu primeiro cluster Proxmox</p>
        <UButton to="/dashboard/clusters/new" color="primary" class="bg-brand-orange">
          Adicionar Cluster
        </UButton>
      </div>

      <div v-else class="grid grid-cols-1 gap-4">
        <UCard v-for="cluster in clusters" :key="cluster.id" class="hover:border-brand-orange/40 transition-all">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-6">
              <div class="w-14 h-14 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center">
                <UIcon name="i-heroicons-server" class="text-brand-orange text-2xl" />
              </div>
              <div>
                <h3 class="text-lg font-black text-black dark:text-white">{{ cluster.name }}</h3>
                <p class="text-sm text-gray-500">{{ cluster.hostname }}:{{ cluster.port }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <UBadge :color="cluster.status === 'online' ? 'green' : 'red'">
                {{ cluster.status }}
              </UBadge>
              <UButton :to="`/dashboard/clusters/${cluster.id}`" color="gray" size="sm">
                Detalhes
              </UButton>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const loading = ref(true)

const stats = ref({
  total_clusters: 0,
  total_nodes: 0,
  total_vms: 0,
  total_tenants: 0
})

const clusters = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const { data } = await useFetch(`${config.public.apiBase}/clusters`)
    clusters.value = data.value || []
    stats.value.total_clusters = clusters.value.length
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
