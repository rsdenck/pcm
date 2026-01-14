<script>
    import { Network, Globe, Share2, Layers, Search, Filter, Plus, Activity, Zap, Shield, ChevronRight, X, Settings2, Save, Trash2 } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiGetSdn, apiGetDashboardData, apiCreateSdnZone, apiCreateSdnVnet, apiCreateSdnSubnet, apiCreateSdnFirewallRule, apiApplySdn, apiDeleteSdnZone, apiDeleteSdnVnet, apiDeleteSdnSubnet, apiDeleteSdnFirewallRule } from '$lib/api';

    let loading = true;
    let zones = [];
    let firewallRules = [];
    let clusters = [];
    let stats = {
        total_vnets: 0,
        total_zones: 0
    };

    // Modal states
    let showZoneModal = false;
    let showVnetModal = false;
    let showSubnetModal = false;
    let showFirewallModal = false;
    let processing = false;

    // Form data
    let zoneForm = { cluster_id: '', zone: '', type: 'vxlan', mtu: 1500 };
    let vnetForm = { cluster_id: '', vnet: '', zone: '', tag: '', alias: '' };
    let subnetForm = { cluster_id: '', vnet: '', cidr: '', gateway: '', snat: true };
    let firewallForm = { cluster_id: '', action: 'ACCEPT', type: 'in', source: '', dest: '', proto: 'tcp', dport: '', enable: true, comment: '' };

    onMount(async () => {
        await refreshData();
    });

    async function refreshData() {
        loading = true;
        try {
            const [sdnRes, dashRes] = await Promise.all([
                apiGetSdn(),
                apiGetDashboardData()
            ]);
            
            zones = sdnRes.data.zones || [];
            firewallRules = sdnRes.data.firewall_rules || [];
            stats.total_vnets = sdnRes.data.total_vnets || 0;
            stats.total_zones = sdnRes.data.total_zones || 0;
            
            clusters = dashRes.clusters || [];
        } catch (error) {
            console.error('Failed to fetch SDN data', error);
        } finally {
            loading = false;
        }
    }

    async function handleCreateZone() {
        processing = true;
        try {
            await apiCreateSdnZone(zoneForm);
            showZoneModal = false;
            await refreshData();
        } catch (error) {
            alert('Erro ao criar zona: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleCreateVnet() {
        processing = true;
        try {
            await apiCreateSdnVnet(vnetForm);
            showVnetModal = false;
            await refreshData();
        } catch (error) {
            alert('Erro ao criar VNet: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleCreateSubnet() {
        processing = true;
        try {
            await apiCreateSdnSubnet(subnetForm);
            showSubnetModal = false;
            await refreshData();
        } catch (error) {
            alert('Erro ao criar Subnet: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleCreateFirewallRule() {
        processing = true;
        try {
            await apiCreateSdnFirewallRule(firewallForm);
            showFirewallModal = false;
            await refreshData();
        } catch (error) {
            alert('Erro ao criar regra de firewall: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleApplySDN(clusterId) {
         if (!confirm('Deseja aplicar as configurações SDN agora? Isso pode causar uma breve interrupção na rede.')) return;
         
         processing = true;
         try {
             await apiApplySdn(clusterId);
             alert('Configurações SDN aplicadas com sucesso!');
             await refreshData();
         } catch (error) {
             alert('Erro ao aplicar SDN: ' + (error.response?.data?.error || error.message));
         } finally {
             processing = false;
         }
     }

     async function handleDeleteZone(clusterId, zoneName) {
        if (!confirm(`Tem certeza que deseja excluir a zona ${zoneName}?`)) return;
        
        processing = true;
        try {
            await apiDeleteSdnZone(clusterId, zoneName);
            await refreshData();
        } catch (error) {
            alert('Erro ao excluir zona: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleDeleteVnet(clusterId, vnetName) {
        if (!confirm(`Tem certeza que deseja excluir a VNet ${vnetName}?`)) return;
        
        processing = true;
        try {
            await apiDeleteSdnVnet(clusterId, vnetName);
            await refreshData();
        } catch (error) {
            alert('Erro ao excluir VNet: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleDeleteSubnet(clusterId, vnetName, subnetCidr) {
        if (!confirm(`Tem certeza que deseja excluir a subnet ${subnetCidr}?`)) return;
        
        processing = true;
        try {
            await apiDeleteSdnSubnet(clusterId, vnetName, subnetCidr);
            await refreshData();
        } catch (error) {
            alert('Erro ao excluir subnet: ' + (error.response?.data?.error || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleDeleteFirewallRule(clusterId, pos) {
        if (!confirm('Tem certeza que deseja excluir esta regra de firewall?')) return;
        
        processing = true;
        try {
            await apiDeleteSdnFirewallRule(clusterId, pos);
            await refreshData();
        } catch (error) {
            console.error('Failed to delete firewall rule', error);
            alert('Erro ao excluir regra de firewall: ' + (error.response?.data?.message || error.message));
        } finally {
            processing = false;
        }
    }

    async function handleApplySdn() {
        if (clusters.length === 0) return;
        
        const clusterId = clusters[0].id; // Apply to the first cluster by default
        if (!confirm('Deseja aplicar as alterações de SDN no cluster? Isso pode levar alguns segundos.')) return;

        processing = true;
        try {
            await apiApplySdn(clusterId);
            alert('Alterações de SDN aplicadas com sucesso!');
            await refreshData();
        } catch (error) {
            console.error('Failed to apply SDN changes', error);
            alert('Erro ao aplicar alterações SDN: ' + (error.response?.data?.message || error.message));
        } finally {
            processing = false;
        }
    }

     function openSubnetModal(clusterId, vnetName) {
        subnetForm = { cluster_id: clusterId, vnet: vnetName, cidr: '', gateway: '', snat: true };
        showSubnetModal = true;
    }

    function openFirewallModal() {
        firewallForm = { cluster_id: '', action: 'ACCEPT', type: 'in', source: '', dest: '', proto: 'tcp', dport: '', enable: true, comment: '' };
        showFirewallModal = true;
    }
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <div class="flex items-center justify-between mb-12">
        <div class="flex items-center gap-6">
            <div class="p-4 bg-brand-orange/10 rounded-[1.5rem] border border-brand-orange/20">
                <Settings2 size={32} class="text-brand-orange" strokeWidth={2} />
            </div>
            <div>
                <h1 class="text-4xl font-black text-black dark:text-white tracking-tighter uppercase">Gestão <span class="text-brand-orange">SDN</span></h1>
                <div class="flex items-center gap-3 mt-1">
                    <div class="w-2 h-2 bg-brand-orange rounded-full animate-pulse"></div>
                    <p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Configurações Técnicas de Rede</p>
                </div>
            </div>
        </div>

        <div class="flex items-center gap-4">
            <button 
                on:click={handleApplySdn}
                disabled={processing || clusters.length === 0}
                class="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95 shadow-lg shadow-green-500/20 disabled:opacity-50">
                <Zap size={16} strokeWidth={3} />
                Aplicar Alterações
            </button>
            <button 
                on:click={() => showZoneModal = true}
                class="bg-white dark:bg-white/5 border border-gray-100 dark:border-white/5 text-black dark:text-white px-8 py-3 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95">
                <Plus size={16} strokeWidth={3} />
                Nova Zona
            </button>
        </div>
    </div>

    {#if loading}
        <div class="flex flex-col justify-center items-center h-[50vh] gap-6">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-[4px] border-brand-orange/10 rounded-full"></div>
                <div class="absolute inset-0 border-[4px] border-brand-orange border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-brand-orange font-black animate-pulse uppercase tracking-[0.3em] text-[9px]">Carregando Configurações SDN...</p>
        </div>
    {:else}
        <!-- Zones and VNets -->
        <div class="space-y-6 mb-12">
            {#each zones as zone}
                <div class="bg-white dark:bg-white/5 rounded-[3rem] border border-gray-100 dark:border-white/5 overflow-hidden shadow-sm">
                    <div class="p-8 border-b border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-white/[0.02]">
                        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                            <div class="flex items-center gap-6">
                                <div class="w-16 h-16 bg-white dark:bg-brand-black rounded-[1.5rem] flex items-center justify-center border border-gray-100 dark:border-white/10 shadow-sm">
                                    <Layers class="text-brand-orange" size={28} />
                                </div>
                                <div>
                                    <div class="flex items-center gap-3 mb-1">
                                        <h3 class="text-2xl font-black text-black dark:text-white tracking-tighter">{zone.zone_name}</h3>
                                        <span class="px-3 py-1 bg-brand-orange/10 text-brand-orange rounded-full text-[9px] font-black uppercase tracking-widest border border-brand-orange/10">{zone.type}</span>
                                    </div>
                                    <div class="flex items-center gap-4">
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Cluster: {zone.cluster?.name || 'Global'}</span>
                                        <div class="w-1 h-1 bg-gray-300 dark:bg-gray-700 rounded-full"></div>
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">MTU: {zone.mtu || '1500'}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="flex gap-4 items-center">
                                <button 
                                    on:click={() => showVnetModal = true}
                                    class="bg-brand-orange text-black px-4 py-2 rounded-lg font-black text-[9px] uppercase tracking-widest hover:bg-brand-orange/90 transition-all">
                                    Nova VNet
                                </button>
                                <button 
                                    on:click={() => handleDeleteZone(zone.cluster_id, zone.zone_name)}
                                    class="p-2 hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-all"
                                    title="Excluir Zona">
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {#each zone.vnets || [] as vnet}
                                <div class="group bg-gray-50 dark:bg-brand-black/40 p-6 rounded-[2rem] border border-gray-100 dark:border-white/5 hover:border-brand-orange/30 transition-all duration-500">
                                    <div class="flex items-center justify-between mb-6">
                                        <div class="flex items-center gap-4">
                                            <div class="w-10 h-10 bg-white dark:bg-white/5 rounded-xl flex items-center justify-center border border-gray-100 dark:border-white/5 group-hover:border-brand-orange/20 transition-all">
                                                <Zap class="text-brand-orange" size={18} />
                                            </div>
                                            <div>
                                                <h4 class="text-sm font-black text-black dark:text-white tracking-tighter uppercase">{vnet.vnet_name}</h4>
                                                <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Tag: {vnet.tag || 'None'}</span>
                                            </div>
                                        </div>
                                        <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
                                            <button 
                                                on:click={() => openSubnetModal(zone.cluster_id, vnet.vnet_name)}
                                                class="w-8 h-8 rounded-lg bg-white dark:bg-white/5 flex items-center justify-center hover:bg-brand-orange hover:text-black transition-all"
                                                title="Adicionar Subnet">
                                                <Plus size={14} strokeWidth={3} />
                                            </button>
                                            <button 
                                                on:click={() => handleDeleteVnet(zone.cluster_id, vnet.vnet_name)}
                                                class="w-8 h-8 rounded-lg bg-white dark:bg-white/5 flex items-center justify-center hover:bg-red-500 hover:text-white transition-all"
                                                title="Excluir VNet">
                                                <Trash2 size={14} strokeWidth={3} />
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div class="space-y-2">
                                        {#each vnet.subnets || [] as subnet}
                                            <div class="flex items-center justify-between p-3 bg-white dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/5">
                                                <span class="text-[10px] font-mono text-gray-500">{subnet.cidr}</span>
                                                <button 
                                                    on:click={() => handleDeleteSubnet(zone.cluster_id, vnet.vnet_name, subnet.cidr)}
                                                    class="text-gray-400 hover:text-red-500 transition-all">
                                                    <Trash2 size={12} />
                                                </button>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Firewall Section -->
        <div class="bg-white dark:bg-white/5 rounded-[3rem] border border-gray-100 dark:border-white/5 p-8">
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-brand-orange/10 rounded-xl flex items-center justify-center">
                        <Shield class="text-brand-orange" size={20} />
                    </div>
                    <h2 class="text-xl font-black text-black dark:text-white tracking-tighter uppercase">Regras de Firewall SDN</h2>
                </div>
                <button 
                    on:click={openFirewallModal}
                    class="bg-white dark:bg-white/5 border border-gray-100 dark:border-white/5 text-black dark:text-white px-6 py-2 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95">
                    <Plus size={14} strokeWidth={3} />
                    Nova Regra
                </button>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead>
                        <tr class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 dark:border-white/5">
                            <th class="px-4 py-4">Ação</th>
                            <th class="px-4 py-4">Tipo</th>
                            <th class="px-4 py-4">Origem</th>
                            <th class="px-4 py-4">Destino</th>
                            <th class="px-4 py-4">Protocolo</th>
                            <th class="px-4 py-4">Porta</th>
                            <th class="px-4 py-4">Status</th>
                            <th class="px-4 py-4 text-right">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                        {#each firewallRules as rule}
                            <tr class="text-[10px] font-bold text-gray-600 dark:text-gray-400">
                                <td class="px-4 py-4">
                                    <span class="px-2 py-1 rounded-md {rule.action === 'ACCEPT' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}">
                                        {rule.action}
                                    </span>
                                </td>
                                <td class="px-4 py-4 uppercase">{rule.type}</td>
                                <td class="px-4 py-4">{rule.source || 'Qualquer'}</td>
                                <td class="px-4 py-4">{rule.dest || 'Qualquer'}</td>
                                <td class="px-4 py-4 uppercase">{rule.proto || 'Qualquer'}</td>
                                <td class="px-4 py-4">{rule.dport || 'Qualquer'}</td>
                                <td class="px-4 py-4">
                                    <div class="flex items-center gap-2">
                                        <div class="w-1.5 h-1.5 rounded-full {rule.enable ? 'bg-green-500' : 'bg-gray-500'}"></div>
                                        <span>{rule.enable ? 'Ativa' : 'Inativa'}</span>
                                    </div>
                                </td>
                                <td class="px-4 py-4 text-right">
                                    <button 
                                        on:click={() => handleDeleteFirewallRule(rule.cluster_id, rule.pos)}
                                        class="p-2 hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-all">
                                        <Trash2 size={14} />
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

<!-- Modals (Simplified for this example, same logic as before) -->
{#if showZoneModal}
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
        <div class="bg-white dark:bg-brand-black w-full max-w-md rounded-[2.5rem] border border-gray-100 dark:border-white/5 overflow-hidden shadow-2xl">
            <div class="p-8 border-b border-gray-100 dark:border-white/5 flex justify-between items-center">
                <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter">Configurar Nova Zona</h3>
                <button on:click={() => showZoneModal = false} class="text-gray-400 hover:text-white transition-all"><X size={24} /></button>
            </div>
            <div class="p-8 space-y-6">
                <div>
                    <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-2">Cluster</label>
                    <select bind:value={zoneForm.cluster_id} class="w-full bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:border-brand-orange transition-all outline-none">
                        <option value="">Selecionar Cluster</option>
                        {#each clusters as cluster}
                            <option value={cluster.id}>{cluster.name}</option>
                        {/each}
                    </select>
                </div>
                <div>
                    <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-2">Nome da Zona</label>
                    <input type="text" bind:value={zoneForm.zone} placeholder="ex: vxlan-main" class="w-full bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:border-brand-orange transition-all outline-none" />
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-2">Tipo</label>
                        <select bind:value={zoneForm.type} class="w-full bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:border-brand-orange transition-all outline-none">
                            <option value="vxlan">VXLAN</option>
                            <option value="vlan">VLAN</option>
                            <option value="simple">Simple</option>
                            <option value="evpn">EVPN</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-2">MTU</label>
                        <input type="number" bind:value={zoneForm.mtu} placeholder="1500" class="w-full bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:border-brand-orange transition-all outline-none" />
                    </div>
                </div>
                <button 
                    on:click={handleCreateZone}
                    disabled={processing}
                    class="w-full bg-brand-orange text-black py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-brand-orange/90 transition-all shadow-lg shadow-brand-orange/20">
                    {processing ? 'Criando...' : 'Criar Zona'}
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Additional Modals for VNet, Subnet and Firewall would go here -->
