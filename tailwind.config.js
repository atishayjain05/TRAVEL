/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        serif: ['Fraunces', 'serif'],
        mono: ['DM Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
