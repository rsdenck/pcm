<script>
    import { Network, Globe, Share2, Shield, RefreshCcw, Activity, Zap, Layers } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiGetSdn } from '$lib/api';

    let loading = true;
    let zones = [];
    let stats = {
        total_vnets: 0,
        total_zones: 0
    };

    onMount(async () => {
        await refreshData();
    });

    async function refreshData() {
        loading = true;
        try {
            const sdnRes = await apiGetSdn();
            zones = sdnRes.data.zones || [];
            stats.total_vnets = sdnRes.data.total_vnets || 0;
            stats.total_zones = sdnRes.data.total_zones || 0;
        } catch (error) {
            console.error('Failed to fetch SDN data', error);
        } finally {
            loading = false;
        }
    }
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Observabilidade de Rede</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter uppercase">
                Monitoramento <span class="text-brand-orange">SDN</span>
            </h1>
        </div>
        
        <button 
            on:click={refreshData}
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
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Sincronizando Topologia SDN...</p>
        </div>
    {:else}
        <!-- SDN Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="bg-white dark:bg-white/5 p-8 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4 mb-6">
                    <div class="w-12 h-12 bg-brand-orange/10 rounded-2xl flex items-center justify-center">
                        <Globe class="text-brand-orange" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Zonas Monitoradas</div>
                        <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{stats.total_zones}</div>
                    </div>
                </div>
                <div class="h-1.5 w-full bg-gray-50 dark:bg-brand-black rounded-full overflow-hidden">
                    <div class="h-full bg-brand-orange w-full"></div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-8 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4 mb-6">
                    <div class="w-12 h-12 bg-brand-orange/10 rounded-2xl flex items-center justify-center">
                        <Share2 class="text-brand-orange" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Redes Virtuais</div>
                        <div class="text-3xl font-black text-black dark:text-white tracking-tighter">{stats.total_vnets}</div>
                    </div>
                </div>
                <div class="h-1.5 w-full bg-gray-50 dark:bg-brand-black rounded-full overflow-hidden">
                    <div class="h-full bg-brand-orange w-full"></div>
                </div>
            </div>

            <div class="bg-white dark:bg-white/5 p-8 rounded-[2.5rem] border border-gray-100 dark:border-white/5 shadow-sm">
                <div class="flex items-center gap-4 mb-6">
                    <div class="w-12 h-12 bg-brand-orange/10 rounded-2xl flex items-center justify-center">
                        <Shield class="text-brand-orange" size={24} />
                    </div>
                    <div>
                        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Segurança de Rede</div>
                        <div class="text-3xl font-black text-black dark:text-white tracking-tighter">VXLAN/EVPN</div>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                    <span class="text-[10px] font-black text-green-500 uppercase tracking-widest">Proteção Ativa</span>
                </div>
            </div>
        </div>

        <!-- Zones Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {#each zones as zone}
                <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 p-8 shadow-sm">
                    <div class="flex justify-between items-start mb-8">
                        <div class="flex items-center gap-4">
                            <div class="w-14 h-14 bg-brand-orange/5 rounded-2xl flex items-center justify-center border border-brand-orange/10">
                                <Layers class="text-brand-orange" size={24} />
                            </div>
                            <div>
                                <h3 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">{zone.zone_name}</h3>
                                <div class="flex items-center gap-2">
                                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Tipo: {zone.type}</span>
                                    <div class="w-1 h-1 bg-gray-700 rounded-full"></div>
                                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">MTU: {zone.mtu || 1500}</span>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-lg">
                            <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                            <span class="text-[9px] font-black text-green-500 uppercase tracking-widest">Operacional</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-gray-50 dark:bg-brand-black/40 p-4 rounded-2xl border border-gray-100 dark:border-white/5">
                            <div class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-2">Redes Virtuais</div>
                            <div class="text-2xl font-black text-black dark:text-white tracking-tighter">{zone.vnets?.length || 0}</div>
                        </div>
                        <div class="bg-gray-50 dark:bg-brand-black/40 p-4 rounded-2xl border border-gray-100 dark:border-white/5">
                            <div class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-2">Cluster</div>
                            <div class="text-xs font-black text-black dark:text-white tracking-tighter truncate">{zone.cluster?.name || 'Global'}</div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>
