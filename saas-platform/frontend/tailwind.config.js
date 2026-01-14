/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          orange: '#ff7a00',
          black: '#000000',
          dark: '#0a0a0a',
          card: '#111111',
        }
      }
    },
  },
  plugins: [],
}
