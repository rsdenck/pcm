<script lang="ts">
    import { Mail, Shield, AlertTriangle, CheckCircle, BarChart3, Search, Filter, RefreshCw, ChevronRight, Activity, Zap, Bug } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiGetPmg } from '$lib/api';

    let loading = true;
    let stats = [];
    let accounts = [];
    let rules = [];
    let summary = {
        total_mail_in: 0,
        total_mail_out: 0,
        total_spam: 0,
        total_virus: 0,
        total_accounts: 0
    };

    onMount(async () => {
        try {
            const response = await apiGetPmg();
            stats = response.data.stats;
            accounts = response.data.accounts;
            rules = response.data.rules;
            summary = response.data.summary;
        } catch (error) {
            console.error('Failed to fetch PMG data', error);
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
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Mail Gateway Security</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Observabilidade <span class="text-brand-orange">PMG</span>
            </h1>
        </div>
        
        <div class="flex items-center gap-4">
            <button class="bg-white dark:bg-white/5 border border-gray-100 dark:border-white/5 text-black dark:text-white px-6 py-3 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95">
                <RefreshCw size={14} strokeWidth={3} />
                Limpar Cache
            </button>
        </div>
    </header>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Analisando Fluxo de E-mail...</p>
        </div>
    {:else}
        <!-- PMG Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                    <div class="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-500">
                        <Mail size={20} />
                    </div>
                    <span class="text-[10px] font-black text-blue-500 uppercase tracking-widest">Incoming</span>
                </div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{summary.total_mail_in}</div>
                <p class="text-[9px] font-black text-gray-400 uppercase mt-2 tracking-widest">Total processado</p>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                    <div class="w-10 h-10 bg-green-500/10 rounded-xl flex items-center justify-center text-green-500">
                        <Zap size={20} />
                    </div>
                    <span class="text-[10px] font-black text-green-500 uppercase tracking-widest">Outgoing</span>
                </div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{summary.total_mail_out}</div>
                <p class="text-[9px] font-black text-gray-400 uppercase mt-2 tracking-widest">Enviados com sucesso</p>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                    <div class="w-10 h-10 bg-orange-500/10 rounded-xl flex items-center justify-center text-orange-500">
                        <Bug size={20} />
                    </div>
                    <span class="text-[10px] font-black text-orange-500 uppercase tracking-widest">Spam</span>
                </div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{summary.total_spam}</div>
                <p class="text-[9px] font-black text-gray-400 uppercase mt-2 tracking-widest">Bloqueados</p>
            </div>

            <div class="bg-white dark:bg-white/5 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                    <div class="w-10 h-10 bg-red-500/10 rounded-xl flex items-center justify-center text-red-500">
                        <Shield size={20} />
                    </div>
                    <span class="text-[10px] font-black text-red-500 uppercase tracking-widest">Virus</span>
                </div>
                <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{summary.total_virus}</div>
                <p class="text-[9px] font-black text-gray-400 uppercase mt-2 tracking-widest">Ameaças eliminadas</p>
            </div>
        </div>

        <!-- Mail Traffic History -->
        <div class="bg-white dark:bg-white/5 p-8 rounded-[3rem] border border-gray-100 dark:border-white/5 shadow-sm mb-12">
            <div class="flex items-center justify-between mb-10">
                <div class="flex items-center gap-4">
                    <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
                    <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Histórico de Tráfego</h2>
                </div>
                <div class="flex gap-4">
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                        <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Incoming</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-green-500"></div>
                        <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Outgoing</span>
                    </div>
                </div>
            </div>

            <div class="h-64 flex items-end justify-between gap-2 px-4">
                {#each stats as stat}
                    <div class="flex-1 flex flex-col gap-1 items-center group relative">
                        <div class="w-full flex flex-col-reverse gap-0.5">
                            <div class="w-full bg-blue-500/20 group-hover:bg-blue-500/40 transition-all rounded-t-sm" style="height: {(stat.mail_in / 100) * 100}px"></div>
                            <div class="w-full bg-green-500/20 group-hover:bg-green-500/40 transition-all rounded-t-sm" style="height: {(stat.mail_out / 100) * 100}px"></div>
                        </div>
                        <div class="absolute -top-12 bg-black text-white px-2 py-1 rounded text-[8px] font-black opacity-0 group-hover:opacity-100 transition-all whitespace-nowrap z-10">
                            IN: {stat.mail_in} | OUT: {stat.mail_out}
                        </div>
                    </div>
                {/each}
            </div>
            <div class="flex justify-between mt-4 px-4">
                <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Há 30 dias</span>
                <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Hoje</span>
            </div>
        </div>

        <!-- Recent Logs -->
        <div class="space-y-4">
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-4">
                    <div class="w-1 h-6 bg-brand-orange rounded-full"></div>
                    <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Logs Recentes</h2>
                </div>
                <button class="text-brand-orange text-[9px] font-black uppercase tracking-widest hover:underline">Ver Todos os Logs</button>
            </div>

            <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 overflow-hidden shadow-sm">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50 dark:bg-white/[0.02]">
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Data</th>
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5">Cluster</th>
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5 text-center">In</th>
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5 text-center">Out</th>
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5 text-center">Spam</th>
                            <th class="px-8 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 dark:border-white/5 text-center">Virus</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each stats.slice(0, 10) as stat}
                            <tr class="hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors group">
                                <td class="px-8 py-5 text-[10px] font-bold text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-white/5">
                                    {new Date(stat.stats_date).toLocaleDateString()}
                                </td>
                                <td class="px-8 py-5 text-[10px] font-black text-black dark:text-white border-b border-gray-100 dark:border-white/5 uppercase tracking-tighter">
                                    {stat.cluster?.name}
                                </td>
                                <td class="px-8 py-5 text-[10px] font-black text-blue-500 border-b border-gray-100 dark:border-white/5 text-center">
                                    {stat.mail_in}
                                </td>
                                <td class="px-8 py-5 text-[10px] font-black text-green-500 border-b border-gray-100 dark:border-white/5 text-center">
                                    {stat.mail_out}
                                </td>
                                <td class="px-8 py-5 text-[10px] font-black text-orange-500 border-b border-gray-100 dark:border-white/5 text-center">
                                    {stat.spam_count}
                                </td>
                                <td class="px-8 py-5 text-[10px] font-black text-red-500 border-b border-gray-100 dark:border-white/5 text-center">
                                    {stat.virus_count}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
            <!-- Accounts Section -->
            <div>
                <h2 class="text-xl font-black text-black dark:text-white uppercase tracking-widest mb-6 px-2 flex items-center gap-3">
                    Contas do Gateway
                    <span class="text-[10px] bg-brand-orange/10 text-brand-orange px-2 py-1 rounded-md">{summary.total_accounts}</span>
                </h2>
                <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="border-b border-gray-100 dark:border-white/5">
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Usuário</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Email</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Função</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                                {#each accounts as account}
                                    <tr class="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                        <td class="px-6 py-4 font-black text-black dark:text-white tracking-tighter">{account.username}</td>
                                        <td class="px-6 py-4 text-[10px] text-gray-400">{account.email}</td>
                                        <td class="px-6 py-4">
                                            <span class="text-[8px] font-black text-blue-500 uppercase tracking-widest border border-blue-500/20 bg-blue-500/5 px-2 py-1 rounded-md">
                                                {account.role}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="w-2 h-2 rounded-full {account.is_active ? 'bg-green-500' : 'bg-red-500'}"></div>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Rules Section -->
            <div>
                <h2 class="text-xl font-black text-black dark:text-white uppercase tracking-widest mb-6 px-2 flex items-center gap-3">
                    Regras (White/Black List)
                </h2>
                <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="border-b border-gray-100 dark:border-white/5">
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Tipo</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Nome da Regra</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Origem/Destino</th>
                                    <th class="px-6 py-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                                {#each rules as rule}
                                    <tr class="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                        <td class="px-6 py-4">
                                            <span class="text-[8px] font-black uppercase tracking-widest px-2 py-1 rounded-md border 
                                                {rule.type === 'whitelist' ? 'text-green-500 border-green-500/20 bg-green-500/5' : 'text-red-500 border-red-500/20 bg-red-500/5'}">
                                                {rule.type}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 font-black text-black dark:text-white tracking-tighter">{rule.name}</td>
                                        <td class="px-6 py-4 text-[10px] text-gray-400">
                                            {rule.sender || rule.receiver || 'Qualquer'}
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="w-2 h-2 rounded-full {rule.is_active ? 'bg-green-500' : 'bg-red-500'}"></div>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
