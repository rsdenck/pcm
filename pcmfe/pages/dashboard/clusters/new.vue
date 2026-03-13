<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header simples -->
      <header class="mb-6">
        <div class="flex items-center gap-4 mb-4">
          <UButton 
            to="/dashboard/clusters" 
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
            Adicionar Cluster
          </h1>
          <p class="text-sm text-gray-600">
            Configure um novo cluster Proxmox
          </p>
        </div>
      </header>

      <!-- Formulário Principal -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Formulário (ocupa mais espaço) -->
        <div class="lg:col-span-3">
          <UCard class="shadow-sm border border-gray-200 bg-white">
            <form @submit.prevent="submitForm" class="space-y-6">
              <!-- Informações Básicas -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  Informações Básicas
                </h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Nome do Cluster *
                    </label>
                    <UInput 
                      v-model="form.name" 
                      placeholder="Ex: Cluster Produção" 
                      required
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Tipo do Cluster *
                    </label>
                    <USelect 
                      v-model="form.cluster_type" 
                      :options="clusterTypes"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Descrição
                  </label>
                  <UTextarea 
                    v-model="form.description" 
                    placeholder="Descrição opcional do cluster..." 
                    rows="3"
                  />
                </div>
              </div>

              <!-- Conexão -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  Configuração de Conexão
                </h3>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Hostname / Endereço IP *
                    </label>
                    <UInput 
                      v-model="form.hostname" 
                      placeholder="192.168.130.20 ou cluster.exemplo.com" 
                      required
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Porta *
                    </label>
                    <UInput 
                      v-model.number="form.port" 
                      type="number" 
                      placeholder="8006" 
                      required
                    />
                  </div>
                </div>
              </div>

              <!-- Autenticação -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  Autenticação API
                </h3>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      API Token ID *
                    </label>
                    <UInput 
                      v-model="form.api_token_id" 
                      placeholder="root@pam!pcm-token" 
                      required
                      class="font-mono"
                    />
                    <p class="text-xs text-gray-500 mt-1">Formato: usuário@realm!nome-do-token</p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      API Token Secret *
                    </label>
                    <UInput 
                      v-model="form.api_token_secret" 
                      type="password" 
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" 
                      required
                      class="font-mono"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Tenant ID *
                    </label>
                    <UInput 
                      v-model="form.tenant_id" 
                      placeholder="tenant-uuid-aqui" 
                      required
                      class="font-mono"
                    />
                    <p class="text-xs text-gray-500 mt-1">ID do tenant que gerenciará este cluster</p>
                  </div>
                </div>
              </div>

              <!-- Configurações Avançadas -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  Configurações Avançadas
                </h3>

                <div class="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                  <UCheckbox v-model="form.verify_ssl" />
                  <div>
                    <label class="block text-sm font-medium text-gray-700">
                      Verificar Certificado SSL
                    </label>
                    <p class="text-xs text-gray-500 mt-1">
                      Ative para validar certificados SSL/TLS (recomendado para produção)
                    </p>
                  </div>
                </div>
              </div>

              <!-- Botões de Ação -->
              <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
                <UButton 
                  type="submit" 
                  :loading="submitting"
                  size="sm"
                  class="flex-1 bg-[#E57000] hover:bg-[#CC6600] text-white"
                >
                  <UIcon name="i-heroicons-check-circle" class="mr-2" />
                  {{ submitting ? 'Adicionando...' : 'Adicionar Cluster' }}
                </UButton>
                
                <UButton 
                  to="/dashboard/clusters" 
                  color="gray" 
                  variant="outline"
                  size="sm"
                  class="flex-1 sm:flex-none"
                >
                  Cancelar
                </UButton>
              </div>
            </form>
          </UCard>
        </div>

        <!-- Painel de Ajuda Recolhível -->
        <div class="space-y-4">
          <!-- Toggle para mostrar/ocultar ajuda -->
          <UButton 
            @click="showHelp = !showHelp"
            color="gray"
            variant="outline"
            size="sm"
            class="w-full justify-between border border-gray-200"
          >
            <span class="flex items-center gap-2">
              <UIcon name="i-heroicons-question-mark-circle" />
              <span class="text-sm">{{ showHelp ? 'Ocultar Ajuda' : 'Mostrar Ajuda' }}</span>
            </span>
            <UIcon :name="showHelp ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" />
          </UButton>

          <!-- Cards de Ajuda (Recolhíveis) -->
          <div v-show="showHelp" class="space-y-4">
            <UCard class="shadow-sm border border-gray-200 bg-white">
              <template #header>
                <h3 class="text-base font-semibold text-gray-900">Ajuda</h3>
              </template>

              <div class="space-y-3">
                <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 class="text-sm font-medium text-blue-900 mb-2">API Token</h4>
                  <ol class="text-xs text-blue-800 space-y-1 list-decimal list-inside">
                    <li>Acesse o Proxmox Web Interface</li>
                    <li>Vá em Datacenter → Permissions → API Tokens</li>
                    <li>Clique em "Add" para criar um novo token</li>
                    <li>Copie o Token ID e Secret gerados</li>
                  </ol>
                </div>

                <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                  <h4 class="text-sm font-medium text-green-900 mb-2">Portas Padrão</h4>
                  <ul class="text-xs text-green-800 space-y-1">
                    <li><strong>Proxmox VE:</strong> 8006</li>
                    <li><strong>Proxmox Backup:</strong> 8007</li>
                    <li><strong>Proxmox Mail:</strong> 8006</li>
                  </ul>
                </div>
              </div>
            </UCard>

            <!-- Teste de Conexão -->
            <UCard class="shadow-sm border border-gray-200 bg-white">
              <template #header>
                <h3 class="text-base font-semibold text-gray-900">Teste de Conexão</h3>
              </template>

              <div class="space-y-3">
                <UButton 
                  @click="testConnection" 
                  :loading="testing"
                  :disabled="!canTest"
                  color="gray"
                  variant="outline"
                  size="sm"
                  class="w-full"
                >
                  <UIcon name="i-heroicons-wifi" class="mr-2" />
                  {{ testing ? 'Testando...' : 'Testar Conexão' }}
                </UButton>

                <div v-if="testResult" class="p-3 rounded-lg" :class="testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
                  <div class="flex items-center gap-2 mb-2">
                    <UIcon 
                      :name="testResult.success ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" 
                      :class="testResult.success ? 'text-green-600' : 'text-red-600'"
                    />
                    <span class="text-sm font-medium" :class="testResult.success ? 'text-green-900' : 'text-red-900'">
                      {{ testResult.success ? 'Conexão Bem-sucedida!' : 'Falha na Conexão' }}
                    </span>
                  </div>
                  <p class="text-xs" :class="testResult.success ? 'text-green-800' : 'text-red-800'">
                    {{ testResult.message }}
                  </p>
                </div>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const router = useRouter()
const submitting = ref(false)
const testing = ref(false)
const testResult = ref<{ success: boolean; message: string } | null>(null)
const showHelp = ref(false)

const clusterTypes = [
  { 
    label: 'Proxmox VE', 
    value: 'pve',
    icon: 'i-heroicons-server',
    description: 'Virtualização e containers'
  },
  { 
    label: 'Proxmox Backup Server', 
    value: 'pbs',
    icon: 'i-heroicons-archive-box',
    description: 'Servidor de backup'
  },
  { 
    label: 'Proxmox Mail Gateway', 
    value: 'pmg',
    icon: 'i-heroicons-envelope',
    description: 'Gateway de email'
  }
]

const form = ref({
  name: '',
  hostname: '',
  port: 8006,
  cluster_type: 'pve',
  api_token_id: '',
  api_token_secret: '',
  tenant_id: '',
  description: '',
  verify_ssl: false
})

// Computed para verificar se pode testar conexão
const canTest = computed(() => {
  return form.value.hostname && 
         form.value.port && 
         form.value.api_token_id && 
         form.value.api_token_secret
})

// Função para testar conexão
const testConnection = async () => {
  if (!canTest.value) return
  
  testing.value = true
  testResult.value = null
  
  try {
    const response = await $fetch(`${config.public.apiBase}/clusters/test-connection`, {
      method: 'POST',
      body: {
        hostname: form.value.hostname,
        port: form.value.port,
        api_token_id: form.value.api_token_id,
        api_token_secret: form.value.api_token_secret,
        verify_ssl: form.value.verify_ssl
      }
    })
    
    testResult.value = {
      success: true,
      message: `Conectado com sucesso! Versão: ${response.version || 'N/A'}`
    }
  } catch (error: any) {
    testResult.value = {
      success: false,
      message: error.data?.message || 'Erro de conexão. Verifique os dados e tente novamente.'
    }
  } finally {
    testing.value = false
  }
}

// Função para submeter o formulário
const submitForm = async () => {
  submitting.value = true
  
  try {
    await $fetch(`${config.public.apiBase}/clusters`, {
      method: 'POST',
      body: form.value
    })
    
    // Mostrar notificação de sucesso
    const toast = useToast()
    toast.add({
      title: 'Cluster Adicionado!',
      description: `O cluster "${form.value.name}" foi configurado com sucesso.`,
      color: 'green',
      timeout: 5000
    })
    
    // Redirecionar para a lista
    await router.push('/dashboard/clusters')
  } catch (error: any) {
    console.error('Failed to create cluster', error)
    
    // Mostrar notificação de erro
    const toast = useToast()
    toast.add({
      title: 'Erro ao Adicionar Cluster',
      description: error.data?.message || 'Verifique os dados e tente novamente.',
      color: 'red',
      timeout: 8000
    })
  } finally {
    submitting.value = false
  }
}

// Watchers para limpar resultado do teste quando dados mudam
watch([
  () => form.value.hostname,
  () => form.value.port,
  () => form.value.api_token_id,
  () => form.value.api_token_secret
], () => {
  testResult.value = null
})

// Meta tags para SEO
useHead({
  title: 'Adicionar Cluster - PCM',
  meta: [
    { name: 'description', content: 'Configure um novo cluster Proxmox no PCM' }
  ]
})
</script>
