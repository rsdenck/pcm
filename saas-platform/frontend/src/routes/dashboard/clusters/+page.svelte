<script lang="ts">
    import { Server, Plus, Search, Filter, ChevronRight, Activity, Cpu, HardDrive } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let clusters = [];
    let loading = true;

    function formatBytes(bytes: number) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    onMount(async () => {
        try {
            const response = await api.get('/dashboard');
            clusters = response.data.clusters;
        } catch (error) {
            console.error('Failed to fetch clusters', error);
        } finally {
            loading = false;
        }
    });
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Infraestrutura</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Meus <span class="text-brand-orange">Clusters</span>
            </h1>
        </div>
        
        <button 
            on:click={() => window.location.href = '/dashboard/clusters/new'}
            class="bg-brand-orange hover:bg-brand-orange/90 text-black px-6 py-3 rounded-xl font-black text-[10px] transition-all shadow-xl shadow-brand-orange/20 flex items-center gap-3 uppercase tracking-widest active:scale-95"
        >
            <Plus size={16} strokeWidth={3} />
            Novo Cluster
        </button>
    </header>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Buscando Clusters...</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 gap-4">
            {#each clusters as cluster}
                <a 
                    href="/dashboard/cluster/{cluster.id}"
                    class="group flex flex-col md:flex-row items-start md:items-center justify-between p-6 bg-white dark:bg-white/5 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:bg-gray-50 dark:hover:bg-white/[0.08] hover:border-brand-orange/40 transition-all duration-500 shadow-sm dark:shadow-none"
                >
                    <div class="flex items-center gap-6">
                        <div class="w-16 h-16 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center border border-gray-100 dark:border-white/5 group-hover:border-brand-orange/30 transition-all duration-500 shadow-sm">
                            <Server class="text-brand-orange group-hover:scale-110 transition-transform" size={28} strokeWidth={2} />
                        </div>
                        <div>
                            <h3 class="text-xl font-black text-black dark:text-white group-hover:text-brand-orange transition-colors tracking-tighter mb-1">{cluster.name}</h3>
                            <div class="flex items-center gap-3">
                                <span class="text-xs font-mono text-gray-400 font-bold">{cluster.hostname}</span>
                                <div class="w-1 h-1 bg-gray-200 dark:bg-gray-800 rounded-full"></div>
                                <span class="text-[10px] font-black text-brand-orange uppercase tracking-[0.2em]">{cluster.type}</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center gap-12 mt-6 md:mt-0 w-full md:w-auto justify-between md:justify-end">
                        <div class="flex gap-8">
                            <div class="text-center">
                                <div class="text-[9px] text-gray-400 dark:text-gray-600 font-black uppercase tracking-widest mb-1">CPU</div>
                                <div class="text-lg font-black text-black dark:text-white tracking-tighter">
                                    {cluster.total_cpu ? (cluster.total_cpu * 100).toFixed(1) + '%' : '--'}
                                </div>
                            </div>
                            <div class="text-center">
                                <div class="text-[9px] text-gray-400 dark:text-gray-600 font-black uppercase tracking-widest mb-1">RAM</div>
                                <div class="text-lg font-black text-black dark:text-white tracking-tighter">
                                    {cluster.total_memory_max ? formatBytes(cluster.total_memory_used) : '--'}
                                </div>
                            </div>
                            <div class="text-center">
                                <div class="text-[9px] text-gray-400 dark:text-gray-600 font-black uppercase tracking-widest mb-1">Storage</div>
                                <div class="text-lg font-black text-black dark:text-white tracking-tighter">
                                    {cluster.total_disk_max ? formatBytes(cluster.total_disk_used) : '--'}
                                </div>
                            </div>
                        </div>
                        <div class="w-12 h-12 rounded-xl bg-gray-50 dark:bg-white/5 flex items-center justify-center group-hover:bg-brand-orange group-hover:translate-x-1 transition-all duration-500 shadow-sm">
                            <ChevronRight size={20} class="text-gray-400 dark:text-gray-500 group-hover:text-black transition-colors" strokeWidth={3} />
                        </div>
                    </div>
                </a>
            {:else}
                <div class="flex flex-col items-center justify-center py-24 bg-white dark:bg-white/5 rounded-[3rem] border-2 border-dashed border-gray-100 dark:border-white/5">
                    <div class="w-24 h-24 bg-gray-50 dark:bg-brand-black rounded-[2rem] flex items-center justify-center mb-8 border border-gray-100 dark:border-white/10 shadow-sm">
                        <Server size={48} class="text-gray-200 dark:text-gray-800" strokeWidth={1.5} />
                    </div>
                    <h3 class="text-2xl font-black text-black dark:text-white mb-3 uppercase tracking-tighter">Nenhum Cluster Encontrado</h3>
                    <p class="text-gray-400 dark:text-gray-600 mb-10 max-w-sm text-center font-bold text-sm uppercase tracking-wide">Comece adicionando seu primeiro ambiente Proxmox.</p>
                    <button 
                        on:click={() => window.location.href = '/dashboard/clusters/new'}
                        class="bg-black dark:bg-white hover:bg-brand-orange dark:hover:bg-brand-orange text-white dark:text-black px-12 py-5 rounded-[2rem] font-black text-sm transition-all shadow-2xl hover:shadow-brand-orange/20 uppercase tracking-[0.2em] active:scale-95"
                    >
                        Configurar Primeiro Cluster
                    </button>
                </div>
            {/each}
        </div>
    {/if}
</div>
