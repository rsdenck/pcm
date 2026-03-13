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
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-gradient-to-r from-[#E57000] to-[#FF8C00] flex items-center justify-center">
              <UIcon name="i-heroicons-building-office" class="text-white text-xl" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ tenant?.name || 'Carregando...' }}</h1>
              <p class="text-sm text-gray-600">{{ tenant?.organization }}</p>
            </div>
          </div>
          
          <UBadge 
            v-if="tenant"
            :color="getStatusColor(tenant.status)" 
            variant="subtle"
            class="capitalize"
          >
            {{ getStatusLabel(tenant.status) }}
          </UBadge>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="animate-pulse">
          <UCard class="shadow-sm border border-gray-200 bg-white h-32">
            <div class="space-y-3">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-2 bg-gray-200 rounded w-1/2"></div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Tenant Details -->
      <div v-else-if="tenant" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Informações Básicas -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Informações Básicas</h3>
          </template>
          
          <div class="space-y-3">
            <div>
              <label class="text-xs font-medium text-gray-500">Proprietário</label>
              <p class="text-sm text-gray-900">{{ tenant.owner }}</p>
            </div>
            
            <div v-if="tenant.region">
              <label class="text-xs font-medium text-gray-500">Região</label>
              <p class="text-sm text-gray-900">{{ tenant.region }}</p>
            </div>
            
            <div v-if="tenant.datacenter">
              <label class="text-xs font-medium text-gray-500">Datacenter</label>
              <p class="text-sm text-gray-900">{{ tenant.datacenter }}</p>
            </div>
            
            <div v-if="tenant.billing_plan">
              <label class="text-xs font-medium text-gray-500">Plano de Cobrança</label>
              <p class="text-sm text-gray-900 capitalize">{{ tenant.billing_plan }}</p>
            </div>
            
            <div>
              <label class="text-xs font-medium text-gray-500">Criado em</label>
              <p class="text-sm text-gray-900">{{ formatDate(tenant.created_at) }}</p>
            </div>
          </div>
        </UCard>

        <!-- Quotas de Computação -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Recursos de Computação</h3>
          </template>
          
          <div class="space-y-4">
            <div v-if="tenant.quotas.compute.cpu_limit">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">CPU (vCPU)</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.cpu.current }}/{{ tenant.quota_status.cpu.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.cpu.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.compute.ram_limit">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">RAM (GB)</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.ram.current }}/{{ tenant.quota_status.ram.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.ram.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.compute.max_vms">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">VMs</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.vms.current }}/{{ tenant.quota_status.vms.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.vms.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.compute.max_containers">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Containers</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.containers.current }}/{{ tenant.quota_status.containers.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.containers.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Quotas de Storage -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Recursos de Storage</h3>
          </template>
          
          <div class="space-y-4">
            <div v-if="tenant.quotas.storage.max_storage_capacity">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Storage (GB)</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.storage.current }}/{{ tenant.quota_status.storage.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-indigo-500 to-indigo-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.storage.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.storage.max_volumes">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Volumes</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.volumes.current }}/{{ tenant.quota_status.volumes.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-yellow-500 to-yellow-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.volumes.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.storage.snapshot_limit">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Snapshots</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.snapshots.current }}/{{ tenant.quota_status.snapshots.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-pink-500 to-pink-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.snapshots.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Quotas de Rede -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Recursos de Rede</h3>
          </template>
          
          <div class="space-y-4">
            <div v-if="tenant.quotas.network.max_networks">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Redes</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.networks.current }}/{{ tenant.quota_status.networks.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-teal-500 to-teal-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.networks.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.network.max_floating_ips">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">IPs Flutuantes</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.floating_ips.current }}/{{ tenant.quota_status.floating_ips.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-cyan-500 to-cyan-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.floating_ips.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.network.max_load_balancers">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">Load Balancers</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.load_balancers.current }}/{{ tenant.quota_status.load_balancers.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-red-500 to-red-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.load_balancers.percentage}%` }"
                ></div>
              </div>
            </div>
            
            <div v-if="tenant.quotas.network.max_vlans">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-medium text-gray-500">VLANs</span>
                <span class="text-xs text-gray-600">{{ tenant.quota_status.vlans.current }}/{{ tenant.quota_status.vlans.limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-gradient-to-r from-orange-500 to-orange-600 h-2 rounded-full transition-all"
                  :style="{ width: `${tenant.quota_status.vlans.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Ações -->
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Ações</h3>
          </template>
          
          <div class="space-y-3">
            <UButton 
              @click="editTenant"
              color="gray" 
              variant="outline" 
              size="sm"
              class="w-full justify-start"
            >
              <UIcon name="i-heroicons-pencil" class="mr-2" />
              Editar Tenant
            </UButton>
            
            <UButton 
              @click="viewStatistics"
              color="gray" 
              variant="outline" 
              size="sm"
              class="w-full justify-start"
            >
              <UIcon name="i-heroicons-chart-bar" class="mr-2" />
              Ver Estatísticas
            </UButton>
            
            <UButton 
              @click="openSettings"
              color="gray" 
              variant="outline" 
              size="sm"
              class="w-full justify-start"
            >
              <UIcon name="i-heroicons-cog-6-tooth" class="mr-2" />
              Configurações
            </UButton>

            <UButton 
              @click="openPBM"
              color="gray" 
              variant="outline" 
              size="sm"
              class="w-full justify-start"
            >
              <UIcon name="i-heroicons-archive-box" class="mr-2" />
              PBM - Backup Manager
            </UButton>

            <UButton 
              @click="openPMO"
              color="gray" 
              variant="outline" 
              size="sm"
              class="w-full justify-start"
            >
              <UIcon name="i-heroicons-chart-pie" class="mr-2" />
              PMO - Platform Observability
            </UButton>
          </div>
        </UCard>

        <!-- Descrição -->
        <UCard v-if="tenant.description" class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Descrição</h3>
          </template>
          
          <p class="text-sm text-gray-600">{{ tenant.description }}</p>
        </UCard>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-exclamation-triangle" class="text-4xl text-red-300 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-600 mb-2">Tenant não encontrado</h3>
        <p class="text-sm text-gray-500 mb-4">O tenant solicitado não existe ou você não tem permissão para visualizá-lo.</p>
        <UButton 
          @click="$router.push('/dashboard/tenants')" 
          size="sm"
          class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white"
        >
          Voltar para Tenants
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()

// Reactive data
const tenant = ref(null)
const loading = ref(true)

// Get tenant ID from route
const tenantId = route.params.id as string

// Methods
const fetchTenant = async () => {
  try {
    loading.value = true
    const response = await $fetch(`${config.public.apiBase}/tenants/${tenantId}`)
    tenant.value = response
  } catch (error) {
    console.error('Failed to fetch tenant:', error)
    tenant.value = null
  } finally {
    loading.value = false
  }
}

// Action methods
const editTenant = () => {
  router.push(`/dashboard/tenants/${tenantId}/edit`)
}

const viewStatistics = () => {
  router.push(`/dashboard/tenants/${tenantId}/statistics`)
}

const openSettings = () => {
  router.push(`/dashboard/tenants/${tenantId}/settings`)
}

const openPBM = () => {
  // Futuro: PBM - Proxmox Backup Manager
  const toast = useToast()
  toast.add({
    title: 'PBM - Proxmox Backup Manager',
    description: 'Módulo em desenvolvimento. Disponível em breve.',
    color: 'blue',
    timeout: 3000
  })
}

const openPMO = () => {
  // Futuro: PMO - Proxmox Platform Observability
  const toast = useToast()
  toast.add({
    title: 'PMO - Platform Observability',
    description: 'Módulo em desenvolvimento. Disponível em breve.',
    color: 'blue',
    timeout: 3000
  })
}

// Utility functions
const getStatusColor = (status: string) => {
  const colors = {
    active: 'green',
    suspended: 'yellow',
    pending: 'blue',
    archived: 'gray'
  }
  return colors[status] || 'gray'
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: 'Ativo',
    suspended: 'Suspenso',
    pending: 'Pendente',
    archived: 'Arquivado'
  }
  return labels[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  fetchTenant()
})

// Meta tags
useHead({
  title: `${tenant.value?.name || 'Tenant'} - PCM`,
  meta: [
    { name: 'description', content: 'Detalhes do tenant no PCM' }
  ]
})
</script>