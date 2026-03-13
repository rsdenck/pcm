<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header com navegação -->
      <header class="mb-6">
        <div class="flex items-center gap-4 mb-4">
          <UButton 
            to="/dashboard/tenants" 
            color="gray" 
            variant="ghost" 
            size="sm"
          >
            <UIcon name="i-heroicons-arrow-left" class="mr-2" />
            Voltar aos Tenants
          </UButton>
        </div>
        
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">
            Criar Novo Tenant
          </h1>
          <p class="text-sm text-gray-600">
            Configure um novo tenant para isolamento de recursos e multi-tenancy
          </p>
        </div>
      </header>

      <!-- Template Selection -->
      <div v-if="showTemplates" class="mb-6">
        <UCard class="shadow-sm border border-gray-200 bg-white">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center">
                  <UIcon name="i-heroicons-template" class="text-white text-xl" />
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-900">Templates de Tenant</h2>
                  <p class="text-sm text-gray-500">Escolha um template ou configure manualmente</p>
                </div>
              </div>
              
              <UButton 
                @click="showTemplates = false"
                color="gray"
                variant="ghost"
              >
                Configuração Manual
              </UButton>
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div 
              v-for="template in templates" 
              :key="template.name"
              @click="applyTemplate(template)"
              class="p-4 border-2 border-gray-200 rounded-xl hover:border-[#E57000] hover:bg-orange-50 cursor-pointer transition-all"
            >
              <h3 class="font-semibold text-gray-900 mb-2">{{ template.name }}</h3>
              <p class="text-sm text-gray-600 mb-3">{{ template.description }}</p>
              
              <div class="space-y-1 text-xs text-gray-500">
                <div>CPU: {{ template.quotas.cpu_limit }} vCPU</div>
                <div>RAM: {{ template.quotas.ram_limit }} GB</div>
                <div>VMs: {{ template.quotas.max_vms }}</div>
                <div>Storage: {{ template.quotas.max_storage_capacity }} GB</div>
              </div>
              
              <UBadge 
                :color="getBillingPlanColor(template.billing_plan)" 
                variant="subtle" 
                class="mt-2 capitalize"
              >
                {{ template.billing_plan }}
              </UBadge>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Formulário Principal -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Formulário -->
        <div class="lg:col-span-2">
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <template #header>
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-[#E57000] to-[#FF8C00] flex items-center justify-center">
                  <UIcon name="i-heroicons-building-office" class="text-white text-xl" />
                </div>
                <div>
                  <h2 class="text-base font-semibold text-gray-900">Configuração do Tenant</h2>
                  <p class="text-xs text-gray-500">Preencha as informações básicas</p>
                </div>
              </div>
            </template>

            <form @submit.prevent="submitForm" class="space-y-8">
              <!-- Seção: Informações Básicas -->
              <div class="space-y-6">
                <div class="flex items-center gap-3 pb-3 border-b border-gray-200">
                  <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <UIcon name="i-heroicons-information-circle" class="text-blue-600 text-lg" />
                  </div>
                  <h3 class="text-lg font-semibold text-gray-900">Informações Básicas</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Nome do Tenant *
                    </label>
                    <UInput 
                      v-model="form.name" 
                      placeholder="Ex: Acme Corporation" 
                      size="md"
                      required
                      class="transition-all focus:ring-2 focus:ring-[#E57000]/20"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Organização *
                    </label>
                    <UInput 
                      v-model="form.organization" 
                      placeholder="Nome da organização" 
                      size="md"
                      required
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Proprietário *
                    </label>
                    <UInput 
                      v-model="form.owner" 
                      placeholder="Nome do responsável" 
                      size="md"
                      required
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Plano de Billing
                    </label>
                    <USelect 
                      v-model="form.billing_plan" 
                      :options="billingPlans"
                      size="md"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Região
                    </label>
                    <UInput 
                      v-model="form.region" 
                      placeholder="Ex: us-east-1" 
                      size="md"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Datacenter
                    </label>
                    <UInput 
                      v-model="form.datacenter" 
                      placeholder="Ex: DC-01" 
                      size="md"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <label class="block text-xs font-medium text-gray-500">
                    Descrição
                  </label>
                  <UTextarea 
                    v-model="form.description" 
                    placeholder="Descrição do tenant..." 
                    rows="3"
                    class="transition-all"
                    :ui="textareaStyles"
                  />
                </div>
              </div>

              <!-- Seção: Quotas de Computação -->
              <div class="space-y-6">
                <div class="flex items-center gap-3 pb-3 border-b border-gray-200">
                  <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                    <UIcon name="i-heroicons-cpu-chip" class="text-green-600 text-lg" />
                  </div>
                  <h3 class="text-lg font-semibold text-gray-900">Quotas de Computação</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      CPU Limit (vCPU)
                    </label>
                    <UInput 
                      v-model.number="form.cpu_limit" 
                      type="number" 
                      placeholder="16" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      RAM Limit (GB)
                    </label>
                    <UInput 
                      v-model.number="form.ram_limit" 
                      type="number" 
                      placeholder="64" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo VMs
                    </label>
                    <UInput 
                      v-model.number="form.max_vms" 
                      type="number" 
                      placeholder="10" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo Containers
                    </label>
                    <UInput 
                      v-model.number="form.max_containers" 
                      type="number" 
                      placeholder="20" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>
              </div>

              <!-- Seção: Quotas de Storage -->
              <div class="space-y-6">
                <div class="flex items-center gap-3 pb-3 border-b border-gray-200">
                  <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                    <UIcon name="i-heroicons-server-stack" class="text-purple-600 text-lg" />
                  </div>
                  <h3 class="text-lg font-semibold text-gray-900">Quotas de Storage</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Capacidade Máxima (GB)
                    </label>
                    <UInput 
                      v-model.number="form.max_storage_capacity" 
                      type="number" 
                      placeholder="1000" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo Volumes
                    </label>
                    <UInput 
                      v-model.number="form.max_volumes" 
                      type="number" 
                      placeholder="50" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Limite de Snapshots
                    </label>
                    <UInput 
                      v-model.number="form.snapshot_limit" 
                      type="number" 
                      placeholder="100" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>
              </div>

              <!-- Seção: Quotas de Rede -->
              <div class="space-y-6">
                <div class="flex items-center gap-3 pb-3 border-b border-gray-200">
                  <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                    <UIcon name="i-heroicons-globe-alt" class="text-indigo-600 text-lg" />
                  </div>
                  <h3 class="text-lg font-semibold text-gray-900">Quotas de Rede</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo Networks
                    </label>
                    <UInput 
                      v-model.number="form.max_networks" 
                      type="number" 
                      placeholder="10" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo IPs Flutuantes
                    </label>
                    <UInput 
                      v-model.number="form.max_floating_ips" 
                      type="number" 
                      placeholder="10" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo Load Balancers
                    </label>
                    <UInput 
                      v-model.number="form.max_load_balancers" 
                      type="number" 
                      placeholder="5" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>

                  <div class="space-y-2">
                    <label class="block text-xs font-medium text-gray-500">
                      Máximo VLANs
                    </label>
                    <UInput 
                      v-model.number="form.max_vlans" 
                      type="number" 
                      placeholder="25" 
                      size="md"
                      min="0"
                      class="transition-all"
                      :ui="inputStyles"
                    />
                  </div>
                </div>
              </div>

              <!-- Botões de Ação -->
              <div class="flex flex-col sm:flex-row gap-4 pt-8 border-t border-gray-200">
                <UButton 
                  type="submit" 
                  size="sm" 
                  :loading="submitting"
                  class="flex-1 bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-sm hover:shadow-md transition-all"
                  :ui="{
                    rounded: 'rounded-lg',
                    size: { sm: 'text-sm px-4 py-2' }
                  }"
                >
                  <UIcon name="i-heroicons-check-circle" class="mr-3 text-xl" />
                  {{ submitting ? 'Criando...' : 'Criar Tenant' }}
                </UButton>
                
                <UButton 
                  to="/dashboard/tenants" 
                  color="gray" 
                  size="xl"
                  variant="outline"
                  class="flex-1 sm:flex-none border-2 hover:bg-gray-50 transition-all"
                  :ui="{
                    rounded: 'rounded-xl',
                    size: { xl: 'text-lg px-8 py-4' }
                  }"
                >
                  Cancelar
                </UButton>
              </div>
            </form>
          </UCard>
        </div>

        <!-- Painel Lateral de Ajuda -->
        <div class="space-y-6">
          <!-- Card de Templates -->
          <UCard v-if="!showTemplates" class="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <template #header>
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <UIcon name="i-heroicons-template" class="text-blue-600 text-lg" />
                </div>
                <h3 class="text-lg font-semibold text-gray-900">Templates</h3>
              </div>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-gray-600">
                Use templates pré-configurados para acelerar a criação de tenants.
              </p>
              
              <UButton 
                @click="showTemplates = true"
                color="gray"
                variant="outline"
                size="md"
                class="w-full"
              >
                <UIcon name="i-heroicons-template" class="mr-2" />
                Ver Templates
              </UButton>
            </div>
          </UCard>

          <!-- Card de Ajuda -->
          <UCard class="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <template #header>
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <UIcon name="i-heroicons-question-mark-circle" class="text-green-600 text-lg" />
                </div>
                <h3 class="text-lg font-semibold text-gray-900">Guia de Quotas</h3>
              </div>
            </template>

            <div class="space-y-4">
              <div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 class="font-semibold text-blue-900 mb-2">Computação</h4>
                <ul class="text-sm text-blue-800 space-y-1">
                  <li><strong>CPU:</strong> Núcleos virtuais disponíveis</li>
                  <li><strong>RAM:</strong> Memória em gigabytes</li>
                  <li><strong>VMs:</strong> Máquinas virtuais simultâneas</li>
                  <li><strong>Containers:</strong> Containers LXC</li>
                </ul>
              </div>

              <div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <h4 class="font-semibold text-purple-900 mb-2">Storage</h4>
                <ul class="text-sm text-purple-800 space-y-1">
                  <li><strong>Capacidade:</strong> Espaço total em GB</li>
                  <li><strong>Volumes:</strong> Discos adicionais</li>
                  <li><strong>Snapshots:</strong> Backups pontuais</li>
                </ul>
              </div>

              <div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <h4 class="font-semibold text-indigo-900 mb-2">Rede</h4>
                <ul class="text-sm text-indigo-800 space-y-1">
                  <li><strong>Networks:</strong> Redes virtuais</li>
                  <li><strong>IPs Flutuantes:</strong> IPs públicos</li>
                  <li><strong>Load Balancers:</strong> Balanceadores</li>
                  <li><strong>VLANs:</strong> Segmentação de rede</li>
                </ul>
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const router = useRouter()

// Reactive data
const submitting = ref(false)
const showTemplates = ref(true)
const templates = ref([])

// Form data
const form = ref({
  name: '',
  organization: '',
  owner: '',
  description: '',
  region: '',
  datacenter: '',
  billing_plan: '',
  
  // Compute quotas
  cpu_limit: null,
  ram_limit: null,
  max_vms: null,
  max_containers: null,
  
  // Storage quotas
  max_storage_capacity: null,
  max_volumes: null,
  snapshot_limit: null,
  
  // Network quotas
  max_networks: null,
  max_floating_ips: null,
  max_load_balancers: null,
  max_vlans: null,
  
  // Configuration
  configuration: {},
  tenant_metadata: {},
  network_isolation: {}
})

// Options
const billingPlans = [
  { label: 'Selecione um plano', value: '' },
  { label: 'Básico', value: 'basic' },
  { label: 'Padrão', value: 'standard' },
  { label: 'Premium', value: 'premium' },
  { label: 'Enterprise', value: 'enterprise' },
  { label: 'Customizado', value: 'custom' }
]

// Styles
const inputStyles = {
  base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
  rounded: 'rounded-xl',
  size: { lg: 'text-base px-4 py-3' },
  color: { white: 'bg-white shadow-sm ring-1 ring-gray-300 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
}

const textareaStyles = {
  base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
  rounded: 'rounded-xl',
  size: { base: 'text-base px-4 py-3' },
  color: { white: 'bg-white shadow-sm ring-1 ring-gray-300 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
}

// Methods
const fetchTemplates = async () => {
  try {
    const response = await $fetch(`${config.public.apiBase}/tenants/templates/list`)
    templates.value = response || []
  } catch (error) {
    console.error('Failed to fetch templates:', error)
    templates.value = []
  }
}

const applyTemplate = (template: any) => {
  // Apply template quotas to form
  Object.assign(form.value, template.quotas)
  form.value.billing_plan = template.billing_plan
  
  showTemplates.value = false
  
  const toast = useToast()
  toast.add({
    title: 'Template Aplicado',
    description: `Template "${template.name}" foi aplicado com sucesso.`,
    color: 'green',
    timeout: 3000
  })
}

const getBillingPlanColor = (plan: string) => {
  const colors = {
    basic: 'blue',
    standard: 'green',
    premium: 'purple',
    enterprise: 'orange',
    custom: 'gray'
  }
  return colors[plan] || 'gray'
}

const submitForm = async () => {
  submitting.value = true
  
  try {
    // Validar campos obrigatórios
    if (!form.value.name || !form.value.organization || !form.value.owner) {
      const toast = useToast()
      toast.add({
        title: 'Campos Obrigatórios',
        description: 'Preencha todos os campos obrigatórios (Nome, Organização e Proprietário).',
        color: 'red',
        timeout: 5000
      })
      return
    }
    
    // Remove empty values
    const cleanForm = Object.fromEntries(
      Object.entries(form.value).filter(([_, value]) => 
        value !== null && value !== undefined && value !== ''
      )
    )
    
    const response = await $fetch(`${config.public.apiBase}/tenants/`, {
      method: 'POST',
      body: cleanForm
    })
    
    const toast = useToast()
    toast.add({
      title: 'Tenant Criado!',
      description: `O tenant "${form.value.name}" foi criado com sucesso.`,
      color: 'green',
      timeout: 5000
    })
    
    await router.push('/dashboard/tenants')
  } catch (error: any) {
    console.error('Failed to create tenant:', error)
    
    const toast = useToast()
    toast.add({
      title: 'Erro ao Criar Tenant',
      description: error.data?.detail || error.message || 'Verifique os dados e tente novamente.',
      color: 'red',
      timeout: 8000
    })
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchTemplates()
})

// Meta tags
useHead({
  title: 'Criar Tenant - PCM',
  meta: [
    { name: 'description', content: 'Crie um novo tenant para isolamento de recursos e multi-tenancy' }
  ]
})
</script>
