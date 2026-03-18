import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        light: {
          primary: '#2563eb',
          secondary: '#0ea5e9',
          accent: '#16a34a',
          neutral: '#1f2937',
          'base-100': '#f8fafc',
          'base-200': '#f1f5f9',
          'base-300': '#e2e8f0',
          'base-content': '#0f172a',
          info: '#0ea5e9',
          success: '#16a34a',
          warning: '#f59e0b',
          error: '#dc2626',
        },
      },
      {
        dark: {
          primary: '#3b82f6',
          secondary: '#0ea5e9',
          accent: '#22c55e',
          neutral: '#111827',
          'base-100': '#0f172a',
          'base-200': '#111827',
          'base-300': '#1f2937',
          'base-content': '#e5e7eb',
          info: '#38bdf8',
          success: '#4ade80',
          warning: '#fbbf24',
          error: '#f87171',
        },
      },
    ],
  },
  theme: {
    extend: {
      boxShadow: {
        card: '0 8px 24px rgba(15, 23, 42, 0.08)',
      },
    },
  },
}
