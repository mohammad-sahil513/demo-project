/**
 * Output downloads — opens a new tab pointing at the streaming download
 * endpoint instead of fetching via axios. The backend serves the file
 * with a `Content-Disposition: attachment` header, so the browser
 * handles the download natively.
 *
 * `downloadUrl` resolves the base URL once, supporting both relative
 * (`/api`) and absolute (`https://...`) configurations.
 */
import { baseURL } from './client'

function downloadUrl(path: string): string {
  if (baseURL.startsWith('http')) {
    return `${baseURL.replace(/\/$/, '')}${path}`
  }
  return `${window.location.origin}${baseURL.replace(/\/$/, '')}${path}`
}

export const outputApi = {
  downloadByOutputId: (outputId: string) => {
    window.open(downloadUrl(`/outputs/${outputId}/download`), '_blank')
  },
}
