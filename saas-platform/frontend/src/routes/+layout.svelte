<script lang="ts">
  import "../app.css";
  import Sidebar from "$lib/components/Sidebar.svelte";
  import { page } from "$app/stores";
  import { theme } from "$lib/stores/theme";
</script>

<div class="flex h-screen bg-white dark:bg-brand-black text-gray-900 dark:text-gray-100 font-sans selection:bg-brand-orange/30 overflow-hidden">
    <Sidebar activePath={$page.url.pathname} />
    <main class="flex-1 overflow-y-auto custom-scrollbar bg-gray-50 dark:bg-brand-black">
        <div class="w-full min-h-screen">
            <slot />
        </div>
    </main>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        background-color: white;
        color: black;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    :global(body.dark) {
        background-color: #000000;
        color: white;
    }

    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #e5e7eb;
        border-radius: 10px;
    }

    :global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #1a1a1a;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: #ff7a00;
    }
</style>
