import { ref } from 'vue'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
  duration: number
}

const toasts = ref<Toast[]>([])

export function useToast() {
  const show = (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const toast: Toast = { id, message, type, duration }

    toasts.value.push(toast)

    setTimeout(() => {
      remove(id)
    }, duration)

    return id
  }

  const remove = (id: string) => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  const success = (message: string, duration?: number) => show(message, 'success', duration)
  const error = (message: string, duration?: number) => show(message, 'error', duration)
  const info = (message: string, duration?: number) => show(message, 'info', duration)

  return {
    toasts,
    show,
    remove,
    success,
    error,
    info,
  }
}
