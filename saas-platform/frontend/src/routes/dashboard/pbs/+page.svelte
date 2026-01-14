<script lang="ts">
    import { Database, HardDrive, Shield, Activity, Clock, Search, Filter, Plus, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiGetPbs } from '$lib/api';

    let loading = true;
    let datastores = [];
    let jobs = [];
    let summary = {
        total_usage: 0,
        total_capacity: 0
    };

    function formatBytes(bytes: number) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    onMount(async () => {
        try {
            const response = await apiGetPbs();
            datastores = response.data.datastores;
            jobs = response.data.jobs;
            summary.total_usage = response.data.total_usage;
            summary.total_capacity = response.data.total_capacity;
        } catch (error) {
            console.error('Failed to fetch PBS data', error);
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
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Backup Server Integration</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Observabilidade <span class="text-brand-orange">PBS</span>
            </h1>
        </div>
        
        <div class="flex items-center gap-4">
            <button class="bg-brand-orange hover:bg-brand-orange/90 text-black px-6 py-3 rounded-xl font-black text-[10px] transition-all shadow-xl shadow-brand-orange/20 flex items-center gap-3 uppercase tracking-widest active:scale-95">
                <Plus size={16} strokeWidth={3} />
                Novo Datastore
            </button>
        </div>
    </header>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Sincronizando Backups...</p>
        </div>
    {:else}
        <!-- PBS Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">Armazenamento Total</div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{formatBytes(summary.total_capacity)}</div>
                <div class="mt-4 h-1 w-full bg-gray-50 dark:bg-brand-black rounded-full overflow-hidden">
                    <div class="h-full bg-brand-orange" style="width: {(summary.total_usage / summary.total_capacity) * 100}%"></div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">Espaço Utilizado</div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{formatBytes(summary.total_usage)}</div>
                <div class="mt-4 flex items-center gap-2">
                    <div class="w-1 h-1 rounded-full bg-brand-orange"></div>
                    <span class="text-[9px] font-black text-brand-orange uppercase tracking-widest">Deduplicação Ativa</span>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">Datastores</div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{datastores.length}</div>
                <div class="mt-4 flex items-center gap-2 text-green-500">
                    <CheckCircle2 size={10} />
                    <span class="text-[9px] font-black uppercase tracking-widest">Todos Saudáveis</span>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">Última Sincronização</div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter uppercase">Agora</div>
                <div class="mt-4 flex items-center gap-2 text-brand-orange">
                    <Clock size={10} />
                    <span class="text-[9px] font-black uppercase tracking-widest">Real-time Sync</span>
                </div>
            </div>
        </div>

        <!-- Datastores List -->
        <div class="space-y-4">
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-4">
                    <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
                    <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Datastores</h2>
                </div>
                <div class="flex gap-2">
                    <button class="p-2 bg-white dark:bg-white/5 rounded-lg border border-gray-100 dark:border-white/5 text-gray-400"><Filter size={14} /></button>
                    <button class="p-2 bg-white dark:bg-white/5 rounded-lg border border-gray-100 dark:border-white/5 text-gray-400"><Search size={14} /></button>
                </div>
            </div>

            {#each datastores as ds}
                <div class="group bg-white dark:bg-white/5 p-6 rounded-[2.5rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div class="flex items-center gap-6">
                        <div class="w-14 h-14 bg-gray-50 dark:bg-brand-black rounded-2xl flex items-center justify-center border border-gray-100 dark:border-white/5 group-hover:border-brand-orange/30 transition-all duration-500">
                            <Database class="text-brand-orange group-hover:scale-110 transition-transform" size={24} />
                        </div>
                        <div>
                            <h3 class="text-lg font-black text-black dark:text-white group-hover:text-brand-orange transition-colors tracking-tighter mb-0.5 uppercase">{ds.store_name}</h3>
                            <div class="flex items-center gap-3">
                                <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Cluster: {ds.cluster?.name}</span>
                                <div class="w-1 h-1 bg-gray-300 dark:bg-gray-700 rounded-full"></div>
                                <span class="text-[9px] font-black text-brand-orange uppercase tracking-widest">Type: ZFS</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex-1 max-w-md w-full">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Ocupação: {ds.usage_percent}%</span>
                            <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">{formatBytes(ds.used)} / {formatBytes(ds.total)}</span>
                        </div>
                        <div class="h-1.5 w-full bg-gray-50 dark:bg-brand-black rounded-full overflow-hidden">
                            <div 
                                class="h-full transition-all duration-1000 {ds.usage_percent > 90 ? 'bg-red-500' : ds.usage_percent > 70 ? 'bg-yellow-500' : 'bg-brand-orange'}" 
                                style="width: {ds.usage_percent}%"
                            ></div>
                        </div>
                    </div>

                    <div class="flex items-center gap-8 w-full md:w-auto justify-between md:justify-end">
                        <div class="text-center">
                            <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">Verify</div>
                            <CheckCircle2 size={16} class="text-green-500 mx-auto" />
                        </div>
                        <div class="text-center">
                            <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">GC</div>
                            <span class="text-[10px] font-black text-black dark:text-white">2d ago</span>
                        </div>
                        <button class="w-10 h-10 rounded-xl bg-gray-50 dark:bg-white/5 flex items-center justify-center group-hover:bg-brand-orange group-hover:translate-x-1 transition-all duration-500">
                            <ChevronRight size={18} class="text-gray-400 dark:text-gray-500 group-hover:text-black" strokeWidth={3} />
                        </button>
                    </div>
                </div>
            {:else}
                <div class="flex flex-col items-center justify-center py-20 bg-white dark:bg-white/5 rounded-[3rem] border-2 border-dashed border-gray-100 dark:border-white/5">
                    <div class="w-20 h-20 bg-gray-50 dark:bg-brand-black rounded-[1.5rem] flex items-center justify-center mb-6 border border-gray-100 dark:border-white/10 shadow-sm">
                        <AlertCircle size={32} class="text-gray-300 dark:text-gray-800" strokeWidth={1.5} />
                    </div>
                    <h3 class="text-xl font-black text-black dark:text-white mb-2 uppercase tracking-tighter">Nenhum PBS Conectado</h3>
                    <p class="text-gray-400 dark:text-gray-600 mb-8 max-w-sm text-center font-bold text-xs uppercase tracking-wide">Integre o Proxmox Backup Server para gerenciamento centralizado de retenção e deduplicação.</p>
                    <button class="bg-black dark:bg-white hover:bg-brand-orange dark:hover:bg-brand-orange text-white dark:text-black px-10 py-4 rounded-2xl font-black text-[10px] transition-all shadow-xl hover:shadow-brand-orange/20 uppercase tracking-[0.2em] active:scale-95">
                        Conectar PBS
                    </button>
                </div>
            {/each}
        </div>

        <!-- PBS Jobs -->
        <div class="mt-12">
            <h2 class="text-xl font-black text-black dark:text-white uppercase tracking-widest mb-6 px-2">Jobs de Backup (PBS)</h2>
            <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-gray-100 dark:border-white/5">
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Tipo de Job</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">ID do Job</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Agendamento</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Última Execução</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Próxima Execução</th>
                                <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                            {#each jobs as job}
                                <tr class="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-2">
                                            <Activity size={14} class="text-brand-orange" />
                                            <span class="text-[9px] font-black text-black dark:text-white uppercase tracking-widest">{job.job_type}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 font-mono text-[10px] text-gray-400">{job.job_id}</td>
                                    <td class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">{job.schedule || 'Manual'}</td>
                                    <td class="px-6 py-4 text-[10px] text-gray-400">{job.last_run || '-'}</td>
                                    <td class="px-6 py-4 text-[10px] text-gray-400">{job.next_run || '-'}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-2">
                                            <div class="w-1.5 h-1.5 rounded-full {job.status === 'OK' ? 'bg-green-500' : 'bg-red-500'}"></div>
                                            <span class="text-[9px] font-black {job.status === 'OK' ? 'text-green-500' : 'text-red-500'} uppercase tracking-widest">{job.status}</span>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    {/if}
</div>
