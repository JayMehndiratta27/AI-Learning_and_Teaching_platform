/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  // Use `.dark` class (we toggle it on `html`) instead of `prefers-color-scheme`.
  darkMode: 'class',
  // Preflight resets borders globally and breaks Angular Material MDC outlined fields (notch / “split” line).
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        lf: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
          dark: '#0f172a',
          surface: 'rgba(255,255,255,0.06)',
        },
      },
      fontFamily: {
        display: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
