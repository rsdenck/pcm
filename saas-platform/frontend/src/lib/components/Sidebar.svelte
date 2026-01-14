<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { theme } from '$lib/stores/theme';
    import { 
        LayoutDashboard, 
        Server, 
        Settings, 
        Users, 
        Bell, 
        Search,
        LogOut,
        Cpu,
        ChevronLeft,
        ChevronRight,
        Activity,
        Sun,
        Moon,
        Network,
        Database,
        Mail,
        HardDrive,
        RefreshCw,
        Shield,
        Globe
    } from 'lucide-svelte';

    export let activePath = '/dashboard';
    let isCollapsed = false;

    const comandoItems = [
        { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
        { name: 'NODES', icon: Cpu, path: '/dashboard/pve/manage' },
        { name: 'Clusters', icon: Server, path: '/dashboard/clusters' },
        { name: 'SDN', icon: Network, path: '/dashboard/sdn/manage' },
        { name: 'Armazenamento', icon: HardDrive, path: '/dashboard/storage' },
        { name: 'Replicação', icon: RefreshCw, path: '/dashboard/replication' },
        { name: 'Backup', icon: Database, path: '/dashboard/pbs/manage' },
        { name: 'Mail Gateway', icon: Mail, path: '/dashboard/pmg/manage' },
    ];

    const observabilityItems = [
        { name: 'PVE', icon: Activity, path: '/dashboard/pve' },
        { name: 'SDN', icon: Globe, path: '/dashboard/sdn' },
        { name: 'PBS', icon: Database, path: '/dashboard/pbs' },
        { name: 'PMG', icon: Mail, path: '/dashboard/pmg' },
    ];

    const systemItems = [
        { name: 'Usuários', icon: Users, path: '/dashboard/users' },
        { name: 'Configurações', icon: Settings, path: '/dashboard/settings' },
    ];

    function toggleSidebar() {
        isCollapsed = !isCollapsed;
    }

    function toggleTheme() {
        theme.update(current => current === 'dark' ? 'light' : 'dark');
    }
</script>

<aside class="{isCollapsed ? 'w-20' : 'w-72'} bg-white dark:bg-brand-black border-r border-gray-100 dark:border-white/5 flex flex-col h-screen sticky top-0 transition-all duration-300 ease-in-out z-50">
    <!-- Logo Section -->
    <div class="p-6 mb-4 relative">
        <div class="flex items-center gap-4">
            <div class="relative flex-shrink-0">
                <!-- Official Logo SVG -->
                <div class="w-10 h-10 relative">
                    <svg viewBox="0 0 100 100" class="w-full h-full">
                        <!-- Orange X Shape -->
                        <path d="M20 20 L40 50 L20 80 L35 80 L50 57.5 L65 80 L80 80 L60 50 L80 20 L65 20 L50 42.5 L35 20 Z" fill="#ff7a00" />
                        <!-- Monitor Icon in middle -->
                        <rect x="35" y="38" width="30" height="20" rx="2" fill="black" stroke="#ff7a00" stroke-width="2" />
                        <path d="M40 48 Q50 42 60 48" stroke="#ff7a00" stroke-width="1.5" fill="none" />
                        <rect x="45" y="58" width="10" height="2" fill="#ff7a00" />
                    </svg>
                </div>
            </div>
            {#if !isCollapsed}
                <span class="text-2xl font-black text-black dark:text-white tracking-tighter transition-opacity duration-300">
                    PROX<span class="text-brand-orange">MON</span>
                </span>
            {/if}
        </div>

        <!-- Theme Toggle Button -->
        {#if !isCollapsed}
            <button 
                on:click={toggleTheme}
                class="mt-6 flex items-center gap-3 px-4 py-2 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/5 text-gray-500 dark:text-gray-400 hover:text-brand-orange transition-all"
            >
                {#if $theme === 'dark'}
                    <Sun size={14} />
                    <span class="text-[10px] font-black uppercase tracking-widest">Tema Light</span>
                {:else}
                    <Moon size={14} />
                    <span class="text-[10px] font-black uppercase tracking-widest">Tema Dark</span>
                {/if}
            </button>
        {:else}
            <button 
                on:click={toggleTheme}
                class="mt-6 w-10 h-10 flex items-center justify-center bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/5 text-gray-500 dark:text-gray-400 hover:text-brand-orange transition-all mx-auto"
            >
                {#if $theme === 'dark'}
                    <Sun size={14} />
                {:else}
                    <Moon size={14} />
                {/if}
            </button>
        {/if}

        <!-- Collapse Button -->
        <button 
            on:click={toggleSidebar}
            class="absolute -right-3 top-8 w-6 h-6 bg-brand-orange rounded-full flex items-center justify-center text-black hover:scale-110 transition-transform shadow-lg shadow-brand-orange/20"
        >
            {#if isCollapsed}
                <ChevronRight size={14} strokeWidth={3} />
            {:else}
                <ChevronLeft size={14} strokeWidth={3} />
            {/if}
        </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-4 space-y-8 overflow-y-auto scrollbar-hide">
        <!-- Comando Section -->
        <div class="space-y-1">
            {#if !isCollapsed}
                <div class="px-4 mb-4">
                    <p class="text-[8px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.4em]">Comando</p>
                </div>
            {/if}
            {#each comandoItems as item}
                <a 
                    href={item.path}
                    class="flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 group relative
                    {activePath === item.path ? 'bg-brand-orange/10 text-brand-orange' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-black dark:hover:text-white'}"
                >
                    {#if activePath === item.path}
                        <div class="absolute left-0 w-1 h-6 bg-brand-orange rounded-r-full"></div>
                    {/if}
                    <svelte:component this={item.icon} size={18} />
                    {#if !isCollapsed}
                        <span class="font-bold tracking-tight text-xs">{item.name}</span>
                    {/if}
                </a>
            {/each}
        </div>

        <!-- Observability Section -->
        <div class="space-y-1">
            {#if !isCollapsed}
                <div class="px-4 mb-4">
                    <p class="text-[8px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.4em]">Observabilidade</p>
                </div>
            {/if}
            {#each observabilityItems as item}
                <a 
                    href={item.path}
                    class="flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 group relative
                    {activePath === item.path ? 'bg-brand-orange/10 text-brand-orange' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-black dark:hover:text-white'}"
                >
                    {#if activePath === item.path}
                        <div class="absolute left-0 w-1 h-6 bg-brand-orange rounded-r-full"></div>
                    {/if}
                    <svelte:component this={item.icon} size={18} />
                    {#if !isCollapsed}
                        <span class="font-bold tracking-tight text-xs">{item.name}</span>
                    {/if}
                </a>
            {/each}
        </div>

        <!-- System Section -->
        <div class="space-y-1">
            {#if !isCollapsed}
                <div class="px-4 mb-4">
                    <p class="text-[8px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.4em]">Configuração</p>
                </div>
            {/if}
            {#each systemItems as item}
                <a 
                    href={item.path}
                    class="flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 group relative
                    {activePath === item.path ? 'bg-brand-orange/10 text-brand-orange' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-black dark:hover:text-white'}"
                >
                    {#if activePath === item.path}
                        <div class="absolute left-0 w-1 h-6 bg-brand-orange rounded-r-full"></div>
                    {/if}
                    <svelte:component this={item.icon} size={18} />
                    {#if !isCollapsed}
                        <span class="font-bold tracking-tight text-xs">{item.name}</span>
                    {/if}
                </a>
            {/each}
        </div>
    </nav>

    <!-- User & Logout -->
    <div class="p-4 border-t border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-white/5">
        <div class="flex items-center gap-3 p-3 rounded-2xl bg-white dark:bg-brand-black/50 border border-gray-100 dark:border-white/5 mb-3">
            <div class="w-8 h-8 rounded-lg bg-brand-orange flex items-center justify-center text-black font-black text-[10px] flex-shrink-0">
                AD
            </div>
            {#if !isCollapsed}
                <div class="flex-1 min-w-0">
                    <p class="text-[10px] font-black text-black dark:text-white uppercase truncate tracking-tight">Admin User</p>
                    <p class="text-[8px] text-gray-400 font-bold uppercase truncate tracking-widest">Master Account</p>
                </div>
            {/if}
        </div>
        
        <button class="w-full flex items-center {isCollapsed ? 'justify-center' : 'gap-3 px-4'} py-3 bg-brand-orange text-black rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-brand-orange/90 transition-all shadow-lg shadow-brand-orange/10 active:scale-95">
            <LogOut size={14} strokeWidth={3} />
            {#if !isCollapsed}
                <span>Sair do Sistema</span>
            {/if}
        </button>
    </div>
</aside>
