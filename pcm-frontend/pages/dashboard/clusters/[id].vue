<template>
  <div class="p-4 md:p-8 w-full">
    <header class="mb-10">
      <UButton to="/dashboard/clusters" color="gray" variant="ghost" class="mb-4">
        <UIcon name="i-heroicons-arrow-left" class="mr-2" />
        Voltar
      </UButton>
      
      <div v-if="loading" class="h-20 flex items-center">
        <div class="animate-pulse flex space-x-4">
          <div class="h-12 w-48 bg-gray-200 dark:bg-gray-800 rounded"></div>
        </div>
      </div>
      
      <div v-else-if="cluster" class="flex justify-between items-start">
        <div>
          <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
            {{ cluster.name }}
          </h1>
          <div class="flex items-center gap-3 mt-2">
            <span class="text-gray-500">{{ cluster.hostname }}:{{ cluster.port }}</span>
            <UBadge :color="cluster.status === 'online' ? 'green' : 'red'" variant="subtle">
              {{ cluster.status }}
            </UBadge>
          </div>
        </div>
        
        <UButton 
          @click="syncCluster" 
          color="primary" 
          class="bg-brand-orange hover:bg-brand-orange/90"
          :loading="syncing"
        >
          <UIcon name="i-heroicons-arrow-path" class="mr-2" />
          Sincronizar
        </UButton>
      </div>
    </header>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="relative w-16 h-16">
        <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
        <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
      </div>
    </div>

    <div v-else-if="cluster">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-cpu-chip" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Nodes</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.online_nodes }}<span class="text-gray-300 dark:text-gray-800 text-2xl">/{{ stats.total_nodes }}</span>
          </div>
          <div class="mt-2 text-xs text-gray-500">Online / Total</div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-cube" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">VMs</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.running_vms }}<span class="text-gray-300 dark:text-gray-800 text-2xl">/{{ stats.total_vms }}</span>
          </div>
          <div class="mt-2 text-xs text-gray-500">Running / Total</div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-cube-transparent" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Containers</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.total_containers }}
          </div>
          <div class="mt-2 text-xs text-gray-500">LXC Containers</div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <UIcon name="i-heroicons-circle-stack" class="text-brand-orange text-2xl" />
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Storage</span>
            </div>
          </template>
          <div class="text-4xl font-black text-black dark:text-white tracking-tighter">
            {{ stats.available_storage }}<span class="text-gray-300 dark:text-gray-800 text-2xl">/{{ stats.total_storage }}</span>
          </div>
          <div class="mt-2 text-xs text-gray-500">Available / Total</div>
        </UCard>
      </div>

      <!-- Cluster Info -->
      <div class="mb-8">
        <h2 class="text-xl font-black text-black dark:text-white mb-4 uppercase tracking-tight">
          Informações do Cluster
        </h2>
        <UCard>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-widest mb-1">Tipo</p>
              <p class="text-lg font-bold text-black dark:text-white">{{ cluster.cluster_type }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-widest mb-1">Última Sincronização</p>
              <p class="text-lg font-bold text-black dark:text-white">
                {{ cluster.last_sync ? new Date(cluster.last_sync).toLocaleString('pt-BR') : 'Nunca' }}
              </p>
            </div>
            <div v-if="cluster.description" class="md:col-span-2">
              <p class="text-xs text-gray-500 uppercase tracking-widest mb-1">Descrição</p>
              <p class="text-lg text-black dark:text-white">{{ cluster.description }}</p>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const route = useRoute()
const loading = ref(true)
const syncing = ref(false)
const cluster = ref(null)
const stats = ref({
  total_nodes: 0,
  online_nodes: 0,
  total_vms: 0,
  running_vms: 0,
  total_containers: 0,
  total_storage: 0,
  available_storage: 0
})

const clusterId = route.params.id as string

const fetchCluster = async () => {
  loading.value = true
  try {
    const { data: clusterData } = await useFetch(`${config.public.apiBase}/clusters/${clusterId}`)
    cluster.value = clusterData.value
    
    const { data: statsData } = await useFetch(`${config.public.apiBase}/clusters/${clusterId}/stats`)
    stats.value = statsData.value || stats.value
  } catch (error) {
    console.error('Failed to fetch cluster', error)
  } finally {
    loading.value = false
  }
}

const syncCluster = async () => {
  syncing.value = true
  try {
    await $fetch(`${config.public.apiBase}/clusters/${clusterId}/sync`)
    await fetchCluster()
  } catch (error) {
    console.error('Failed to sync cluster', error)
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchCluster()
})
</script>
