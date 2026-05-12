/// <reference types="vite/client" />

/**
 * Vite environment variables exposed to the client bundle.
 *
 * Only variables prefixed with `VITE_` are inlined at build time. Add
 * new fields here whenever a `VITE_*` variable is added to `.env` so
 * `import.meta.env` stays type-safe across the frontend.
 *
 * - `VITE_API_BASE` — base URL for the API client. Defaults to `/api`
 *   when unset (see `api/client.ts`), which works with the Vite proxy
 *   in dev and the same-origin deployment in production.
 */
interface ImportMetaEnv {
  readonly VITE_API_BASE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
