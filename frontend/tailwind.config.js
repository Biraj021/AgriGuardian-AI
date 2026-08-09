/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#10B981', // Emerald 500
          600: '#059669', // Emerald 600
        },
        secondary: {
          500: '#3B82F6', // Blue 500
        },
        background: '#F3F4F6', // Gray 100
        surface: '#FFFFFF',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
