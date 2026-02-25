/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#ffffff",
          card: "#f8fafc",
          hover: "#f1f5f9",
        },
        accent: {
          green: "#10b981",
          blue: "#3b82f6",
          purple: "#8b5cf6",
          amber: "#f59e0b",
          red: "#ef4444",
          cyan: "#06b6d4",
        },
      },
    },
  },
  plugins: [],
};
