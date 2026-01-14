<script>
    import { Database, Settings2, Plus, Shield, Clock } from 'lucide-svelte';
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <div class="flex items-center justify-between mb-12">
        <div class="flex items-center gap-6">
            <div class="p-4 bg-brand-orange/10 rounded-[1.5rem] border border-brand-orange/20">
                <Database size={32} class="text-brand-orange" strokeWidth={2} />
            </div>
            <div>
                <h1 class="text-4xl font-black text-black dark:text-white tracking-tighter uppercase">Gestão <span class="text-brand-orange">Backup (PBS)</span></h1>
                <div class="flex items-center gap-3 mt-1">
                    <div class="w-2 h-2 bg-brand-orange rounded-full animate-pulse"></div>
                    <p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Administração de Proxmox Backup Server</p>
                </div>
            </div>
        </div>

        <div class="flex items-center gap-4">
            <button class="bg-brand-orange text-black px-8 py-3 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95 shadow-lg shadow-brand-orange/20">
                <Plus size={16} strokeWidth={3} />
                Novo Datastore
            </button>
        </div>
    </div>

    <div class="flex flex-col items-center justify-center h-[50vh] bg-white dark:bg-white/5 rounded-[3rem] border border-gray-100 dark:border-white/5 border-dashed p-12">
        <div class="w-20 h-20 bg-brand-orange/10 rounded-3xl flex items-center justify-center mb-6">
            <Clock size={40} class="text-brand-orange" />
        </div>
        <h2 class="text-2xl font-black text-black dark:text-white tracking-tighter uppercase mb-2">Módulo de Backup Server</h2>
        <p class="text-gray-400 text-xs font-bold uppercase tracking-widest text-center max-w-md">
            Gerencie Datastores, agende verificações e controle a retenção de backups (Pruning/Garbage Collection) do seu PBS.
        </p>
    </div>
</div>
