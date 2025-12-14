import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ScoringResult } from '@/types/scoring'

export const useScoringStore = defineStore('scoring', () => {
  // State
  const isRunning = ref<boolean>(false)
  const isError = ref<boolean>(false)
  const errorMessage = ref<string>('')
  const result = ref<ScoringResult | null>(null)
  const currentStep = ref<number>(-1)
  const isInitializingPyodide = ref<boolean>(false)

  // Actions
  function setRunning(running: boolean) {
    isRunning.value = running
  }

  function setResult(scoringResult: ScoringResult) {
    result.value = scoringResult
    isError.value = false
    errorMessage.value = ''
  }

  function setError(error: string) {
    isError.value = true
    errorMessage.value = error
    result.value = null
  }

  function setCurrentStep(step: number) {
    currentStep.value = step
  }

  function setInitializingPyodide(initializing: boolean) {
    isInitializingPyodide.value = initializing
  }

  function clear() {
    result.value = null
    isError.value = false
    errorMessage.value = ''
    currentStep.value = -1
  }

  function nextStep() {
    if (result.value && currentStep.value < result.value.executionSteps.length - 1) {
      currentStep.value++
    }
  }

  function previousStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  return {
    // State
    isRunning,
    isError,
    errorMessage,
    result,
    currentStep,
    isInitializingPyodide,
    // Actions
    setRunning,
    setResult,
    setError,
    setCurrentStep,
    setInitializingPyodide,
    clear,
    nextStep,
    previousStep,
  }
})
