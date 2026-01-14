<script lang="ts">
    import { Settings, Bell, Shield, Globe, Database, CreditCard, Save, RefreshCcw, Eye, EyeOff, Lock, Mail, Server } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiGetSettings, apiUpdateSettings } from '$lib/api';

    let activeTab = 'geral';
    let isSaving = false;
    let isLoading = true;

    // Form states
    let generalSettings = {
        orgName: 'Proxmon Datacenter',
        domain: 'proxmon.cloud',
        email: 'support@proxmon.cloud',
        timezone: 'America/Sao_Paulo'
    };

    let notificationSettings = {
        emailAlerts: true,
        slackAlerts: false,
        criticalOnly: true,
        dailyReport: true
    };

    let securitySettings = {
        twoFactor: false,
        sessionTimeout: '24h',
        ipWhitelist: ''
    };

    let apiSettings = {
        apiKey: 'px_live_7241_9921_bcda_1290',
        webhookUrl: 'https://api.proxmon.cloud/webhooks/proxmox',
        showKey: false
    };

    onMount(async () => {
        await loadSettings();
    });

    async function loadSettings() {
        isLoading = true;
        try {
            const response = await apiGetSettings();
            const data = response.data;
            
            if (data.general) generalSettings = data.general;
            if (data.notifications) notificationSettings = data.notifications;
            if (data.security) securitySettings = data.security;
            if (data.api) apiSettings = data.api;
        } catch (error) {
            console.error('Failed to load settings', error);
        } finally {
            isLoading = false;
        }
    }

    async function handleSave() {
        isSaving = true;
        try {
            await apiUpdateSettings({
                general: generalSettings,
                notifications: notificationSettings,
                security: securitySettings,
                api: apiSettings
            });
            alert('Configurações atualizadas com sucesso!');
        } catch (error) {
            console.error('Failed to save settings', error);
            alert('Erro ao salvar configurações.');
        } finally {
            isSaving = false;
        }
    }

    function toggleApiKey() {
        apiSettings.showKey = !apiSettings.showKey;
    }
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Preferências</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Configurações do <span class="text-brand-orange">Sistema</span>
            </h1>
        </div>
        
        <button 
            on:click={handleSave}
            disabled={isSaving || isLoading}
            class="bg-brand-orange hover:bg-brand-orange/90 text-black px-6 py-3 rounded-xl font-black text-[10px] transition-all shadow-xl shadow-brand-orange/20 flex items-center gap-3 uppercase tracking-widest active:scale-95 disabled:opacity-50"
        >
            {#if isSaving || isLoading}
                <RefreshCcw size={16} class="animate-spin" />
            {:else}
                <Save size={16} strokeWidth={3} />
            {/if}
            Salvar Alterações
        </button>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <!-- Sidebar Navigation -->
        <nav class="space-y-1">
            <button 
                on:click={() => activeTab = 'geral'}
                class="w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all text-left group border {activeTab === 'geral' ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/20' : 'hover:bg-white/5 text-gray-400 hover:text-white border-transparent'}"
            >
                <Globe size={18} />
                <span class="text-[10px] font-black uppercase tracking-widest">Geral</span>
            </button>
            <button 
                on:click={() => activeTab = 'notificacoes'}
                class="w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all text-left group border {activeTab === 'notificacoes' ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/20' : 'hover:bg-white/5 text-gray-400 hover:text-white border-transparent'}"
            >
                <Bell size={18} />
                <span class="text-[10px] font-black uppercase tracking-widest">Notificações</span>
            </button>
            <button 
                on:click={() => activeTab = 'seguranca'}
                class="w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all text-left group border {activeTab === 'seguranca' ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/20' : 'hover:bg-white/5 text-gray-400 hover:text-white border-transparent'}"
            >
                <Shield size={18} />
                <span class="text-[10px] font-black uppercase tracking-widest">Segurança</span>
            </button>
            <button 
                on:click={() => activeTab = 'api'}
                class="w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all text-left group border {activeTab === 'api' ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/20' : 'hover:bg-white/5 text-gray-400 hover:text-white border-transparent'}"
            >
                <Database size={18} />
                <span class="text-[10px] font-black uppercase tracking-widest">API & Integrações</span>
            </button>
        </nav>

        <!-- Main Content -->
        <div class="lg:col-span-3 bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 p-10">
            {#if activeTab === 'geral'}
                <div class="max-w-2xl">
                    <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter mb-8">Informações da Organização</h3>
                    
                    <div class="space-y-8">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Nome da Empresa</label>
                                <input bind:value={generalSettings.orgName} type="text" class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Domínio Principal</label>
                                <input bind:value={generalSettings.domain} type="text" class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all" />
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">E-mail de Suporte</label>
                            <input bind:value={generalSettings.email} type="email" class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all" />
                        </div>

                        <div class="space-y-2">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Fuso Horário</label>
                            <select bind:value={generalSettings.timezone} class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all appearance-none">
                                <option value="America/Sao_Paulo">Brasília (GMT-3)</option>
                                <option value="UTC">UTC (GMT+0)</option>
                                <option value="Europe/London">London (GMT+1)</option>
                            </select>
                        </div>
                    </div>
                </div>
            {:else if activeTab === 'notificacoes'}
                <div class="max-w-2xl">
                    <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter mb-8">Preferências de Notificação</h3>
                    
                    <div class="space-y-6">
                        <div class="flex items-center justify-between p-6 bg-gray-50 dark:bg-white/5 rounded-2xl border border-transparent hover:border-brand-orange/20 transition-all">
                            <div class="flex items-center gap-4">
                                <Mail class="text-brand-orange" size={20} />
                                <div>
                                    <p class="text-[10px] font-black text-black dark:text-white uppercase tracking-widest">Alertas por E-mail</p>
                                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">Notificações críticas via e-mail</p>
                                </div>
                            </div>
                            <input type="checkbox" bind:checked={notificationSettings.emailAlerts} class="w-10 h-5 rounded-full bg-gray-200 dark:bg-white/10 appearance-none cursor-pointer relative checked:bg-brand-orange transition-all before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-5 before:transition-transform" />
                        </div>

                        <div class="flex items-center justify-between p-6 bg-gray-50 dark:bg-white/5 rounded-2xl border border-transparent hover:border-brand-orange/20 transition-all">
                            <div class="flex items-center gap-4">
                                <Bell class="text-brand-orange" size={20} />
                                <div>
                                    <p class="text-[10px] font-black text-black dark:text-white uppercase tracking-widest">Apenas Alertas Críticos</p>
                                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">Silenciar avisos informativos</p>
                                </div>
                            </div>
                            <input type="checkbox" bind:checked={notificationSettings.criticalOnly} class="w-10 h-5 rounded-full bg-gray-200 dark:bg-white/10 appearance-none cursor-pointer relative checked:bg-brand-orange transition-all before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-5 before:transition-transform" />
                        </div>

                        <div class="flex items-center justify-between p-6 bg-gray-50 dark:bg-white/5 rounded-2xl border border-transparent hover:border-brand-orange/20 transition-all opacity-50">
                            <div class="flex items-center gap-4">
                                <Database class="text-gray-400" size={20} />
                                <div>
                                    <p class="text-[10px] font-black text-black dark:text-white uppercase tracking-widest">Integração Slack (BETA)</p>
                                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">Disponível em breve</p>
                                </div>
                            </div>
                            <input type="checkbox" disabled class="w-10 h-5 rounded-full bg-gray-200 dark:bg-white/10 appearance-none cursor-not-allowed" />
                        </div>
                    </div>
                </div>
            {:else if activeTab === 'seguranca'}
                <div class="max-w-2xl">
                    <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter mb-8">Segurança & Autenticação</h3>
                    
                    <div class="space-y-8">
                        <div class="p-8 bg-brand-orange/5 border border-brand-orange/10 rounded-[2rem]">
                            <div class="flex items-center gap-4 mb-6">
                                <div class="w-12 h-12 rounded-2xl bg-brand-orange flex items-center justify-center text-black">
                                    <Lock size={24} strokeWidth={3} />
                                </div>
                                <div>
                                    <h4 class="text-[11px] font-black text-black dark:text-white uppercase tracking-widest">Autenticação de Dois Fatores (2FA)</h4>
                                    <p class="text-[9px] text-gray-500 font-bold uppercase tracking-widest mt-1">Proteja sua conta com uma camada extra de segurança.</p>
                                </div>
                            </div>
                            <button class="bg-black dark:bg-white text-white dark:text-black px-8 py-3 rounded-xl font-black text-[9px] uppercase tracking-widest hover:scale-105 transition-transform active:scale-95">Configurar 2FA</button>
                        </div>

                        <div class="space-y-4">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Tempo Limite de Sessão</label>
                            <div class="grid grid-cols-3 gap-4">
                                {#each ['1h', '12h', '24h'] as time}
                                    <button 
                                        on:click={() => securitySettings.sessionTimeout = time}
                                        class="py-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border {securitySettings.sessionTimeout === time ? 'bg-brand-orange text-black border-brand-orange shadow-lg shadow-brand-orange/10' : 'bg-gray-50 dark:bg-white/5 text-gray-400 border-transparent hover:border-white/10'}"
                                    >
                                        {time}
                                    </button>
                                {/each}
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Whitelist de IPs (Opcional)</label>
                            <textarea 
                                bind:value={securitySettings.ipWhitelist}
                                placeholder="0.0.0.0/0"
                                class="w-full h-32 bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all resize-none"
                            ></textarea>
                            <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest ml-2">Separe múltiplos IPs por vírgula.</p>
                        </div>
                    </div>
                </div>
            {:else if activeTab === 'api'}
                <div class="max-w-2xl">
                    <h3 class="text-xl font-black text-black dark:text-white uppercase tracking-tighter mb-8">API & Integrações Externas</h3>
                    
                    <div class="space-y-8">
                        <div class="space-y-4">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Chave de API Principal</label>
                            <div class="flex gap-2">
                                <div class="flex-1 relative">
                                    <input 
                                        type={apiSettings.showKey ? 'text' : 'password'} 
                                        readonly 
                                        value={apiSettings.apiKey}
                                        class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[11px] font-black tracking-widest text-black dark:text-white focus:ring-0" 
                                    />
                                    <button 
                                        on:click={toggleApiKey}
                                        class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-brand-orange transition-colors"
                                    >
                                        {#if apiSettings.showKey}
                                            <EyeOff size={16} />
                                        {:else}
                                            <Eye size={16} />
                                        {/if}
                                    </button>
                                </div>
                                <button class="bg-gray-50 dark:bg-white/5 hover:bg-white/10 text-white px-6 rounded-xl transition-all active:scale-95 border border-white/5">
                                    <RefreshCcw size={16} class="text-brand-orange" />
                                </button>
                            </div>
                            <p class="text-[8px] text-red-400 font-black uppercase tracking-widest ml-2">Atenção: Nunca compartilhe sua chave de API.</p>
                        </div>

                        <div class="space-y-4">
                            <label class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2">Webhook de Sincronização Proxmox</label>
                            <div class="p-6 bg-gray-50 dark:bg-white/5 rounded-2xl border border-transparent flex items-center gap-4">
                                <Server class="text-brand-orange flex-shrink-0" size={20} />
                                <div class="flex-1 min-w-0">
                                    <p class="text-[10px] font-black text-black dark:text-white uppercase tracking-widest truncate">{apiSettings.webhookUrl}</p>
                                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest mt-1">Status: Conectado e Sincronizando</p>
                                </div>
                                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            </div>
                        </div>

                        <div class="pt-8 border-t border-gray-100 dark:border-white/5">
                            <div class="flex items-center gap-4">
                                <Database class="text-gray-400" size={24} />
                                <div>
                                    <h4 class="text-[10px] font-black text-black dark:text-white uppercase tracking-widest">Exportação de Dados</h4>
                                    <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest mt-1">Baixe todos os logs e métricas em formato JSON ou CSV.</p>
                                </div>
                                <button class="ml-auto text-[9px] font-black text-brand-orange uppercase tracking-widest hover:underline">Exportar Agora</button>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    </div>
</div>
