/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        sidebar: '#1a4d2e',
        sidebarHover: '#2d6a4f',
        accent: '#f4a261',
        accentDark: '#e76f51',
        content: '#f8f9fa',
      },
    },
  },
  plugins: [],
}
