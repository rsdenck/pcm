import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const defaultValue = 'dark';
const initialValue = browser ? window.localStorage.getItem('theme') ?? defaultValue : defaultValue;

export const theme = writable(initialValue);

if (browser) {
    theme.subscribe((value) => {
        window.localStorage.setItem('theme', value);
        if (value === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
        }
    });
}
