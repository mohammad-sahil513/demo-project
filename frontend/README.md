# AI SDLC — Frontend

React + TypeScript + Vite + Tailwind UI for the document generation workflow. It talks to the **FastAPI** backend using the real `/api` contract (`success_response` envelopes are unwrapped in the Axios client).

## Stack

- React 18, Vite 5, TypeScript
- Tailwind CSS (black / `#FFD400` theme)
- Zustand for client state
- Axios (`baseURL` from `VITE_API_BASE`, default `/api`)
- react-markdown + remark-gfm (section preview)
- docx-preview (template DOCX popup preview)
- lucide-react

## Setup

```bash
npm install
npm run dev
