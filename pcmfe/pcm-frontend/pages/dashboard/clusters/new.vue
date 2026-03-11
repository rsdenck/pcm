<template>
  <div class="p-4 md:p-8 w-full max-w-4xl mx-auto">
    <header class="mb-10">
      <UButton to="/dashboard/clusters" color="gray" variant="ghost" class="mb-4">
        <UIcon name="i-heroicons-arrow-left" class="mr-2" />
        Voltar
      </UButton>
      <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
        Adicionar <span class="text-brand-orange">Cluster</span>
      </h1>
      <p class="text-gray-500 mt-2">Configure um novo cluster Proxmox</p>
    </header>

    <UCard>
      <form @submit.prevent="submitForm" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-bold text-black dark:text-white mb-2">Nome do Cluster</label>
            <UInput 
              v-model="form.name" 
              placeholder="Production Cluster" 
              size="lg"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-bold text-black dark:text-white mb-2">Tipo</label>
            <USelect 
              v-model="form.cluster_type" 
              :options="clusterTypes"
              size="lg"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-bold text-black dark:text-white mb-2">Hostname / IP</label>
            <UInput 
              v-model="form.hostname" 
              placeholder="192.168.130.20" 
              size="lg"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-bold text-black dark:text-white mb-2">Porta</label>
            <UInput 
              v-model.number="form.port" 
              type="number" 
              placeholder="8006" 
              size="lg"
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-bold text-black dark:text-white mb-2">API Token ID</label>
          <UInput 
            v-model="form.api_token_id" 
            placeholder="root@pam!pcm" 
            size="lg"
            required
          />
          <p class="text-xs text-gray-500 mt-1">Formato: user@realm!tokenname</p>
        </div>

        <div>
          <label class="block text-sm font-bold text-black dark:text-white mb-2">API Token Secret</label>
          <UInput 
            v-model="form.api_token_secret" 
            type="password" 
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" 
            size="lg"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-bold text-black dark:text-white mb-2">Tenant ID</label>
          <UInput 
            v-model="form.tenant_id" 
            placeholder="tenant-uuid" 
            size="lg"
            required
          />
          <p class="text-xs text-gray-500 mt-1">ID do tenant que gerenciará este cluster</p>
        </div>

        <div>
          <label class="block text-sm font-bold text-black dark:text-white mb-2">Descrição (Opcional)</label>
          <UTextarea 
            v-model="form.description" 
            placeholder="Cluster de produção principal" 
            rows="3"
          />
        </div>

        <div class="flex items-center gap-2">
          <UCheckbox v-model="form.verify_ssl" />
          <label class="text-sm text-gray-600 dark:text-gray-400">Verificar certificado SSL</label>
        </div>

        <div class="flex gap-4 pt-4">
          <UButton 
            type="submit" 
            color="primary" 
            size="lg" 
            class="bg-brand-orange hover:bg-brand-orange/90"
            :loading="submitting"
          >
            <UIcon name="i-heroicons-check" class="mr-2" />
            Adicionar Cluster
          </UButton>
          <UButton 
            to="/dashboard/clusters" 
            color="gray" 
            size="lg"
            variant="outline"
          >
            Cancelar
          </UButton>
        </div>
      </form>
    </UCard>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const router = useRouter()
const submitting = ref(false)

const clusterTypes = [
  { label: 'Proxmox VE', value: 'pve' },
  { label: 'Proxmox Backup Server', value: 'pbs' },
  { label: 'Proxmox Mail Gateway', value: 'pmg' }
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

const submitForm = async () => {
  submitting.value = true
  try {
    await $fetch(`${config.public.apiBase}/clusters`, {
      method: 'POST',
      body: form.value
    })
    router.push('/dashboard/clusters')
  } catch (error) {
    console.error('Failed to create cluster', error)
    alert('Erro ao criar cluster. Verifique os dados e tente novamente.')
  } finally {
    submitting.value = false
  }
}
</script>
