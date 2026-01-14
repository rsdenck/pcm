<script>
    import { RefreshCw, Settings2, Plus, Repeat, Share2 } from 'lucide-svelte';
</script>

<div class="p-4 md:p-8 w-full transition-all">
    <div class="flex items-center justify-between mb-12">
        <div class="flex items-center gap-6">
            <div class="p-4 bg-brand-orange/10 rounded-[1.5rem] border border-brand-orange/20">
                <RefreshCw size={32} class="text-brand-orange" strokeWidth={2} />
            </div>
            <div>
                <h1 class="text-4xl font-black text-black dark:text-white tracking-tighter uppercase">Gestão de <span class="text-brand-orange">Replicação</span></h1>
                <div class="flex items-center gap-3 mt-1">
                    <div class="w-2 h-2 bg-brand-orange rounded-full animate-pulse"></div>
                    <p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Alta Disponibilidade e Sincronismo</p>
                </div>
            </div>
        </div>

        <div class="flex items-center gap-4">
            <button class="bg-brand-orange text-black px-8 py-3 rounded-xl font-black text-[10px] transition-all flex items-center gap-3 uppercase tracking-widest active:scale-95 shadow-lg shadow-brand-orange/20">
                <Plus size={16} strokeWidth={3} />
                Nova Replicação
            </button>
        </div>
    </div>

    <div class="flex flex-col items-center justify-center h-[50vh] bg-white dark:bg-white/5 rounded-[3rem] border border-gray-100 dark:border-white/5 border-dashed p-12">
        <div class="w-20 h-20 bg-brand-orange/10 rounded-3xl flex items-center justify-center mb-6">
            <Repeat size={40} class="text-brand-orange" />
        </div>
        <h2 class="text-2xl font-black text-black dark:text-white tracking-tighter uppercase mb-2">Módulo de Replicação</h2>
        <p class="text-gray-400 text-xs font-bold uppercase tracking-widest text-center max-w-md">
            Configure jobs de replicação entre Nodes do Cluster para garantir a redundância dos seus dados.
        </p>
    </div>
</div>
