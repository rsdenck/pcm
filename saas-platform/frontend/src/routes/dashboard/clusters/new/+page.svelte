<script lang="ts">
    import { ChevronLeft, Server, Shield, Globe, Activity } from 'lucide-svelte';
    import { api } from '$lib/api';

    let name = '';
    let hostname = '';
    let type = 'pve';
    let username = '';
    let password = '';
    let port = 8006;
    let loading = false;
    let message = '';

    async function handleSubmit() {
        loading = true;
        try {
            // Placeholder for actual API call
            // await api.post('/clusters', { name, hostname, type, username, password, port });
            message = 'Funcionalidade de API será implementada em breve!';
        } catch (error) {
            message = 'Erro ao conectar com o backend.';
        } finally {
            loading = false;
        }
    }
</script>

<div class="p-8 max-w-4xl mx-auto">
    <a href="/dashboard" class="inline-flex items-center gap-2 text-gray-500 hover:text-brand-orange transition-colors font-black text-[10px] uppercase tracking-widest mb-10">
        <ChevronLeft size={16} strokeWidth={3} />
        Voltar ao Dashboard
    </a>

    <header class="mb-12">
        <h1 class="text-5xl font-black text-white tracking-tighter mb-4">
            Novo <span class="text-brand-orange">Cluster</span>
        </h1>
        <p class="text-gray-500 font-bold uppercase tracking-widest text-[10px]">Configuração de Infraestrutura Proxmox</p>
    </header>

    <form on:submit|preventDefault={handleSubmit} class="space-y-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Basic Info -->
            <div class="bg-white/5 p-8 rounded-[2.5rem] border border-white/5 space-y-6">
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-10 h-10 bg-brand-orange/10 rounded-2xl flex items-center justify-center border border-brand-orange/20">
                        <Server class="text-brand-orange" size={20} />
                    </div>
                    <h2 class="text-lg font-black text-white uppercase tracking-tight">Identificação</h2>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Nome do Cluster</label>
                        <input 
                            bind:value={name}
                            type="text" 
                            placeholder="Ex: Datacenter Principal"
                            class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                        />
                    </div>
                    <div>
                        <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Tipo de Serviço</label>
                        <select 
                            bind:value={type}
                            class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none appearance-none"
                        >
                            <option value="pve">Proxmox VE (Virtual Environment)</option>
                            <option value="pbs">Proxmox Backup Server</option>
                            <option value="pmg">Proxmox Mail Gateway</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Connection Info -->
            <div class="bg-white/5 p-8 rounded-[2.5rem] border border-white/5 space-y-6">
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-10 h-10 bg-brand-orange/10 rounded-2xl flex items-center justify-center border border-brand-orange/20">
                        <Globe class="text-brand-orange" size={20} />
                    </div>
                    <h2 class="text-lg font-black text-white uppercase tracking-tight">Conexão</h2>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Endereço IP / Hostname</label>
                        <input 
                            bind:value={hostname}
                            type="text" 
                            placeholder="192.168.1.100"
                            class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                        />
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Porta</label>
                            <input 
                                bind:value={port}
                                type="number" 
                                class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                            />
                        </div>
                        <div>
                            <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Timeout (s)</label>
                            <input 
                                type="number" 
                                value="30"
                                class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Credentials -->
            <div class="md:col-span-2 bg-white/5 p-8 rounded-[2.5rem] border border-white/5 space-y-6">
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-10 h-10 bg-brand-orange/10 rounded-2xl flex items-center justify-center border border-brand-orange/20">
                        <Shield class="text-brand-orange" size={20} />
                    </div>
                    <h2 class="text-lg font-black text-white uppercase tracking-tight">Credenciais de Acesso</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Usuário / API Token ID</label>
                        <input 
                            bind:value={username}
                            type="text" 
                            placeholder="root@pam"
                            class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                        />
                    </div>
                    <div>
                        <label class="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 px-1">Senha / Secret</label>
                        <input 
                            bind:value={password}
                            type="password" 
                            placeholder="••••••••••••"
                            class="w-full bg-brand-black border border-white/5 rounded-2xl px-5 py-4 text-sm font-bold text-white focus:border-brand-orange/50 transition-all outline-none"
                        />
                    </div>
                </div>
            </div>
        </div>

        <div class="flex items-center justify-between gap-6 pt-4">
            {#if message}
                <div class="text-brand-orange font-black text-xs uppercase tracking-widest animate-pulse">
                    {message}
                </div>
            {/if}
            
            <button 
                type="submit"
                disabled={loading}
                class="ml-auto bg-brand-orange hover:bg-brand-orange/90 text-black px-12 py-5 rounded-[2rem] font-black text-sm transition-all shadow-2xl shadow-brand-orange/20 uppercase tracking-[0.2em] flex items-center gap-3 active:scale-95 disabled:opacity-50"
            >
                {#if loading}
                    <div class="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                    Processando...
                {:else}
                    <Activity size={20} strokeWidth={3} />
                    Conectar Cluster
                {/if}
            </button>
        </div>
    </form>
</div>
