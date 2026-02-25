/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0f1117",
          card: "#1a1d27",
          hover: "#242836",
        },
        accent: {
          green: "#22c55e",
          blue: "#3b82f6",
          purple: "#a855f7",
          amber: "#f59e0b",
          red: "#ef4444",
          cyan: "#06b6d4",
        },
      },
    },
  },
  plugins: [],
};
