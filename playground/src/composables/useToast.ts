import { toast } from 'vue-sonner'

export function useToast() {
  const success = (message: string, duration?: number) => {
    return toast.success(message, { duration })
  }

  const error = (message: string, duration?: number) => {
    return toast.error(message, { duration })
  }

  const info = (message: string, duration?: number) => {
    return toast.info(message, { duration })
  }

  return {
    success,
    error,
    info,
  }
}
