/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#133a4d",
          light: "#1a4a61",
          lighter: "#215a76",
        },
        accent: {
          DEFAULT: "#2dd4bf",
          dark: "#0d9488",
        },
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(45, 212, 191, 0.4)",
      },
    },
  },
  plugins: [],
};
