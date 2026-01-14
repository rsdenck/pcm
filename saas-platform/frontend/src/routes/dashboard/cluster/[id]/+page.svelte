<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { api } from '$lib/api';
    import { 
        ChevronLeft, Server, Activity, Database, HardDrive, 
        Cpu, MemoryStick, Clock, ShieldCheck, Play, Square, RefreshCcw, MoveHorizontal, MoreVertical
    } from 'lucide-svelte';

    const clusterId = $page.params.id;
    let cluster = null;
    let loading = true;
    let actionLoading = null;

    onMount(async () => {
        await loadCluster();
    });

    async function loadCluster() {
        loading = true;
        try {
            const response = await api.get(`/dashboard/cluster/${clusterId}`);
            cluster = response.data;
        } catch (error) {
            console.error('Failed to fetch cluster details', error);
        } finally {
            loading = false;
        }
    }

    async function handleResourceAction(resource, action) {
        actionLoading = `${resource.vmid}-${action}`;
        try {
            await api.post(`/cluster/${clusterId}/resource/${resource.vmid}/${action}`);
            await loadCluster();
            alert(`Ação ${action} enviada com sucesso para ${resource.name}`);
        } catch (error) {
            console.error(`Failed to ${action} resource`, error);
            alert(`Erro ao executar ${action} no recurso.`);
        } finally {
            actionLoading = null;
        }
    }

    function formatBytes(bytes: number, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
</script>

<div class="p-4 md:p-8 w-full transition-all">
    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Acessando Cluster...</p>
        </div>
    {:else if cluster}
        <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
                <div class="flex items-center gap-2 mb-2">
                    <a href="/dashboard/clusters" class="text-brand-orange hover:scale-110 transition-transform">
                        <ChevronLeft size={20} strokeWidth={3} />
                    </a>
                    <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                    <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Detalhes do Cluster</span>
                </div>
                <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                    {cluster.name} <span class="text-brand-orange text-2xl uppercase ml-4">{cluster.type}</span>
                </h1>
                <p class="text-gray-400 font-mono text-xs mt-2">{cluster.hostname}</p>
            </div>
            
            <div class="flex items-center gap-4 bg-white dark:bg-white/5 p-3 rounded-2xl border border-gray-100 dark:border-white/5">
                <div class="px-4 border-r border-gray-100 dark:border-white/10">
                    <div class="text-[8px] text-gray-400 uppercase font-black tracking-widest mb-0.5">Status</div>
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full {cluster.is_active ? 'bg-green-500' : 'bg-red-500'}"></div>
                        <span class="text-xs font-black uppercase tracking-widest {cluster.is_active ? 'text-green-500' : 'text-red-500'}">
                            {cluster.is_active ? 'Conectado' : 'Offline'}
                        </span>
                    </div>
                </div>
                <button 
                    on:click={loadCluster}
                    class="bg-brand-orange hover:bg-brand-orange/90 text-black px-5 py-2.5 rounded-xl font-black text-[9px] transition-all flex items-center gap-2 uppercase tracking-widest active:scale-95"
                >
                    <RefreshCcw size={14} strokeWidth={3} />
                    Sincronizar
                </button>
            </div>
        </header>

        <!-- Nodes Section -->
        <div class="flex items-center gap-4 mb-8">
            <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
            <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Nodes do Cluster</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            {#each cluster.nodes || [] as node}
                <div class="bg-white dark:bg-white/5 p-8 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm group hover:border-brand-orange/30 transition-all duration-500">
                    <div class="flex justify-between items-start mb-8">
                        <div>
                            <h3 class="text-2xl font-black text-black dark:text-white tracking-tighter mb-1 uppercase">{node.node_name}</h3>
                            <div class="flex items-center gap-2">
                                <div class="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                                <span class="text-[10px] font-black text-green-500 uppercase tracking-widest">{node.status}</span>
                            </div>
                        </div>
                        <div class="w-12 h-12 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center border border-gray-100 dark:border-white/5 group-hover:border-brand-orange/20 transition-all">
                            <Server class="text-brand-orange" size={24} />
                        </div>
                    </div>
                    
                    <div class="space-y-6">
                        <div>
                            <div class="flex justify-between items-end mb-2">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-2"><Cpu size={14} /> Processamento</span>
                                <span class="text-sm font-black text-black dark:text-white">{node.cpu_usage?.toFixed(1)}%</span>
                            </div>
                            <div class="w-full bg-gray-50 dark:bg-brand-black rounded-full h-1.5 overflow-hidden">
                                <div class="bg-brand-orange h-full shadow-[0_0_10px_rgba(255,122,0,0.3)]" style="width: {node.cpu_usage}%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between items-end mb-2">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-2"><MemoryStick size={14} /> Memória RAM</span>
                                <span class="text-[10px] font-black text-black dark:text-white">{formatBytes(node.memory_used)} / {formatBytes(node.memory_total)}</span>
                            </div>
                            <div class="w-full bg-gray-50 dark:bg-brand-black rounded-full h-1.5 overflow-hidden">
                                <div class="bg-brand-orange h-full shadow-[0_0_10px_rgba(255,122,0,0.3)]" style="width: {(node.memory_used / node.memory_total) * 100}%"></div>
                            </div>
                        </div>

                        <div class="pt-4 flex items-center justify-between border-t border-gray-50 dark:border-white/5">
                            <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-2"><Clock size={12} /> Uptime</span>
                            <span class="text-[10px] font-black text-black dark:text-white">{Math.floor(node.uptime / 86400)} Dias</span>
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Resources Section -->
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-4">
                <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
                <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Máquinas Virtuais e Containers</h2>
            </div>
            <div class="flex gap-2">
                <button class="bg-white dark:bg-white/5 p-2 rounded-xl border border-gray-100 dark:border-white/5 text-gray-400 hover:text-brand-orange transition-all"><MoreVertical size={16} /></button>
            </div>
        </div>

        <div class="bg-white dark:bg-white/5 rounded-[3rem] border border-gray-100 dark:border-white/5 overflow-hidden shadow-sm">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50 dark:bg-white/[0.02]">
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">ID</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Nome / Instância</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Tipo</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Node</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Status</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">CPU/RAM</th>
                            <th class="px-8 py-5 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5 text-right">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                        {#each cluster.resources || [] as res}
                            <tr class="hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors group">
                                <td class="px-8 py-6 text-xs font-mono font-bold text-brand-orange">{res.vmid}</td>
                                <td class="px-8 py-6">
                                    <span class="text-sm font-black text-black dark:text-white uppercase tracking-tighter">{res.name}</span>
                                </td>
                                <td class="px-8 py-6">
                                    <span class="px-3 py-1 bg-gray-100 dark:bg-white/5 rounded-full text-[9px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-white/10">{res.type}</span>
                                </td>
                                <td class="px-8 py-6 text-xs font-bold text-gray-400 uppercase">{res.node}</td>
                                <td class="px-8 py-6">
                                    <div class="flex items-center gap-2">
                                        <div class="w-2 h-2 rounded-full {res.status === 'running' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}"></div>
                                        <span class="text-[10px] font-black uppercase tracking-widest {res.status === 'running' ? 'text-green-500' : 'text-gray-400'}">{res.status}</span>
                                    </div>
                                </td>
                                <td class="px-8 py-6">
                                    <div class="flex flex-col gap-1">
                                        <span class="text-[10px] font-bold text-black dark:text-white">CPU: {res.cpu_usage?.toFixed(1)}%</span>
                                        <span class="text-[9px] text-gray-400">RAM: {formatBytes(res.memory_used)}</span>
                                    </div>
                                </td>
                                <td class="px-8 py-6">
                                    <div class="flex items-center justify-end gap-2">
                                        {#if res.status !== 'running'}
                                            <button 
                                                on:click={() => handleResourceAction(res, 'start')}
                                                disabled={actionLoading === `${res.vmid}-start`}
                                                class="w-8 h-8 rounded-lg bg-green-500/10 text-green-500 flex items-center justify-center hover:bg-green-500 hover:text-white transition-all disabled:opacity-50"
                                                title="Iniciar"
                                            >
                                                <Play size={14} strokeWidth={3} class={actionLoading === `${res.vmid}-start` ? 'animate-spin' : ''} />
                                            </button>
                                        {:else}
                                            <button 
                                                on:click={() => handleResourceAction(res, 'stop')}
                                                disabled={actionLoading === `${res.vmid}-stop`}
                                                class="w-8 h-8 rounded-lg bg-red-500/10 text-red-500 flex items-center justify-center hover:bg-red-500 hover:text-white transition-all disabled:opacity-50"
                                                title="Parar"
                                            >
                                                <Square size={14} strokeWidth={3} class={actionLoading === `${res.vmid}-stop` ? 'animate-spin' : ''} />
                                            </button>
                                            <button 
                                                on:click={() => handleResourceAction(res, 'reboot')}
                                                disabled={actionLoading === `${res.vmid}-reboot`}
                                                class="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-500 flex items-center justify-center hover:bg-blue-500 hover:text-white transition-all disabled:opacity-50"
                                                title="Reiniciar"
                                            >
                                                <RefreshCcw size={14} strokeWidth={3} class={actionLoading === `${res.vmid}-reboot` ? 'animate-spin' : ''} />
                                            </button>
                                        {/if}
                                        <button 
                                            on:click={() => alert('Migração ao vivo em desenvolvimento')}
                                            class="w-8 h-8 rounded-lg bg-brand-orange/10 text-brand-orange flex items-center justify-center hover:bg-brand-orange hover:text-black transition-all"
                                            title="Migrar entre Clusters"
                                        >
                                            <MoveHorizontal size={14} strokeWidth={3} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>


<style>
    .bg-gray-850 { background-color: #1a202c; }
    .bg-gray-750 { background-color: #2d3748; }
</style>
