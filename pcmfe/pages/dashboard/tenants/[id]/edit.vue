<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-6">
    <div class="max-w-4xl mx-auto">
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
        
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">
            Editar Tenant
          </h1>
          <p class="text-sm text-gray-600">
            Modifique as configurações do tenant
          </p>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="loading" class="animate-pulse">
        <UCard class="shadow-sm border border-gray-200 bg-white h-64">
          <div class="space-y-4">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </UCard>
      </div>

      <!-- Edit Form -->
      <div v-else-if="tenant">
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <h3 class="text-base font-semibold text-gray-900">Informações do Tenant</h3>
          </template>
          
          <form @submit.prevent="updateTenant" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Nome *</label>
                <UInput v-model="form.name" size="md" required />
              </div>
              
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Organização *</label>
                <UInput v-model="form.organization" size="md" required />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Proprietário *</label>
                <UInput v-model="form.owner" size="md" required />
              </div>
              
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Status</label>
                <USelect 
                  v-model="form.status" 
                  :options="statusOptions"
                  size="md"
                />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Descrição</label>
              <UTextarea v-model="form.description" rows="3" />
            </div>

            <div class="flex gap-3 pt-4 border-t border-gray-100">
              <UButton 
                type="submit" 
                :loading="saving"
                size="sm"
                class="bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white"
              >
                {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
              </UButton>
              
              <UButton 
                @click="$router.back()"
                color="gray"
                variant="outline"
                size="sm"
              >
                Cancelar
              </UButton>
            </div>
          </form>
        </UCard>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-exclamation-triangle" class="text-4xl text-red-300 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-600 mb-2">Erro ao carregar tenant</h3>
        <p class="text-sm text-gray-500">Não foi possível carregar os dados do tenant.</p>
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
const saving = ref(false)

// Get tenant ID from route
const tenantId = route.params.id as string

// Form data
const form = ref({
  name: '',
  organization: '',
  owner: '',
  status: 'active',
  description: ''
})

const statusOptions = [
  { label: 'Ativo', value: 'active' },
  { label: 'Suspenso', value: 'suspended' },
  { label: 'Pendente', value: 'pending' },
  { label: 'Arquivado', value: 'archived' }
]

// Methods
const fetchTenant = async () => {
  try {
    loading.value = true
    const response = await $fetch(`${config.public.apiBase}/tenants/${tenantId}`)
    tenant.value = response
    
    // Populate form
    form.value = {
      name: response.name,
      organization: response.organization,
      owner: response.owner,
      status: response.status,
      description: response.description || ''
    }
  } catch (error) {
    console.error('Failed to fetch tenant:', error)
    tenant.value = null
  } finally {
    loading.value = false
  }
}

const updateTenant = async () => {
  try {
    saving.value = true
    
    await $fetch(`${config.public.apiBase}/tenants/${tenantId}`, {
      method: 'PUT',
      body: form.value
    })
    
    const toast = useToast()
    toast.add({
      title: 'Tenant Atualizado',
      description: 'As alterações foram salvas com sucesso.',
      color: 'green',
      timeout: 3000
    })
    
    router.back()
  } catch (error) {
    console.error('Failed to update tenant:', error)
    const toast = useToast()
    toast.add({
      title: 'Erro ao Atualizar',
      description: 'Não foi possível salvar as alterações.',
      color: 'red',
      timeout: 5000
    })
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchTenant()
})

// Meta tags
useHead({
  title: `Editar Tenant - PCM`,
  meta: [
    { name: 'description', content: 'Editar configurações do tenant' }
  ]
})
</script>