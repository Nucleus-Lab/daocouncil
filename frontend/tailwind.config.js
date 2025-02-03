/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'court-brown': '#2c1810',
        'court-gold': '#d4af37',
      },
      backgroundImage: {
        'court': "url('./src/assets/bg.jpg')",
      },
    },
  },
  plugins: [],
}

