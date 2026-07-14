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
        background: "#020817",
        sidebar: "#07111f",
        surface: "#0b1220",
        elevated: "#111827",
        primary: "#22D3EE",
        blue: "#0EA5E9",
        secondary: "#8B5CF6",
        success: "#2ee6a6",
        warning: "#ff9f43",
        danger: "#ff5f6d",
        text: "#f5f7fb",
        muted: "#95a3b8",
        border: "rgba(255,255,255,0.08)"
      },
      boxShadow: {
        panel: "0 24px 70px rgba(2,8,23,0.42), inset 0 1px 0 rgba(255,255,255,0.06)",
        glow: "0 0 40px rgba(34,211,238,0.18)"
      },
      borderRadius: {
        panel: "24px"
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" }
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" }
        }
      },
      animation: {
        float: "float 4s ease-in-out infinite",
        shimmer: "shimmer 2.4s ease-in-out infinite"
      }
    },
  },
  plugins: [],
};

export default config;
