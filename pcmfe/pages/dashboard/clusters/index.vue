<template>
  <div class="p-4 md:p-8 w-full">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
      <div>
        <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
          Clusters <span class="text-brand-orange">Proxmox</span>
        </h1>
        <p class="text-gray-500 mt-2">Gerenciamento de clusters multi-site</p>
      </div>
      
      <UButton 
        to="/dashboard/clusters/new" 
        color="primary" 
        class="bg-brand-orange hover:bg-brand-orange/90"
      >
        <UIcon name="i-heroicons-plus" class="mr-2" />
        Adicionar Cluster
      </UButton>
    </header>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="relative w-16 h-16">
        <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
        <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
      </div>
    </div>

    <div v-else>
      <div v-if="clusters.length === 0" class="text-center py-20 bg-white dark:bg-white/5 rounded-3xl border border-gray-100 dark:border-white/5">
        <UIcon name="i-heroicons-server" class="text-gray-300 dark:text-gray-700 text-6xl mb-4" />
        <h3 class="text-xl font-black text-black dark:text-white mb-2">Nenhum Cluster Configurado</h3>
        <p class="text-gray-500 mb-8">Adicione seu primeiro cluster Proxmox para começar</p>
        <UButton to="/dashboard/clusters/new" color="primary" class="bg-brand-orange">
          <UIcon name="i-heroicons-plus" class="mr-2" />
          Adicionar Cluster
        </UButton>
      </div>

      <div v-else class="grid grid-cols-1 gap-4">
        <UCard v-for="cluster in clusters" :key="cluster.id" class="hover:border-brand-orange/40 transition-all">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-6">
              <div class="w-14 h-14 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center border border-gray-100 dark:border-white/5">
                <UIcon name="i-heroicons-server" class="text-brand-orange text-2xl" />
              </div>
              <div>
                <h3 class="text-lg font-black text-black dark:text-white">{{ cluster.name }}</h3>
                <div class="flex items-center gap-3 mt-1">
                  <span class="text-sm text-gray-500">{{ cluster.hostname }}:{{ cluster.port }}</span>
                  <div class="w-1 h-1 bg-gray-200 dark:bg-gray-800 rounded-full"></div>
                  <span class="text-xs font-black text-brand-orange uppercase">{{ cluster.cluster_type }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <UBadge :color="cluster.status === 'online' ? 'green' : 'red'" variant="subtle">
                {{ cluster.status }}
              </UBadge>
              <UButton 
                @click="syncCluster(cluster.id)" 
                color="gray" 
                size="sm"
                :loading="syncing[cluster.id]"
              >
                <UIcon name="i-heroicons-arrow-path" />
              </UButton>
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
