/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        /** EY-inspired semantic tokens (tune hexes against official brand when available). */
        ey: {
          primary: '#FFE600',
          primaryHover: '#E6CF00',
          ink: '#1A1A1A',
          'ink-strong': '#000000',
          muted: '#6B6B6B',
          surface: '#F7F7F7',
          border: '#E5E5E5',
          nav: '#000000',
          white: '#FFFFFF',
          /** Page well behind cards (viewer, previews). */
          canvas: '#f0f0f0',
        },
        /** Legacy aliases — map to same palette for gradual migration. */
        brand: {
          black: '#000000',
          yellow: '#FFE600',
          gray: '#F7F7F7',
          border: '#E5E5E5',
          text: '#1A1A1A',
          muted: '#6B6B6B',
        },
      },
      fontFamily: {
        display: ['Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-bar': 'pulseBar 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        pulseBar: { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.6 } },
      },
    },
  },
  plugins: [],
}
