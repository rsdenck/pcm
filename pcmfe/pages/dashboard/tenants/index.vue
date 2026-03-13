<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <header class="mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">
              Tenants
            </h1>
            <p class="text-sm text-gray-600">
              Gerencie tenants e organizações da sua infraestrutura multi-tenant
            </p>
          </div>
          
          <div class="flex flex-col sm:flex-row gap-3">
            <UButton 
              @click="navigateToNew" 
              size="sm"
              class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-sm hover:shadow-md transition-all"
              :ui="{
                rounded: 'rounded-lg',
                size: { sm: 'text-sm px-4 py-2' }
              }"
            >
              <UIcon name="i-heroicons-plus" class="mr-2 text-sm" />
              Novo Tenant
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
                placeholder="Buscar tenants..." 
                size="md"
                class="w-full"
                :ui="{ 
                  base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                  rounded: 'rounded-lg',
                  size: { md: 'text-sm px-3 py-2' },
                  color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
                }"
              >
                <template #leading>
                  <UIcon name="i-heroicons-magnifying-glass" class="text-gray-400" />
                </template>
              </UInput>
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
                @click="refreshTenants" 
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

      <!-- Tenants Grid -->
      <div v-if="loading && tenants.length === 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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

      <div v-else-if="filteredTenants.length === 0 && !loading" class="text-center py-12">
        <UIcon name="i-heroicons-building-office" class="text-4xl text-gray-300 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-600 mb-2">Nenhum tenant encontrado</h3>
        <p class="text-sm text-gray-500 mb-4">
          {{ searchQuery ? 'Tente ajustar os filtros de busca' : 'Comece criando seu primeiro tenant' }}
        </p>
        <UButton 
          v-if="!searchQuery"
          @click="navigateToNew" 
          size="sm"
          class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white"
        >
          <UIcon name="i-heroicons-plus" class="mr-2" />
          Criar Primeiro Tenant
        </UButton>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard 
          v-for="tenant in filteredTenants" 
          :key="tenant.id"
          class="shadow-sm border border-gray-200 bg-white hover:shadow-md transition-all cursor-pointer"
          @click="navigateToTenant(tenant.id)"
        >
          <template #header>
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-[#E57000] to-[#FF8C00] flex items-center justify-center">
                  <UIcon name="i-heroicons-building-office" class="text-white text-lg" />
                </div>
                <div>
                  <h3 class="text-base font-semibold text-gray-900 truncate">{{ tenant.name }}</h3>
                  <p class="text-xs text-gray-500">{{ tenant.organization }}</p>
                </div>
              </div>
              
              <UBadge 
                :color="getStatusColor(tenant.status)" 
                variant="subtle"
                class="capitalize text-xs"
              >
                {{ getStatusLabel(tenant.status) }}
              </UBadge>
            </div>
          </template>

          <div class="space-y-3">
            <!-- Tenant Info -->
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-xs text-gray-600">
                <UIcon name="i-heroicons-user" class="text-gray-400" />
                <span>{{ tenant.owner }}</span>
              </div>
              
              <div v-if="tenant.region" class="flex items-center gap-2 text-xs text-gray-600">
                <UIcon name="i-heroicons-globe-alt" class="text-gray-400" />
                <span>{{ tenant.region }}</span>
                <span v-if="tenant.datacenter">/ {{ tenant.datacenter }}</span>
              </div>
              
              <div v-if="tenant.billing_plan" class="flex items-center gap-2 text-xs text-gray-600">
                <UIcon name="i-heroicons-credit-card" class="text-gray-400" />
                <span class="capitalize">{{ tenant.billing_plan }}</span>
              </div>
            </div>

            <!-- Resource Usage -->
            <div class="space-y-2">
              <h4 class="text-xs font-medium text-gray-700">Uso de Recursos</h4>
              
              <div class="space-y-1">
                <div v-if="tenant.quotas.compute.cpu_limit" class="flex items-center justify-between text-xs">
                  <span class="text-gray-600">CPU</span>
                  <div class="flex items-center gap-2">
                    <div class="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        class="h-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] transition-all"
                        :style="{ width: `${getCpuUsagePercentage(tenant)}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-500 w-8 text-right">
                      {{ getCpuUsagePercentage(tenant) }}%
                    </span>
                  </div>
                </div>
                
                <div v-if="tenant.quotas.compute.ram_limit" class="flex items-center justify-between text-xs">
                  <span class="text-gray-600">RAM</span>
                  <div class="flex items-center gap-2">
                    <div class="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all"
                        :style="{ width: `${getRamUsagePercentage(tenant)}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-500 w-8 text-right">
                      {{ getRamUsagePercentage(tenant) }}%
                    </span>
                  </div>
                </div>
                
                <div v-if="tenant.quotas.storage.max_storage_capacity" class="flex items-center justify-between text-xs">
                  <span class="text-gray-600">Storage</span>
                  <div class="flex items-center gap-2">
                    <div class="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        class="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all"
                        :style="{ width: `${getStorageUsagePercentage(tenant)}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-500 w-8 text-right">
                      {{ getStorageUsagePercentage(tenant) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Stats -->
            <div class="grid grid-cols-3 gap-2 pt-2 border-t border-gray-100">
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ tenant.quota_status.vms?.current || 0 }}</div>
                <div class="text-xs text-gray-500">VMs</div>
              </div>
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ tenant.quota_status.containers?.current || 0 }}</div>
                <div class="text-xs text-gray-500">Containers</div>
              </div>
              <div class="text-center">
                <div class="text-sm font-semibold text-gray-900">{{ tenant.quota_status.networks?.current || 0 }}</div>
                <div class="text-xs text-gray-500">Networks</div>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">
                Criado em {{ formatDate(tenant.created_at) }}
              </span>
              
              <div class="flex gap-1">
                <UButton 
                  @click.stop="editTenant(tenant.id)"
                  color="gray" 
                  variant="ghost" 
                  size="xs"
                  class="hover:bg-gray-50"
                >
                  <UIcon name="i-heroicons-pencil" />
                </UButton>
                
                <UButton 
                  @click.stop="viewTenantStats(tenant.id)"
                  color="gray" 
                  variant="ghost" 
                  size="xs"
                  class="hover:bg-gray-50"
                >
                  <UIcon name="i-heroicons-chart-bar" />
                </UButton>
              </div>
            </div>
          </template>
        </UCard>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTenants.length > 0" class="mt-8 flex justify-center">
        <UPagination 
          v-model="currentPage" 
          :page-count="pageSize" 
          :total="totalTenants"
          class="shadow-lg"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const router = useRouter()

// Reactive data
const tenants = ref([])
const loading = ref(true)
const searchQuery = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(12)
const totalTenants = ref(0)

// Status options for filter
const statusOptions = [
  { label: 'Todos os Status', value: 'all' },
  { label: 'Ativo', value: 'active' },
  { label: 'Suspenso', value: 'suspended' },
  { label: 'Pendente', value: 'pending' },
  { label: 'Arquivado', value: 'archived' }
]

// Computed properties
const filteredTenants = computed(() => {
  let filtered = tenants.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tenant => 
      tenant.name.toLowerCase().includes(query) ||
      tenant.organization.toLowerCase().includes(query) ||
      tenant.owner.toLowerCase().includes(query)
    )
  }

  // Filter by status
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(tenant => tenant.status === statusFilter.value)
  }

  return filtered
})

// Methods
const navigateToNew = () => {
  console.log('Botão Novo Tenant clicado!')
  try {
    router.push('/dashboard/tenants/new')
    console.log('Navegação iniciada para /dashboard/tenants/new')
  } catch (error) {
    console.error('Erro na navegação:', error)
  }
}

const fetchTenants = async () => {
  try {
    loading.value = true
    const response = await $fetch(`${config.public.apiBase}/tenants/`, {
      query: {
        limit: 100,
        offset: 0
      }
    })
    
    tenants.value = response || []
    totalTenants.value = response?.length || 0
  } catch (error) {
    console.error('Failed to fetch tenants:', error)
    tenants.value = []
    const toast = useToast()
    toast.add({
      title: 'Erro ao Carregar Tenants',
      description: 'Não foi possível carregar a lista de tenants.',
      color: 'red',
      timeout: 5000
    })
  } finally {
    loading.value = false
  }
}

const refreshTenants = () => {
  fetchTenants()
}

const navigateToTenant = (tenantId: string) => {
  // Abrir em nova aba conforme solicitado
  const url = `/dashboard/tenants/${tenantId}`
  window.open(url, '_blank')
}

const editTenant = (tenantId: string) => {
  router.push(`/dashboard/tenants/${tenantId}/edit`)
}

const viewTenantStats = (tenantId: string) => {
  router.push(`/dashboard/tenants/${tenantId}/statistics`)
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

const getCpuUsagePercentage = (tenant: any) => {
  const current = tenant.quota_status?.cpu?.current || 0
  const limit = tenant.quota_status?.cpu?.limit || 1
  return Math.round((current / limit) * 100)
}

const getRamUsagePercentage = (tenant: any) => {
  const current = tenant.quota_status?.ram?.current || 0
  const limit = tenant.quota_status?.ram?.limit || 1
  return Math.round((current / limit) * 100)
}

const getStorageUsagePercentage = (tenant: any) => {
  const current = tenant.quota_status?.storage?.current || 0
  const limit = tenant.quota_status?.storage?.limit || 1
  return Math.round((current / limit) * 100)
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
  fetchTenants()
})

// Meta tags
useHead({
  title: 'Tenants - PCM',
  meta: [
    { name: 'description', content: 'Gerencie tenants e organizações da sua infraestrutura multi-tenant' }
  ]
})
</script>