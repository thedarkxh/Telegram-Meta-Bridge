/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBg: '#090d16',
        darkCard: 'rgba(17, 24, 39, 0.65)',
        darkBorder: 'rgba(255, 255, 255, 0.08)',
        accentPrimary: '#6366f1',   // Indigo
        accentSecondary: '#a855f7', // Purple
        success: '#10b981',         // Emerald (mastery)
        warning: '#f59e0b',         // Amber (average progress)
        danger: '#ef4444',          // Red
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-inset': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.05)',
      },
    },
  },
  plugins: [],
}
