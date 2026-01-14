<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { Cpu } from 'lucide-svelte';

    onMount(() => {
        setTimeout(() => {
            goto('/dashboard');
        }, 1000);
    });
</script>

<div class="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
    <div class="animate-pulse mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/40">
            <Cpu class="text-white" size={48} />
        </div>
    </div>
    
    <h1 class="text-5xl font-black text-white tracking-tighter mb-2">
        Proxmon
    </h1>
    <p class="text-gray-500 font-medium tracking-wide uppercase text-sm">
        Iniciando Monitoramento...
    </p>

    <div class="mt-12 w-48 h-1 bg-gray-800 rounded-full overflow-hidden">
        <div class="h-full bg-blue-500 animate-[loading_1.5s_ease-in-out_infinite]"></div>
    </div>
</div>

<style>
    @keyframes loading {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
</style>
