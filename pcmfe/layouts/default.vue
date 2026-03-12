<template>
  <div class="flex h-screen bg-[#f5f5f5]">
    <!-- Sidebar -->
    <aside class="w-80 bg-white border-r border-[#e5e5e5] flex flex-col shadow-sm">
      <!-- Logo & Brand -->
      <div class="p-6 border-b border-[#e5e5e5]">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-lg bg-white border border-[#e5e5e5] flex items-center justify-center">
            <img src="/favicon.svg" alt="PCM Logo" class="w-8 h-8" />
          </div>
          <div class="flex-1">
            <h1 class="text-sm font-bold text-[#E57000] uppercase tracking-wide leading-tight">Proxmox Center Manager</h1>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-4 py-6 space-y-6 overflow-y-auto">
        <!-- Infrastructure Section -->
        <div class="space-y-1">
          <div class="px-3 mb-3 flex items-center gap-2">
            <div class="w-1 h-4 bg-[#E57000] rounded-full"></div>
            <p class="text-[10px] font-bold text-[#000000] uppercase tracking-wider">
              Infraestrutura
            </p>
          </div>
          
          <NuxtLink 
            to="/dashboard" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path === '/dashboard' 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-squares-2x2" class="text-lg text-[#E57000]" 
                   :class="$route.path === '/dashboard' ? 'text-white' : 'text-[#E57000]'" />
            <span>Dashboard</span>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard/clusters" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/clusters') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-server" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/clusters') ? 'text-white' : 'text-[#E57000]'" />
            <span>Clusters</span>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard/tenants" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/tenants') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-building-office" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/tenants') ? 'text-white' : 'text-[#E57000]'" />
            <span>Tenants</span>
          </NuxtLink>
        </div>

        <!-- Resources Section -->
        <div class="space-y-1">
          <div class="px-3 mb-3 flex items-center gap-2">
            <div class="w-1 h-4 bg-[#E57000] rounded-full"></div>
            <p class="text-[10px] font-bold text-[#000000] uppercase tracking-wider">
              Recursos
            </p>
          </div>
          
          <NuxtLink 
            to="/dashboard/compute" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/compute') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-cube" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/compute') ? 'text-white' : 'text-[#E57000]'" />
            <span>Compute</span>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard/storage" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/storage') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-circle-stack" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/storage') ? 'text-white' : 'text-[#E57000]'" />
            <span>Storage</span>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard/network" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/network') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-globe-alt" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/network') ? 'text-white' : 'text-[#E57000]'" />
            <span>Network</span>
          </NuxtLink>
        </div>

        <!-- System Section -->
        <div class="space-y-1">
          <div class="px-3 mb-3 flex items-center gap-2">
            <div class="w-1 h-4 bg-[#E57000] rounded-full"></div>
            <p class="text-[10px] font-bold text-[#000000] uppercase tracking-wider">
              Sistema
            </p>
          </div>
          
          <NuxtLink 
            to="/dashboard/users" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/users') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-users" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/users') ? 'text-white' : 'text-[#E57000]'" />
            <span>Usuários</span>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard/settings" 
            class="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium"
            :class="$route.path.startsWith('/dashboard/settings') 
              ? 'bg-[#E57000] text-white' 
              : 'text-[#333333] hover:bg-[#f5f5f5]'"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="text-lg" 
                   :class="$route.path.startsWith('/dashboard/settings') ? 'text-white' : 'text-[#E57000]'" />
            <span>Configurações</span>
          </NuxtLink>
        </div>
      </nav>

      <!-- User Profile -->
      <div class="p-4 border-t border-[#e5e5e5] bg-[#fafafa]">
        <div class="flex items-center gap-3 p-3 rounded-lg bg-white border border-[#e5e5e5]">
          <div class="w-10 h-10 rounded-lg bg-[#E57000] flex items-center justify-center text-white font-bold text-sm">
            PA
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-bold text-[#000000] truncate">Provider Admin</p>
            <p class="text-[10px] text-[#666666] truncate">admin@pcm.local</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto bg-[#f5f5f5]">
      <slot />
    </main>
  </div>
</template>
