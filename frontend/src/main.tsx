/**
 * Frontend entry point — mounts the React tree into the root element.
 *
 * Loaded by `index.html` via the Vite dev/build pipeline. `StrictMode`
 * is enabled so React surfaces unsafe lifecycles and double-invokes
 * effects in development.
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
