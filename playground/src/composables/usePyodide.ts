import { ref } from 'vue'
import type { ScoringRequest, ScoringResult } from '@/types/scoring'

// Module-level storage (singleton pattern)
let worker: Worker | null = null
const isInitialized = ref(false)
const isInitializing = ref(false)
const error = ref<string | null>(null)

// Initialize worker
async function initWorker(): Promise<void> {
  if (isInitialized.value || isInitializing.value) return

  isInitializing.value = true
  error.value = null

  try {
    // Import worker as a module
    const PyodideWorker = await import('@/workers/pyodide.worker.ts?worker')
    worker = new PyodideWorker.default()

    // Wait for initialization
    await new Promise<void>((resolve, reject) => {
      const handler = (event: MessageEvent) => {
        if (event.data.type === 'initialized') {
          isInitialized.value = true
          worker?.removeEventListener('message', handler)
          resolve()
        } else if (event.data.type === 'error') {
          error.value = event.data.error
          worker?.removeEventListener('message', handler)
          reject(new Error(event.data.error))
        }
      }

      worker?.addEventListener('message', handler)

      // Send init message with BASE_URL
      worker?.postMessage({ type: 'init', baseURL: import.meta.env.BASE_URL })

      // Timeout after 30 seconds
      setTimeout(() => {
        worker?.removeEventListener('message', handler)
        reject(new Error('Pyodide initialization timeout'))
      }, 30000)
    })
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err)
    if (errorMsg.includes('timeout')) {
      error.value = 'Pyodide initialization timed out. Please check your internet connection and try again.'
    } else if (errorMsg.includes('Failed to fetch')) {
      error.value = 'Failed to download Pyodide. Please check your internet connection.'
    } else {
      error.value = `Failed to initialize Pyodide: ${errorMsg}`
    }
    isInitialized.value = false
    throw new Error(error.value)
  } finally {
    isInitializing.value = false
  }
}

// Score widgets
async function scoreWidgets(request: ScoringRequest): Promise<ScoringResult> {
  if (!worker || !isInitialized.value) {
    await initWorker()
  }

  return new Promise<ScoringResult>((resolve, reject) => {
    if (!worker) {
      reject(new Error('Worker not initialized'))
      return
    }

    const handler = (event: MessageEvent) => {
      if (event.data.type === 'result') {
        worker?.removeEventListener('message', handler)
        resolve(event.data.payload as ScoringResult)
      } else if (event.data.type === 'error') {
        worker?.removeEventListener('message', handler)
        error.value = event.data.error
        reject(new Error(event.data.error))
      }
    }

    worker.addEventListener('message', handler)
    worker.postMessage({ type: 'score', payload: request })

    // Timeout after 60 seconds
    setTimeout(() => {
      worker?.removeEventListener('message', handler)
      reject(new Error('Scoring timeout'))
    }, 60000)
  })
}

// Cleanup
function cleanup() {
  if (worker) {
    worker.terminate()
    worker = null
    isInitialized.value = false
  }
}

export function usePyodide() {
  // Return direct references to module-level state
  return {
    isInitialized,
    isInitializing,
    error,
    initWorker,
    scoreWidgets,
    cleanup,
  }
}
