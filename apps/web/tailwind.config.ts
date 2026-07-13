import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#06111f",
        sidebar: "#071523",
        surface: "#0d1b2a",
        elevated: "#12243a",
        primary: "#18d7df",
        blue: "#2f80ff",
        secondary: "#7c5cff",
        success: "#2ee6a6",
        warning: "#ff9f43",
        danger: "#ff5f6d",
        text: "#f5f7fb",
        muted: "#95a3b8",
        border: "rgba(255,255,255,0.08)"
      },
      boxShadow: {
        panel: "0 20px 40px rgba(0,0,0,0.2)"
      },
      borderRadius: {
        panel: "18px"
      }
    },
  },
  plugins: [],
};

export default config;
