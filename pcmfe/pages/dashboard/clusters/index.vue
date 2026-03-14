<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <header class="mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">
              Clusters
            </h1>
            <p class="text-sm text-gray-600">
              Gerencie clusters Proxmox da sua infraestrutura multi-site
            </p>
          </div>
          
          <div class="flex flex-col sm:flex-row gap-3">
            <UButton 
              @click="navigateToNew" 
              :disabled="!canUpdate('cluster')"
              size="sm"
              class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-sm hover:shadow-md transition-all"
              :class="{ 'opacity-50 cursor-not-allowed': !canUpdate('cluster') }"
              :ui="{
                rounded: 'rounded-lg',
                size: { sm: 'text-sm px-4 py-2' }
              }"
            >
              <UIcon name="i-heroicons-plus" class="mr-2 text-sm" />
              Adicionar Cluster
            </UButton>
          </div>
        </div>
      </header>

      <!-- Filters and Search -->
      <div class="mb-6">
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <div class="flex flex-col md:flex-row gap-3">
            <div class="flex-1">
              <UInput 
                v-model="searchQuery" 
                placeholder="Buscar clusters..." 
                size="md"
                class="w-full"
                :ui="{ 
                  base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                  rounded: 'rounded-lg',
                  size: { md: 'text-sm px-3 py-2' },
                  color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
                }"
              />
            </div>
            
            <div class="flex gap-3">
              <USelect 
                v-model="statusFilter" 
                :options="statusOptions"
                size="md"
                class="w-40"
                :ui="{ 
                  base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                  rounded: 'rounded-lg',
                  size: { md: 'text-sm px-3 py-2' },
                  color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
                }"
              />
              
              <UButton 
                @click="refreshClusters" 
                :loading="loading"
                color="gray"
                variant="outline"
                size="md"
                class="border border-gray-200"
                :ui="{
                  rounded: 'rounded-lg'
                }"
              >
                <UIcon name="i-heroicons-arrow-path" />
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Clusters Grid -->
      <div v-if="loading && clusters.length === 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="animate-pulse">
          <UCard class="shadow-sm border border-gray-200 bg-white h-48">
            <div class="space-y-3">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-2 bg-gray-200 rounded w-1/2"></div>
              <div class="space-y-2">
                <div class="h-2 bg-gray-200 rounded"></div>
                <div class="h-2 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <div v-else-if="filteredClusters.length === 0 && !loading" class="text-center py-12">
        <UIcon name="i-heroicons-server" class="text-4xl text-gray-300 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-600 mb-2">Nenhum cluster encontrado</h3>
        <p class="text-sm text-gray-500 mb-4">
          {{ searchQuery ? 'Tente ajustar os filtros de busca' : 'Comece adicionando seu primeiro cluster' }}
        </p>
        <UButton 
          v-if="!searchQuery"
          @click="navigateToNew" 
          size="sm"
          class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white"
        >
          <UIcon name="i-heroicons-plus" class="mr-2" />
          Adicionar Primeiro Cluster
        </UButton>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard 
          v-for="cluster in filteredClusters" 
          :key="cluster.id"
          class="shadow-sm border border-gray-200 bg-white hover:shadow-md transition-all cursor-pointer"
          @click="navigateToCluster(cluster.id)"
        >
          <template #header>
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-[#E57000] to-[#FF8C00] flex items-center justify-center">
                  <UIcon name="i-heroicons-server" class="text-white text-lg" />
                </div>
                <div>
                  <h3 class="text-base font-semibold text-gray-900 truncate">{{ cluster.name }}</h3>
                  <p class="text-xs text-gray-500">{{ cluster.hostname }}:{{ cluster.port }}</p>
                </div>
              </div>
              
              <UBadge 
                :color="getStatusColor(cluster.status)" 
                variant="subtle"
                class="capitalize text-xs"
              >
                {{ getStatusLabel(cluster.status) }}
              </UBadge>
            </div>
          </template>

          <div class="space-y-3">
            <!-- Cluster Info -->
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-xs text-gray-600">
                <UIcon name="i-heroicons-cube" class="text-gray-400" />
                <span class="capitalize">{{ cluster.cluster_type }}</span>
              </div>
              
              <div v-if="cluster.description" class="flex items-center gap-2 text-xs text-gray-600">
                <UIcon name="i-heroicons-document-text" class="text-gray-400" />
                <span>{{ cluster.description }}</span>
              </div>
            </div>

            <!-- Quick Stats -->
            <div class="grid grid-cols-3 gap-2 pt-2 border-t border-gray-100">
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ cluster.nodes_count || 0 }}</div>
                <div class="text-xs text-gray-500">Nodes</div>
              </div>
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ cluster.vms_count || 0 }}</div>
                <div class="text-xs text-gray-500">VMs</div>
              </div>
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ cluster.containers_count || 0 }}</div>
                <div class="text-xs text-gray-500">Containers</div>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">
                Adicionado em {{ formatDate(cluster.created_at) }}
              </span>
              
              <div class="flex gap-1">
                <UButton 
                  @click.stop="syncCluster(cluster.id)"
                  :loading="syncing[cluster.id]"
                  :disabled="!canRead('cluster')"
                  color="gray" 
                  variant="ghost" 
                  size="xs"
                  class="hover:bg-gray-50"
                  :class="{ 'opacity-50 cursor-not-allowed': !canRead('cluster') }"
                >
                  <UIcon name="i-heroicons-arrow-path" />
                </UButton>
                
                <UButton 
                  @click.stop="editCluster(cluster.id)"
                  :disabled="!canUpdate('cluster')"
                  color="gray" 
                  variant="ghost" 
                  size="xs"
                  class="hover:bg-gray-50"
                  :class="{ 'opacity-50 cursor-not-allowed': !canUpdate('cluster') }"
                >
                  <UIcon name="i-heroicons-pencil" />
                </UButton>
              </div>
            </div>
          </template>
        </UCard>
      </div>

      <!-- Pagination -->
      <div v-if="filteredClusters.length > 0" class="mt-8 flex justify-center">
        <UPagination 
          v-model="currentPage" 
          :page-count="pageSize" 
          :total="totalClusters"
          class="shadow-lg"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'
import { useRuntimeConfig } from '#app'
import { useRouter } from 'vue-router'
import { useFetchWithTimeout } from '~/composables/useFetchWithTimeout'
import { useDebounce } from '~/composables/useDebounce'

const config = useRuntimeConfig()
const router = useRouter()
const toast = useToast()
const { canRead, canUpdate, canDelete } = useRBAC3()
const { fetchWithTimeout, cancelAll } = useFetchWithTimeout()
const { debounce } = useDebounce()

// Reactive data
const clusters = ref([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(12)
const totalClusters = ref(0)
const syncing = ref<Record<string, boolean>>({})

// Status options for filter
const statusOptions = [
  { label: 'Todos os Status', value: 'all' },
  { label: 'Online', value: 'online' },
  { label: 'Offline', value: 'offline' },
  { label: 'Manutenção', value: 'maintenance' }
]

// Computed properties
const filteredClusters = computed(() => {
  let filtered = clusters.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cluster => 
      cluster.name.toLowerCase().includes(query) ||
      cluster.hostname.toLowerCase().includes(query) ||
      cluster.cluster_type.toLowerCase().includes(query)
    )
  }

  // Filter by status
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(cluster => cluster.status === statusFilter.value)
  }

  return filtered
})

// Methods
const navigateToNew = () => {
  router.push('/dashboard/clusters/new')
}

const fetchClusters = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetchWithTimeout(
      `${config.public.apiBase}/clusters/`,
      { timeout: 30000 }
    )
    
    clusters.value = response || []
    totalClusters.value = response?.length || 0
  } catch (err: any) {
    console.error('Failed to fetch clusters:', err)
    error.value = err.message || 'Falha ao carregar clusters'
    clusters.value = []
    
    toast.add({
      title: 'Erro ao Carregar Clusters',
      description: error.value,
      color: 'red',
      timeout: 5000
    })
  } finally {
    loading.value = false
  }
}

const refreshClusters = async () => {
  await debounce(() => fetchClusters(), 500, 'clusters-refresh')
}

const navigateToCluster = (clusterId: string) => {
  if (!canRead('cluster')) {
    toast.add({
      title: 'Permissão Negada',
      description: 'Você não tem permissão para visualizar clusters.',
      color: 'red',
      timeout: 3000
    })
    return
  }
  router.push(`/dashboard/clusters/${clusterId}`)
}

const editCluster = (clusterId: string) => {
  if (!canUpdate('cluster')) {
    toast.add({
      title: 'Permissão Negada',
      description: 'Você não tem permissão para editar clusters.',
      color: 'red',
      timeout: 3000
    })
    return
  }
  router.push(`/dashboard/clusters/${clusterId}/edit`)
}

const syncCluster = async (clusterId: string) => {
  // Prevenir múltiplos cliques
  if (syncing.value[clusterId]) {
    return
  }
  
  syncing.value[clusterId] = true
  try {
    await fetchWithTimeout(
      `${config.public.apiBase}/clusters/${clusterId}/sync`,
      { method: 'POST', timeout: 30000 }
    )
    
    await fetchClusters()
    
    toast.add({
      title: 'Cluster Sincronizado',
      description: 'O cluster foi sincronizado com sucesso.',
      color: 'green',
      timeout: 3000
    })
  } catch (err: any) {
    console.error('Failed to sync cluster', err)
    toast.add({
      title: 'Erro na Sincronização',
      description: err.message || 'Não foi possível sincronizar o cluster.',
      color: 'red',
      timeout: 5000
    })
  } finally {
    syncing.value[clusterId] = false
  }
}
      timeout: 5000
    })
  } finally {
    syncing.value[clusterId] = false
  }
}

// Utility functions
const getStatusColor = (status: string) => {
  const colors = {
    online: 'green',
    offline: 'red',
    maintenance: 'yellow'
  }
  return colors[status] || 'gray'
}

const getStatusLabel = (status: string) => {
  const labels = {
    online: 'Online',
    offline: 'Offline',
    maintenance: 'Manutenção'
  }
  return labels[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  fetchClusters()
})

onBeforeUnmount(() => {
  cancelAll()
})

// Watch para refetch quando necessário
watch([searchQuery, statusFilter], () => {
  currentPage.value = 1
}, { debounce: 300 })

// Meta tags
useHead({
  title: 'Clusters - PCM',
  meta: [
    { name: 'description', content: 'Gerencie clusters Proxmox da sua infraestrutura multi-site' }
  ]
})
</script>