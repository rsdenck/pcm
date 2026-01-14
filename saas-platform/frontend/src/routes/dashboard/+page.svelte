<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { Activity, Server, Database, Mail, ShieldCheck, AlertCircle } from 'lucide-svelte';

    let stats = {
        total_nodes: 0,
        total_vms: 0,
        total_containers: 0,
        online_nodes: 0
    };
    let clusters = [];
    let loading = true;

    onMount(async () => {
        try {
            const response = await api.get('/dashboard');
            stats = response.data.stats;
            clusters = response.data.clusters;
        } catch (error) {
            console.error('Failed to fetch dashboard data', error);
        } finally {
            loading = false;
        }
    });
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange animate-pulse"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Sistema Ativo</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Visão <span class="text-brand-orange">Geral</span>
            </h1>
        </div>
        
        <div class="flex items-center gap-4 bg-white dark:bg-white/5 p-3 rounded-2xl border border-gray-100 dark:border-white/5">
            <div class="px-4 border-r border-gray-100 dark:border-white/10 hidden md:block">
                <div class="text-[8px] text-gray-400 uppercase font-black tracking-widest mb-0.5">Uptime Global</div>
                <div class="text-sm font-black text-brand-orange">99.98%</div>
            </div>
            <button 
                on:click={() => window.location.reload()}
                class="bg-brand-orange hover:bg-brand-orange/90 text-black px-5 py-2.5 rounded-xl font-black text-[9px] transition-all flex items-center gap-2 uppercase tracking-widest active:scale-95"
            >
                <Activity size={14} strokeWidth={3} />
                Sincronizar
            </button>
        </div>
    </header>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Carregando Datacenter...</p>
        </div>
    {:else}
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            <div class="group relative bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500 shadow-sm dark:shadow-none">
                <div class="flex items-center justify-between mb-6">
                    <div class="w-10 h-10 bg-brand-orange/5 dark:bg-brand-orange/10 rounded-xl flex items-center justify-center border border-brand-orange/10 dark:border-brand-orange/20">
                        <Server class="text-brand-orange" size={20} strokeWidth={2.5} />
                    </div>
                    <span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Nodes</span>
                </div>
                <div class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Status de Rede</div>
                <div class="text-4xl font-black text-black dark:text-white tracking-tighter">{stats.online_nodes}<span class="text-gray-300 dark:text-gray-800 text-2xl font-light">/{stats.total_nodes}</span></div>
                <div class="mt-6 h-1 w-full bg-gray-50 dark:bg-white/5 rounded-full overflow-hidden">
                    <div class="h-full bg-brand-orange shadow-[0_0_15px_rgba(255,122,0,0.3)] transition-all duration-1000" style="width: {(stats.online_nodes / stats.total_nodes) * 100}%"></div>
                </div>
            </div>

            <div class="group relative bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500 shadow-sm dark:shadow-none">
                <div class="flex items-center justify-between mb-6">
                    <div class="w-10 h-10 bg-brand-orange/5 dark:bg-brand-orange/10 rounded-xl flex items-center justify-center border border-brand-orange/10 dark:border-brand-orange/20">
                        <Activity class="text-brand-orange" size={20} strokeWidth={2.5} />
                    </div>
                    <span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Virtualização</span>
                </div>
                <div class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">VMs Ativas</div>
                <div class="text-4xl font-black text-black dark:text-white tracking-tighter">{stats.total_vms}</div>
                <div class="mt-6 flex items-center gap-2">
                    <div class="w-1 h-1 rounded-full bg-brand-orange animate-pulse"></div>
                    <span class="text-[9px] font-black text-brand-orange uppercase tracking-widest">Instâncias</span>
                </div>
            </div>

            <div class="group relative bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500 shadow-sm dark:shadow-none">
                <div class="flex items-center justify-between mb-6">
                    <div class="w-10 h-10 bg-brand-orange/5 dark:bg-brand-orange/10 rounded-xl flex items-center justify-center border border-brand-orange/10 dark:border-brand-orange/20">
                        <Database class="text-brand-orange" size={20} strokeWidth={2.5} />
                    </div>
                    <span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Containers</span>
                </div>
                <div class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Ambientes LXC</div>
                <div class="text-4xl font-black text-black dark:text-white tracking-tighter">{stats.total_containers}</div>
                <div class="mt-6 flex items-center gap-2">
                    <div class="w-1 h-1 rounded-full bg-brand-orange"></div>
                    <span class="text-[9px] font-black text-brand-orange uppercase tracking-widest">Isolados</span>
                </div>
            </div>

            <div class="group relative bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500 shadow-sm dark:shadow-none">
                <div class="flex items-center justify-between mb-6">
                    <div class="w-10 h-10 bg-brand-orange/5 dark:bg-brand-orange/10 rounded-xl flex items-center justify-center border border-brand-orange/10 dark:border-brand-orange/20">
                        <ShieldCheck class="text-brand-orange" size={20} strokeWidth={2.5} />
                    </div>
                    <span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Proteção</span>
                </div>
                <div class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Firewall</div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter uppercase">Ativo</div>
                <div class="mt-6 flex items-center gap-2">
                    <span class="text-[9px] font-black text-brand-orange uppercase tracking-widest">Segurança Total</span>
                </div>
            </div>
        </div>

        <!-- Clusters Section -->
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-4">
                <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
                <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Infraestrutura</h2>
            </div>
            <button class="text-gray-400 dark:text-gray-500 text-[9px] font-black hover:text-brand-orange transition-colors uppercase tracking-[0.2em]">Gerenciar Todos</button>
        </div>

        <div class="grid grid-cols-1 gap-4">
            {#each clusters as cluster}
                <a 
                    href="/dashboard/cluster/{cluster.id}"
                    class="group flex items-center justify-between p-6 bg-white dark:bg-white/5 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:bg-gray-50 dark:hover:bg-white/[0.08] hover:border-brand-orange/40 transition-all duration-500 shadow-sm dark:shadow-none"
                >
                    <div class="flex items-center gap-6">
                        <div class="w-14 h-14 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center border border-gray-100 dark:border-white/5 group-hover:border-brand-orange/30 transition-all duration-500 shadow-sm">
                            <Server class="text-brand-orange group-hover:scale-110 transition-transform" size={24} strokeWidth={2} />
                        </div>
                        <div>
                            <h3 class="text-lg font-black text-black dark:text-white group-hover:text-brand-orange transition-colors tracking-tighter mb-0.5">{cluster.name}</h3>
                            <div class="flex items-center gap-3">
                                <span class="text-[10px] font-mono text-gray-400 font-bold">{cluster.hostname}</span>
                                <div class="w-1 h-1 bg-gray-200 dark:bg-gray-800 rounded-full"></div>
                                <span class="text-[9px] font-black text-brand-orange uppercase tracking-[0.2em]">{cluster.type}</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center gap-12">
                        <div class="text-center">
                            <div class="text-[9px] text-gray-400 dark:text-gray-600 font-black uppercase tracking-widest mb-1">Recursos</div>
                            <div class="text-xl font-black text-black dark:text-white tracking-tighter">{cluster.resources_count}</div>
                        </div>
                        <div class="text-center hidden md:block">
                            <div class="text-[9px] text-gray-400 dark:text-gray-600 font-black uppercase tracking-widest mb-1">Estado</div>
                            <span class="px-4 py-1 rounded-full text-[9px] font-black bg-brand-orange/5 dark:bg-brand-orange/10 text-brand-orange border border-brand-orange/10 dark:border-brand-orange/20 uppercase tracking-widest">Online</span>
                        </div>
                        <div class="w-10 h-10 rounded-xl bg-gray-50 dark:bg-white/5 flex items-center justify-center group-hover:bg-brand-orange group-hover:translate-x-1 transition-all duration-500">
                            <ChevronRight size={18} class="text-gray-400 dark:text-gray-500 group-hover:text-black transition-colors" strokeWidth={3} />
                        </div>
                    </div>
                </a>
            {:else}
                <div class="flex flex-col items-center justify-center py-20 bg-white dark:bg-white/5 rounded-[3rem] border-2 border-dashed border-gray-100 dark:border-white/5">
                    <div class="w-20 h-20 bg-gray-50 dark:bg-brand-black rounded-[1.5rem] flex items-center justify-center mb-6 border border-gray-100 dark:border-white/10 shadow-sm">
                        <AlertCircle size={32} class="text-gray-300 dark:text-gray-800" strokeWidth={1.5} />
                    </div>
                    <h3 class="text-xl font-black text-black dark:text-white mb-2 uppercase tracking-tighter">Nenhum Cluster Ativo</h3>
                    <p class="text-gray-400 dark:text-gray-600 mb-8 max-w-sm text-center font-bold text-xs uppercase tracking-wide">Conecte sua infraestrutura Proxmox.</p>
                    <button 
                        on:click={() => window.location.href = '/dashboard/clusters/new'}
                        class="bg-black dark:bg-white hover:bg-brand-orange dark:hover:bg-brand-orange text-white dark:text-black px-10 py-4 rounded-2xl font-black text-[10px] transition-all shadow-xl hover:shadow-brand-orange/20 uppercase tracking-[0.2em] active:scale-95"
                    >
                        Adicionar Novo Cluster
                    </button>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .bg-gray-850 { background-color: #1a202c; }
    .bg-gray-750 { background-color: #2d3748; }
</style>
