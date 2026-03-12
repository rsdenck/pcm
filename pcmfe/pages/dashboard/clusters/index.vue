<template>
  <div class="p-6 md:p-8 w-full">
    <!-- Header -->
    <header class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-[#000000] mb-1">Clusters Proxmox</h1>
        <p class="text-sm text-[#666666]">Gerenciamento de clusters multi-site</p>
      </div>
      
      <UButton 
        to="/dashboard/clusters/new" 
        class="bg-[#E57000] hover:bg-[#CC6600] text-white"
      >
        <UIcon name="i-heroicons-plus" class="mr-2" />
        Adicionar Cluster
      </UButton>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="relative w-12 h-12">
        <div class="absolute inset-0 border-4 border-[#e5e5e5] rounded-full"></div>
        <div class="absolute inset-0 border-4 border-[#E57000] border-t-transparent rounded-full animate-spin"></div>
      </div>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Empty State -->
      <div v-if="clusters.length === 0" class="bg-white rounded-lg border border-[#e5e5e5] p-16 text-center">
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
      <div v-else class="space-y-4">
        <div 
          v-for="cluster in clusters" 
          :key="cluster.id" 
          class="bg-white rounded-lg border border-[#e5e5e5] p-6 hover:border-[#E57000]/30 hover:shadow-md transition-all"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-lg bg-[#fafafa] border border-[#e5e5e5] flex items-center justify-center">
                <UIcon name="i-heroicons-server" class="text-[#E57000] text-2xl" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-[#000000]">{{ cluster.name }}</h3>
                <div class="flex items-center gap-3 mt-1">
                  <span class="text-sm text-[#666666]">{{ cluster.hostname }}:{{ cluster.port }}</span>
                  <div class="w-1 h-1 bg-[#d4d4d4] rounded-full"></div>
                  <span class="text-xs font-medium text-[#E57000] uppercase">{{ cluster.cluster_type }}</span>
                </div>
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
                @click="syncCluster(cluster.id)" 
                color="gray" 
                size="sm"
                :loading="syncing[cluster.id]"
                class="text-[#333333] hover:bg-[#fafafa]"
              >
                <UIcon name="i-heroicons-arrow-path" />
              </UButton>
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
const syncing = ref<Record<string, boolean>>({})
const clusters = ref([])

const fetchClusters = async () => {
  loading.value = true
  try {
    const { data } = await useFetch(`${config.public.apiBase}/clusters`)
    clusters.value = data.value || []
  } catch (error) {
    console.error('Failed to fetch clusters', error)
  } finally {
    loading.value = false
  }
}

const syncCluster = async (clusterId: string) => {
  syncing.value[clusterId] = true
  try {
    await $fetch(`${config.public.apiBase}/clusters/${clusterId}/sync`)
    await fetchClusters()
  } catch (error) {
    console.error('Failed to sync cluster', error)
  } finally {
    syncing.value[clusterId] = false
  }
}

onMounted(() => {
  fetchClusters()
})
</script>
