import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
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
    }
  }
}
