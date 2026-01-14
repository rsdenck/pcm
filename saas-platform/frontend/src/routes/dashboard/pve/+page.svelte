<script lang="ts">
    import { onMount } from 'svelte';
    import { Server, Monitor, Activity, Zap, RefreshCcw, Search, Filter, AlertTriangle } from 'lucide-svelte';
    import { apiGetPve } from '$lib/api';

    let loading = true;
    let error: string | null = null;
    let data = {
        nodes: [],
        resources: [],
        summary: {
            total_nodes: 0,
            online_nodes: 0,
            total_vms: 0,
            total_containers: 0,
            running_resources: 0
        }
    };

    async function loadData() {
        loading = true;
        error = null;
        try {
            const response = await apiGetPve();
            data = response.data;
        } catch (e) {
            console.error(e);
            error = "Não foi possível carregar os dados do PVE.";
        } finally {
            loading = false;
        }
    }

    onMount(loadData);

    function formatBytes(bytes: number) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Proxmox Virtual Environment</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Visibilidade <span class="text-brand-orange">PVE</span>
            </h1>
        </div>
        
        <button 
            on:click={loadData}
            class="group flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-brand-orange/10 rounded-xl transition-all border border-white/5"
            disabled={loading}
        >
            <RefreshCcw size={14} class="text-brand-orange {loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}" />
            <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Atualizar</span>
        </button>
    </header>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Sincronizando Infraestrutura PVE...</p>
        </div>
    {:else if error}
        <div class="bg-red-500/10 border border-red-500/20 p-8 rounded-[2rem] text-center">
            <AlertTriangle size={48} class="text-red-500 mx-auto mb-4" />
            <p class="text-red-500 font-black uppercase tracking-widest text-xs">{error}</p>
        </div>
    {:else}
        <!-- Stats Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-brand-orange/10 rounded-2xl flex items-center justify-center">
                        <Server class="text-brand-orange" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Nodes Online</div>
                        <div class="text-2xl font-black text-black dark:text-white tracking-tighter">
                            {data.summary.online_nodes} <span class="text-xs text-gray-400">/ {data.summary.total_nodes}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center">
                        <Monitor class="text-blue-500" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total VMs</div>
                        <div class="text-2xl font-black text-black dark:text-white tracking-tighter">
                            {data.summary.total_vms}
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-purple-500/10 rounded-2xl flex items-center justify-center">
                        <Activity class="text-purple-500" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Containers</div>
                        <div class="text-2xl font-black text-black dark:text-white tracking-tighter">
                            {data.summary.total_containers}
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-green-500/10 rounded-2xl flex items-center justify-center">
                        <Zap class="text-green-500" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Recursos em Execução</div>
                        <div class="text-2xl font-black text-black dark:text-white tracking-tighter">
                            {data.summary.running_resources}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Nodes List -->
        <div class="mb-12">
            <h2 class="text-xl font-black text-black dark:text-white uppercase tracking-widest mb-6 px-2">Nodes do Cluster</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each data.nodes as node}
                    <div class="bg-white dark:bg-white/5 p-6 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm">
                        <div class="flex justify-between items-start mb-6">
                            <div class="flex items-center gap-3">
                                <div class="w-2 h-2 rounded-full {node.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
                                <h3 class="font-black text-black dark:text-white tracking-tighter text-lg">{node.node_name}</h3>
                            </div>
                            <span class="text-[8px] font-black {node.status === 'online' ? 'text-green-500' : 'text-red-500'} uppercase tracking-widest border {node.status === 'online' ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5'} px-2 py-1 rounded-md">
                                {node.status}
                            </span>
                        </div>
                        
                        <div class="space-y-4">
                            <!-- New Detailed Info -->
                            <div class="grid grid-cols-2 gap-2 text-[8px] font-bold uppercase tracking-widest text-gray-500 bg-gray-50 dark:bg-white/5 p-3 rounded-xl border border-gray-100 dark:border-white/5">
                                <div>
                                    <div class="text-gray-400 mb-1">Kernel</div>
                                    <div class="text-black dark:text-white truncate">{node.kernel_version || 'N/A'}</div>
                                </div>
                                <div>
                                    <div class="text-gray-400 mb-1">PVE Version</div>
                                    <div class="text-black dark:text-white">{node.pve_version || 'N/A'}</div>
                                </div>
                                <div class="col-span-2">
                                    <div class="text-gray-400 mb-1">CPU Model</div>
                                    <div class="text-black dark:text-white truncate">{node.cpu_model || 'N/A'}</div>
                                </div>
                                <div>
                                    <div class="text-gray-400 mb-1">Cores/Sockets</div>
                                    <div class="text-black dark:text-white">{node.cpu_cores}c / {node.cpu_sockets}s</div>
                                </div>
                                <div>
                                    <div class="text-gray-400 mb-1">Load Avg</div>
                                    <div class="text-black dark:text-white">{node.loadavg || 'N/A'}</div>
                                </div>
                            </div>

                            <div>
                                <div class="flex justify-between text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
                                    <span>CPU</span>
                                    <span>{node.cpu_usage.toFixed(1)}%</span>
                                </div>
                                <div class="h-1 w-full bg-gray-50 dark:bg-white/5 rounded-full overflow-hidden">
                                    <div class="h-full bg-brand-orange" style="width: {node.cpu_usage}%"></div>
                                </div>
                            </div>
                            <div>
                                <div class="flex justify-between text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
                                    <span>Memória</span>
                                    <span>{(node.memory_used / node.memory_total * 100).toFixed(1)}%</span>
                                </div>
                                <div class="h-1 w-full bg-gray-50 dark:bg-white/5 rounded-full overflow-hidden">
                                    <div class="h-full bg-blue-500" style="width: {(node.memory_used / node.memory_total * 100)}%"></div>
                                </div>
                                <div class="text-[8px] text-gray-500 mt-1">{formatBytes(node.memory_used)} / {formatBytes(node.memory_total)}</div>
                            </div>
                            
                            {#if node.swap_total > 0}
                            <div>
                                <div class="flex justify-between text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">
                                    <span>Swap</span>
                                    <span>{(node.swap_used / node.swap_total * 100).toFixed(1)}%</span>
                                </div>
                                <div class="h-1 w-full bg-gray-50 dark:bg-white/5 rounded-full overflow-hidden">
                                    <div class="h-full bg-amber-500" style="width: {(node.swap_used / node.swap_total * 100)}%"></div>
                                </div>
                                <div class="text-[8px] text-gray-500 mt-1">{formatBytes(node.swap_used)} / {formatBytes(node.swap_total)}</div>
                            </div>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Resources List -->
        <div>
            <h2 class="text-xl font-black text-black dark:text-white uppercase tracking-widest mb-6 px-2">Recursos (VMs/LXCs)</h2>
            <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-gray-100 dark:border-white/5">
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Tipo</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">ID</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Nome</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Node</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Uptime</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                            {#each data.resources as res}
                                <tr class="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors group">
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-2">
                                            {#if res.type === 'qemu'}
                                                <Monitor size={14} class="text-blue-500" />
                                                <span class="text-[9px] font-black text-blue-500 uppercase tracking-widest">VM</span>
                                            {:else}
                                                <Zap size={14} class="text-purple-500" />
                                                <span class="text-[9px] font-black text-purple-500 uppercase tracking-widest">LXC</span>
                                            {/if}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 font-mono text-[10px] text-gray-400">{res.vmid}</td>
                                    <td class="px-6 py-4">
                                        <span class="font-black text-black dark:text-white tracking-tighter">{res.name}</span>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-2">
                                            <div class="w-1.5 h-1.5 rounded-full {res.status === 'running' ? 'bg-green-500' : 'bg-red-500'}"></div>
                                            <span class="text-[9px] font-black {res.status === 'running' ? 'text-green-500' : 'text-red-500'} uppercase tracking-widest">{res.status}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-[10px] font-bold text-gray-400">{res.node}</td>
                                    <td class="px-6 py-4 text-[10px] text-gray-400">{Math.floor(res.uptime / 3600)}h {Math.floor((res.uptime % 3600) / 60)}m</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    {/if}
</div>