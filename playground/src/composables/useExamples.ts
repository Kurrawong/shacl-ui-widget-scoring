import { ref, computed } from 'vue'
import type { ExamplesData, Example, SharedGraphs } from '@/types/examples'

export function useExamples() {
  const examples = ref<Example[]>([])
  const sharedGraphs = ref<SharedGraphs | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Load examples from JSON
  async function loadExamples(): Promise<void> {
    if (isLoading.value || examples.value.length > 0) return

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${import.meta.env.BASE_URL}examples.json`)
      if (!response.ok) {
        throw new Error(`Failed to load examples: ${response.statusText}`)
      }

      const data: ExamplesData = await response.json()
      examples.value = data.examples
      sharedGraphs.value = data.sharedGraphs
    } catch (err) {
      error.value = `Failed to load examples: ${err}`
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Get example by ID
  function getExample(id: string): Example | undefined {
    return examples.value.find((ex) => ex.id === id)
  }

  // Get all examples
  const allExamples = computed(() => examples.value)

  // Get example IDs
  const exampleIds = computed(() => examples.value.map((ex) => ex.id))

  return {
    examples: allExamples,
    exampleIds,
    sharedGraphs,
    isLoading,
    error,
    loadExamples,
    getExample,
  }
}
