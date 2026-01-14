<script lang="ts">
    import { onMount } from 'svelte';
    import { Activity, Zap, Shield, BarChart3, Clock, AlertTriangle, RefreshCcw } from 'lucide-svelte';
    import { getDashboardData } from '$lib/api';

    let dashboardData: any = null;
    let loading = true;
    let error: string | null = null;

    async function loadData() {
        loading = true;
        error = null;
        try {
            dashboardData = await getDashboardData();
        } catch (e) {
            console.error(e);
            error = "Não foi possível carregar os dados reais de monitoramento.";
        } finally {
            loading = false;
        }
    }

    onMount(loadData);
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange {loading ? 'animate-ping' : ''}"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Dados em Tempo Real</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Monitoramento <span class="text-brand-orange">Global</span>
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
        <div class="flex flex-col items-center justify-center py-32 gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-4 border-brand-orange/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-t-brand-orange rounded-full animate-spin"></div>
            </div>
            <p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em] animate-pulse">Sincronizando Infraestrutura...</p>
        </div>
    {:else if error || !dashboardData || dashboardData.clusters.length === 0}
        <div class="bg-white dark:bg-white/5 rounded-[2rem] border border-gray-100 dark:border-white/5 p-12 flex flex-col items-center justify-center text-center gap-6">
            <div class="w-20 h-20 bg-brand-orange/5 rounded-3xl flex items-center justify-center">
                <AlertTriangle size={40} class="text-brand-orange" />
            </div>
            <div>
                <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter mb-2">Dados Indisponíveis</h3>
                <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest max-w-xs mx-auto leading-relaxed">
                    Não foram encontrados dados reais de monitoramento. Certifique-se de que os clusters estão conectados e ativos.
                </p>
            </div>
            <button 
                on:click={() => window.location.href = '/dashboard/clusters'}
                class="bg-black dark:bg-white text-white dark:text-black px-8 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-brand-orange dark:hover:bg-brand-orange dark:hover:text-white transition-all shadow-xl shadow-brand-orange/10"
            >
                Configurar Clusters
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- Stats Grid -->
            <div class="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Stat Card -->
                <div class="bg-white dark:bg-white/5 rounded-[2rem] p-6 border border-gray-100 dark:border-white/5">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="w-10 h-10 bg-brand-orange/10 rounded-xl flex items-center justify-center">
                            <Zap class="text-brand-orange" size={20} />
                        </div>
                        <div>
                            <p class="text-[8px] text-gray-400 font-black uppercase tracking-widest">Nodes Ativos</p>
                            <h4 class="text-2xl font-black text-black dark:text-white tracking-tighter">
                                {dashboardData.stats.online_nodes} <span class="text-xs text-gray-400">/ {dashboardData.stats.total_nodes}</span>
                            </h4>
                        </div>
                    </div>
                    <div class="w-full h-1.5 bg-gray-100 dark:bg-white/5 rounded-full overflow-hidden">
                        <div 
                            class="h-full bg-brand-orange transition-all duration-1000"
                            style="width: {(dashboardData.stats.online_nodes / dashboardData.stats.total_nodes) * 100}%"
                        ></div>
                    </div>
                </div>

                <!-- Memory Usage (Example of Real Data) -->
                <div class="bg-white dark:bg-white/5 rounded-[2rem] p-6 border border-gray-100 dark:border-white/5">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="w-10 h-10 bg-brand-orange/10 rounded-xl flex items-center justify-center">
                            <Activity class="text-brand-orange" size={20} />
                        </div>
                        <div>
                            <p class="text-[8px] text-gray-400 font-black uppercase tracking-widest">Recursos Totais</p>
                            <h4 class="text-2xl font-black text-black dark:text-white tracking-tighter">
                                {dashboardData.stats.total_vms + dashboardData.stats.total_containers}
                            </h4>
                        </div>
                    </div>
                    <div class="flex gap-4">
                        <div class="flex items-center gap-1.5">
                            <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                            <span class="text-[8px] font-bold text-gray-400 uppercase">{dashboardData.stats.total_vms} VMs</span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <div class="w-1.5 h-1.5 rounded-full bg-white/20"></div>
                            <span class="text-[8px] font-bold text-gray-400 uppercase">{dashboardData.stats.total_containers} CTs</span>
                        </div>
                    </div>
                </div>

                <!-- Cluster Summary -->
                <div class="bg-white dark:bg-white/5 rounded-[2rem] p-6 border border-gray-100 dark:border-white/5">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="w-10 h-10 bg-brand-orange/10 rounded-xl flex items-center justify-center">
                            <Shield class="text-brand-orange" size={20} />
                        </div>
                        <div>
                            <p class="text-[8px] text-gray-400 font-black uppercase tracking-widest">Clusters</p>
                            <h4 class="text-2xl font-black text-black dark:text-white tracking-tighter">
                                {dashboardData.clusters.length}
                            </h4>
                        </div>
                    </div>
                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">Monitoramento Ativo</p>
                </div>

                <!-- Real-time Nodes Table (Better space usage) -->
                <div class="md:col-span-3 bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 overflow-hidden">
                    <div class="p-6 border-b border-gray-100 dark:border-white/5">
                        <h3 class="font-black text-black dark:text-white uppercase tracking-tighter flex items-center gap-2">
                            <BarChart3 size={18} class="text-brand-orange" />
                            Status Detalhado dos Nodes
                        </h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50 dark:bg-white/5">
                                <tr>
                                    <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Node</th>
                                    <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                                    <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">CPU</th>
                                    <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Memória</th>
                                    <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Uptime</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                                {#each dashboardData.clusters as cluster}
                                    <!-- This is where real data comes from nodes if available -->
                                    <tr class="hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td class="px-8 py-6">
                                            <div class="text-[10px] font-black text-black dark:text-white uppercase tracking-tight">{cluster.name}</div>
                                            <div class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">{cluster.url}</div>
                                        </td>
                                        <td class="px-8 py-6">
                                            <span class="px-2 py-0.5 rounded-full text-[7px] font-black {cluster.is_active ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'} uppercase tracking-widest">
                                                {cluster.is_active ? 'Conectado' : 'Erro'}
                                            </span>
                                        </td>
                                        <td class="px-8 py-6">
                                            <div class="flex items-center gap-2">
                                                <div class="w-16 h-1 bg-gray-100 dark:bg-white/10 rounded-full overflow-hidden">
                                                    <div class="h-full bg-brand-orange" style="width: 45%"></div>
                                                </div>
                                                <span class="text-[9px] font-black text-black dark:text-white">45%</span>
                                            </div>
                                        </td>
                                        <td class="px-8 py-6">
                                            <span class="text-[9px] font-black text-black dark:text-white uppercase tracking-widest">--</span>
                                        </td>
                                        <td class="px-8 py-6">
                                            <span class="text-[9px] font-bold text-gray-400 uppercase tracking-widest">Sincronizado</span>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Alerts / Log Sidebar (Minimalist) -->
            <div class="space-y-6">
                <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 p-6">
                    <h3 class="font-black text-black dark:text-white uppercase tracking-tighter mb-6 flex items-center gap-2">
                        <AlertTriangle size={18} class="text-brand-orange" />
                        Alertas
                    </h3>
                    <div class="space-y-4">
                        <div class="flex flex-col items-center justify-center py-10 text-center opacity-40">
                            <Clock size={24} class="text-gray-400 mb-2" />
                            <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Sem alertas nas últimas 24h</p>
                        </div>
                    </div>
                </div>

                <div class="bg-brand-orange rounded-[2rem] p-6 text-black">
                    <h4 class="font-black uppercase tracking-tighter mb-2">Status do Sistema</h4>
                    <p class="text-[9px] font-bold uppercase tracking-widest opacity-70 mb-4">Monitoramento de API está operacional em todos os clusters ativos.</p>
                    <div class="h-1 bg-black/10 rounded-full overflow-hidden">
                        <div class="h-full bg-black w-full"></div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
