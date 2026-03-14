<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-6">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <header class="mb-6">
        <div class="flex items-center gap-4 mb-4">
          <UButton 
            @click="$router.back()" 
            color="gray" 
            variant="ghost" 
            size="sm"
          >
            <UIcon name="i-heroicons-arrow-left" class="mr-2" />
            Voltar
          </UButton>
        </div>
        
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">
              Estatísticas do Tenant
            </h1>
            <p class="text-sm text-gray-600">
              {{ tenant?.name }} - Métricas e uso de recursos
            </p>
          </div>
          
          <UButton 
            @click="refreshStats"
            :loading="loading"
            color="gray"
            variant="outline"
            size="sm"
          >
            <UIcon name="i-heroicons-arrow-path" class="mr-2" />
            Atualizar
          </UButton>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="loading && !stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="i in 8" :key="i" class="animate-pulse">
          <UCard class="shadow-sm border border-gray-200 bg-white h-32">
            <div class="space-y-3">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-6 bg-gray-200 rounded w-1/2"></div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Statistics -->
      <div v-else-if="stats" class="space-y-6">
        <!-- Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Total VMs -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-500">Total VMs</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.resource_counts?.vms || 0 }}</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <UIcon name="i-heroicons-server" class="text-blue-600 text-lg" />
              </div>
            </div>
          </UCard>

          <!-- Total Users -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-500">Usuários</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.resource_counts?.users || 0 }}</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <UIcon name="i-heroicons-users" class="text-green-600 text-lg" />
              </div>
            </div>
          </UCard>

          <!-- Total Clusters -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-500">Clusters</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.resource_counts?.clusters || 0 }}</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <UIcon name="i-heroicons-cube" class="text-purple-600 text-lg" />
              </div>
            </div>
          </UCard>

          <!-- Storage Used -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-500">Storage Usado</p>
                <p class="text-2xl font-bold text-gray-900">{{ formatStorage(stats.usage_summary?.storage?.current || 0) }}</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
                <UIcon name="i-heroicons-circle-stack" class="text-orange-600 text-lg" />
              </div>
            </div>
          </UCard>
        </div>

        <!-- Resource Usage Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- CPU Usage -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <template #header>
              <h3 class="text-base font-semibold text-gray-900">Uso de CPU</h3>
            </template>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">CPU Atual</span>
                <span class="text-sm font-medium text-gray-900">
                  {{ stats.quota_status?.cpu?.current || 0 }} / {{ stats.quota_status?.cpu?.limit || 'Ilimitado' }} vCPU
                </span>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div 
                  class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] h-3 rounded-full transition-all"
                  :style="{ width: `${stats.quota_status?.cpu?.percentage || 0}%` }"
                ></div>
              </div>
              
              <p class="text-xs text-gray-500">
                {{ stats.quota_status?.cpu?.percentage || 0 }}% utilizado
              </p>
            </div>
          </UCard>

          <!-- RAM Usage -->
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <template #header>
              <h3 class="text-base font-semibold text-gray-900">Uso de RAM</h3>
            </template>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">RAM Atual</span>
                <span class="text-sm font-medium text-gray-900">
                  {{ stats.quota_status?.ram?.current || 0 }} / {{ stats.quota_status?.ram?.limit || 'Ilimitado' }} GB
                </span>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div 
                  class="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all"
                  :style="{ width: `${stats.quota_status?.ram?.percentage || 0}%` }"
                ></div>
              </div>
              
              <p class="text-xs text-gray-500">
                {{ stats.quota_status?.ram?.percentage || 0 }}% utilizado
              </p>
            </div>
          </UCard>
        </div>

        <!-- Detailed Quotas -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Quotas Detalhadas</h3>
          </template>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="(quota, key) in stats.quota_status" :key="key" class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700 capitalize">{{ formatQuotaName(key) }}</span>
                <span class="text-xs text-gray-500">{{ quota.unit }}</span>
              </div>
              
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Usado: {{ quota.current }}</span>
                <span class="text-gray-600">Limite: {{ quota.limit || 'Ilimitado' }}</span>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all"
                  :style="{ width: `${quota.percentage || 0}%` }"
                ></div>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-exclamation-triangle" class="text-4xl text-red-300 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-600 mb-2">Erro ao carregar estatísticas</h3>
        <p class="text-sm text-gray-500">Não foi possível carregar as estatísticas do tenant.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFetchWithTimeout } from '~/composables/useFetchWithTimeout'
import { useDebounce } from '~/composables/useDebounce'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()
const { fetchWithTimeout, cancelAll } = useFetchWithTimeout()
const { debounce } = useDebounce()

// Reactive data
const tenant = ref(null)
const stats = ref(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Get tenant ID from route
const tenantId = route.params.id as string

// Methods
const fetchStats = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Fetch tenant info
    const tenantResponse = await fetchWithTimeout(
      `${config.public.apiBase}/tenants/${tenantId}`,
      { timeout: 30000 }
    )
    
    tenant.value = tenantResponse
    
    // Fetch statistics (using tenant data for now, will be separate endpoint later)
    stats.value = {
      resource_counts: {
        vms: tenantResponse.quota_status?.vms?.current || 0,
        users: 1, // Placeholder
        clusters: 1 // Placeholder
      },
      quota_status: tenantResponse.quota_status,
      usage_summary: {
        storage: {
          current: tenantResponse.quota_status?.storage?.current || 0
        }
      }
    }
  } catch (err: any) {
    console.error('Failed to fetch statistics:', err)
    error.value = err.message || 'Falha ao carregar estatísticas'
    stats.value = null
  } finally {
    loading.value = false
  }
}

const refreshStats = async () => {
  await debounce(() => fetchStats(), 500, 'stats-refresh')
}

// Utility functions
const formatStorage = (bytes: number) => {
  if (bytes === 0) return '0 GB'
  const gb = bytes / (1024 * 1024 * 1024)
  return `${gb.toFixed(1)} GB`
}

const formatQuotaName = (key: string) => {
  const names = {
    cpu: 'CPU',
    ram: 'RAM',
    vms: 'VMs',
    containers: 'Containers',
    storage: 'Storage',
    volumes: 'Volumes',
    snapshots: 'Snapshots',
    networks: 'Redes',
    floating_ips: 'IPs Flutuantes',
    load_balancers: 'Load Balancers',
    vlans: 'VLANs'
  }
  return names[key] || key
}

// Lifecycle
onMounted(() => {
  fetchStats()
})

onBeforeUnmount(() => {
  cancelAll()
})

// Meta tags
useHead({
  title: `Estatísticas - ${tenant.value?.name || 'Tenant'} - PCM`,
  meta: [
    { name: 'description', content: 'Estatísticas e métricas do tenant' }
  ]
})
</script>