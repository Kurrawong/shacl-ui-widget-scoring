import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", ...defaultTheme.fontFamily.sans],
        mono: ["Monaco", "Menlo", "Consolas", "Courier New", ...defaultTheme.fontFamily.mono],
      },
      colors: {
        // VS Code inspired color system
        vscode: {
          bg: {
            primary: '#1e1e1e',
            secondary: '#252526',
            tertiary: '#2d2d30',
            elevated: '#3e3e42',
          },
          text: {
            primary: '#ffffff',
            secondary: '#cccccc',
            muted: '#858585',
          },
          accent: {
            primary: '#007acc',
            'primary-hover': '#1177bb',
            success: '#4ec9b0',
            warning: '#dcdcaa',
            error: '#f48771',
            info: '#9cdcfe',
          },
          border: {
            default: '#3e3e42',
            focus: '#007acc',
          }
        }
      },
      spacing: {
        '18': '4.5rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 122, 204, 0.3)',
        'glow-sm': '0 0 10px rgba(0, 122, 204, 0.2)',
        'card': '0 2px 8px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 4px 16px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
