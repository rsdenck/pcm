<script lang="ts">
    import { Users, UserPlus, Shield, Key, Mail, MoreVertical, Search, Check, X, Trash2, Edit2, RefreshCcw } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { getUsers, createUser, updateUser, deleteUser as apiDeleteUser } from '$lib/api';

    let showInviteModal = false;
    let showEditModal = false;
    let inviteEmail = '';
    let inviteRole = 'editor';
    let isInviting = false;
    let searchQuery = '';
    let loading = true;

    let users: any[] = [];
    let editingUser: any = null;

    async function loadUsers() {
        loading = true;
        try {
            users = await getUsers();
        } catch (error) {
            console.error('Failed to load users', error);
        } finally {
            loading = false;
        }
    }

    onMount(loadUsers);

    function toggleInviteModal() {
        showInviteModal = !showInviteModal;
    }

    function toggleEditModal(user = null) {
        editingUser = user ? { ...user } : null;
        showEditModal = !!user;
    }

    async function handleInvite() {
        if (!inviteEmail) return;
        isInviting = true;
        
        try {
            // For invitation, we'll create a user with a temporary password
            // In a real app, this would send an invitation email
            await createUser({
                name: inviteEmail.split('@')[0],
                email: inviteEmail,
                role: inviteRole,
                password: 'password123' // Temp password
            });
            
            await loadUsers();
            inviteEmail = '';
            showInviteModal = false;
        } catch (error) {
            console.error('Failed to invite user', error);
            alert('Erro ao convidar usuário.');
        } finally {
            isInviting = false;
        }
    }

    async function handleUpdateUser() {
        if (!editingUser) return;
        isInviting = true;
        
        try {
            await updateUser(editingUser.id, {
                name: editingUser.name,
                role: editingUser.role.toLowerCase()
            });
            await loadUsers();
            showEditModal = false;
        } catch (error) {
            console.error('Failed to update user', error);
            alert('Erro ao atualizar usuário.');
        } finally {
            isInviting = false;
        }
    }

    async function handleDeleteUser(id) {
        if (confirm('Tem certeza que deseja remover este usuário?')) {
            try {
                await apiDeleteUser(id);
                await loadUsers();
            } catch (error) {
                console.error('Failed to delete user', error);
                alert('Erro ao deletar usuário.');
            }
        }
    }

    function getInitial(name) {
        return name ? name.substring(0, 2).toUpperCase() : '??';
    }

    function formatLastAccess(dateString) {
        if (!dateString) return 'Nunca';
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
        
        if (diffInHours < 1) return 'Agora mesmo';
        if (diffInHours < 24) return `Há ${diffInHours} horas`;
        return `Há ${Math.floor(diffInHours / 24)} dias`;
    }

    $: filteredUsers = users.filter(u => 
        (u.name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
         u.email?.toLowerCase().includes(searchQuery.toLowerCase()))
    );
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                <span class="text-[8px] font-black text-brand-orange uppercase tracking-[0.4em]">Controle de Acesso</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-black dark:text-white tracking-tighter">
                Gestão de <span class="text-brand-orange">Usuários</span>
            </h1>
        </div>
        
        <button 
            on:click={toggleInviteModal}
            class="bg-brand-orange hover:bg-brand-orange/90 text-black px-6 py-3 rounded-xl font-black text-[10px] transition-all shadow-xl shadow-brand-orange/20 flex items-center gap-3 uppercase tracking-widest active:scale-95"
        >
            <UserPlus size={16} strokeWidth={3} />
            Convidar Membro
        </button>
    </header>

    <div class="bg-white dark:bg-white/5 rounded-[2.5rem] border border-gray-100 dark:border-white/5 overflow-hidden">
        <div class="p-6 border-b border-gray-100 dark:border-white/5 flex items-center gap-4">
            <div class="flex-1 relative">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={14} />
                <input 
                    bind:value={searchQuery}
                    type="text" 
                    placeholder="BUSCAR USUÁRIO..." 
                    class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-3 pl-12 pr-4 text-[9px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all"
                />
            </div>
            <button 
                on:click={loadUsers}
                class="p-3 bg-gray-50 dark:bg-white/5 rounded-xl text-gray-400 hover:text-brand-orange transition-colors"
                disabled={loading}
            >
                <RefreshCcw size={14} class={loading ? 'animate-spin' : ''} />
            </button>
        </div>
        
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-50 dark:bg-white/5">
                    <tr>
                        <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Usuário</th>
                        <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Cargo</th>
                        <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Status</th>
                        <th class="text-left px-8 py-4 text-[8px] font-black text-gray-400 uppercase tracking-widest">Último Acesso</th>
                        <th class="px-8 py-4 text-right">Ações</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                    {#if loading}
                        <tr>
                            <td colspan="5" class="px-8 py-12 text-center">
                                <div class="flex flex-col items-center gap-4">
                                    <RefreshCcw size={24} class="animate-spin text-brand-orange" />
                                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Carregando usuários...</span>
                                </div>
                            </td>
                        </tr>
                    {:else}
                        {#each filteredUsers as user (user.id)}
                            <tr class="hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors group">
                                <td class="px-8 py-5">
                                    <div class="flex items-center gap-4">
                                        <div class="w-8 h-8 rounded-lg bg-brand-orange flex items-center justify-center text-black font-black text-[10px]">
                                            {getInitial(user.name)}
                                        </div>
                                        <div>
                                            <div class="text-[10px] font-black text-black dark:text-white uppercase tracking-tight">
                                                {user.name}
                                            </div>
                                            <div class="text-[8px] text-gray-400 font-bold uppercase tracking-widest">
                                                {user.email}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-8 py-5">
                                    <div class="flex items-center gap-2">
                                        <Shield size={10} class="text-brand-orange" />
                                        <span class="text-[9px] font-black text-black dark:text-white uppercase tracking-widest">
                                            {user.role}
                                        </span>
                                    </div>
                                </td>
                                <td class="px-8 py-5">
                                    <span class="px-2 py-0.5 rounded-full text-[7px] font-black {user.email_verified_at ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border-amber-500/20'} border uppercase tracking-widest">
                                        {user.email_verified_at ? 'Ativo' : 'Pendente'}
                                    </span>
                                </td>
                                <td class="px-8 py-5">
                                    <span class="text-[9px] font-bold text-gray-400 uppercase tracking-widest">{formatLastAccess(user.last_login_at)}</span>
                                </td>
                                <td class="px-8 py-5 text-right">
                                    <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button 
                                            on:click={() => toggleEditModal(user)}
                                            class="p-2 text-gray-400 hover:text-brand-orange transition-colors"
                                        >
                                            <Edit2 size={14} />
                                        </button>
                                        <button 
                                            on:click={() => handleDeleteUser(user.id)}
                                            class="p-2 text-gray-400 hover:text-red-500 transition-colors"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="5" class="px-8 py-12 text-center">
                                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Nenhum usuário encontrado.</span>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
    </div>
</div>

{#if showInviteModal}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" on:click={toggleInviteModal}></div>
        <div class="relative w-full max-w-md bg-white dark:bg-brand-black border border-gray-100 dark:border-white/10 rounded-[2rem] p-8 shadow-2xl">
            <button on:click={toggleInviteModal} class="absolute top-6 right-6 text-gray-400 hover:text-brand-orange transition-colors">
                <X size={20} />
            </button>
            <h3 class="text-2xl font-black text-black dark:text-white uppercase tracking-tighter mb-2">Convidar <span class="text-brand-orange">Membro</span></h3>
            <p class="text-[9px] text-gray-400 font-bold uppercase tracking-widest mb-8">Envie um convite de acesso para sua organização.</p>
            <div class="space-y-6">
                <div>
                    <label class="block text-[8px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2">E-mail do Usuário</label>
                    <div class="relative">
                        <Mail class="absolute left-4 top-1/2 -translate-y-1/2 text-brand-orange" size={14} />
                        <input bind:value={inviteEmail} type="email" placeholder="exemplo@email.com" class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 pl-12 pr-4 text-[10px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all" />
                    </div>
                </div>
                <div>
                    <label class="block text-[8px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2">Cargo / Permissão</label>
                    <select bind:value={inviteRole} class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[10px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all appearance-none">
                        <option value="admin">Administrador</option>
                        <option value="editor">Editor</option>
                        <option value="viewer">Visualizador</option>
                    </select>
                </div>
                <button on:click={handleInvite} disabled={isInviting || !inviteEmail} class="w-full bg-brand-orange hover:bg-brand-orange/90 disabled:opacity-50 text-black py-4 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-center gap-3">
                    {#if isInviting}
                        <RefreshCcw size={14} class="animate-spin" />
                    {:else}
                        <Check size={14} strokeWidth={3} />
                        Enviar Convite
                    {/if}
                </button>
            </div>
        </div>
    </div>
{/if}

{#if showEditModal}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" on:click={() => toggleEditModal()}></div>
        <div class="relative w-full max-w-md bg-white dark:bg-brand-black border border-gray-100 dark:border-white/10 rounded-[2rem] p-8 shadow-2xl">
            <button on:click={() => toggleEditModal()} class="absolute top-6 right-6 text-gray-400 hover:text-brand-orange transition-colors">
                <X size={20} />
            </button>
            <h3 class="text-2xl font-black text-black dark:text-white uppercase tracking-tighter mb-2">Editar <span class="text-brand-orange">Usuário</span></h3>
            <div class="space-y-6 mt-8">
                <div>
                    <label class="block text-[8px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2">Nome Completo</label>
                    <input bind:value={editingUser.name} type="text" class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[10px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all" />
                </div>
                <div>
                    <label class="block text-[8px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2">Cargo / Permissão</label>
                    <select bind:value={editingUser.role} class="w-full bg-gray-50 dark:bg-white/5 border-none rounded-xl py-4 px-6 text-[10px] font-black uppercase tracking-widest text-black dark:text-white focus:ring-1 focus:ring-brand-orange transition-all appearance-none">
                        <option value="admin">Administrador</option>
                        <option value="editor">Editor</option>
                        <option value="viewer">Visualizador</option>
                    </select>
                </div>
                <button on:click={handleUpdateUser} disabled={isInviting} class="w-full bg-brand-orange hover:bg-brand-orange/90 disabled:opacity-50 text-black py-4 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-center gap-3">
                    {#if isInviting}
                        <RefreshCcw size={14} class="animate-spin" />
                    {:else}
                        <Check size={14} strokeWidth={3} />
                        Salvar Alterações
                    {/if}
                </button>
            </div>
        </div>
    </div>
{/if}
