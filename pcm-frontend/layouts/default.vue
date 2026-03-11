<template>
  <div class="flex h-screen bg-white dark:bg-brand-black text-gray-900 dark:text-gray-100">
    <aside class="w-72 bg-white dark:bg-brand-black border-r border-gray-100 dark:border-white/5 flex flex-col">
      <div class="p-6 mb-4">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-brand-orange rounded-xl flex items-center justify-center">
            <UIcon name="i-heroicons-cpu-chip" class="text-black text-xl" />
          </div>
          <span class="text-2xl font-black text-black dark:text-white tracking-tighter">
            <span class="text-brand-orange">PCM</span>
          </span>
        </div>
      </div>

      <nav class="flex-1 px-4 py-4 space-y-8">
        <div class="space-y-1">
          <div class="px-4 mb-4">
            <p class="text-[8px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.4em]">
              Control Plane
            </p>
          </div>
          
          <UButton 
            to="/dashboard" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path === '/dashboard' }"
          >
            <UIcon name="i-heroicons-squares-2x2" class="mr-3" />
            Dashboard
          </UButton>
          
          <UButton 
            to="/dashboard/clusters" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/clusters') }"
          >
            <UIcon name="i-heroicons-server" class="mr-3" />
            Clusters
          </UButton>
          
          <UButton 
            to="/dashboard/tenants" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/tenants') }"
          >
            <UIcon name="i-heroicons-building-office" class="mr-3" />
            Tenants
          </UButton>
          
          <UButton 
            to="/dashboard/compute" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/compute') }"
          >
            <UIcon name="i-heroicons-cube" class="mr-3" />
            Compute
          </UButton>
          
          <UButton 
            to="/dashboard/storage" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/storage') }"
          >
            <UIcon name="i-heroicons-circle-stack" class="mr-3" />
            Storage
          </UButton>
          
          <UButton 
            to="/dashboard/network" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/network') }"
          >
            <UIcon name="i-heroicons-globe-alt" class="mr-3" />
            Network
          </UButton>
        </div>

        <div class="space-y-1">
          <div class="px-4 mb-4">
            <p class="text-[8px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.4em]">
              Sistema
            </p>
          </div>
          
          <UButton 
            to="/dashboard/users" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/users') }"
          >
            <UIcon name="i-heroicons-users" class="mr-3" />
            Usuários
          </UButton>
          
          <UButton 
            to="/dashboard/settings" 
            variant="ghost" 
            class="w-full justify-start"
            :class="{ 'bg-brand-orange/10 text-brand-orange': $route.path.startsWith('/dashboard/settings') }"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="mr-3" />
            Configurações
          </UButton>
        </div>
      </nav>

      <div class="p-4 border-t border-gray-100 dark:border-white/5">
        <div class="flex items-center gap-3 p-3 rounded-2xl bg-gray-50 dark:bg-white/5">
          <div class="w-8 h-8 rounded-lg bg-brand-orange flex items-center justify-center text-black font-black text-[10px]">
            PA
          </div>
          <div class="flex-1">
            <p class="text-[10px] font-black text-black dark:text-white uppercase">Provider Admin</p>
            <p class="text-[8px] text-gray-400 uppercase">Master Account</p>
          </div>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto bg-gray-50 dark:bg-brand-black">
      <slot />
    </main>
  </div>
</template>
