<template>
  <div class="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
    <div class="animate-pulse mb-8">
      <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/40">
        <UIcon name="i-heroicons-cpu-chip" class="text-white text-5xl" />
      </div>
    </div>
    
    <h1 class="text-5xl font-black text-white tracking-tighter mb-2">
      PCM
    </h1>
    <p class="text-gray-500 font-medium tracking-wide uppercase text-sm mb-2">
      Proxmox Center Manager
    </p>
    <p class="text-gray-600 text-xs">
      Cloud Control Plane
    </p>

    <div class="mt-12 w-48 h-1 bg-gray-800 rounded-full overflow-hidden">
      <div class="h-full bg-blue-500 animate-[loading_1.5s_ease-in-out_infinite]"></div>
    </div>

    <div class="mt-12">
      <UButton 
        to="/dashboard" 
        color="primary" 
        size="lg"
        class="bg-brand-orange hover:bg-brand-orange/90"
      >
        Acessar Dashboard
      </UButton>
    </div>
  </div>
</template>

<style scoped>
@keyframes loading {
  0%, 100% { width: 0%; margin-left: 0%; }
  50% { width: 100%; margin-left: 0%; }
}
</style>
