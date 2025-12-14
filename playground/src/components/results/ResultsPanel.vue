<template>
  <div class="results-panel">
    <!-- Loading State -->
    <div v-if="isRunning" class="results-loading">
      <div class="spinner"></div>
      <p v-if="isInitializing">
        Initializing Pyodide runtime (first time only, ~30s)...
      </p>
      <p v-else>Running widget scoring...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="isError" class="results-error">
      <div class="error-icon">⚠️</div>
      <h3>Scoring Error</h3>
      <pre>{{ errorMessage }}</pre>
      <button class="btn-close" @click="$emit('clear')">Dismiss</button>
    </div>

    <!-- No Results -->
    <div v-else-if="!result" class="results-empty">
      <p>No results yet. Run the scoring to see widget recommendations.</p>
    </div>

    <!-- Results Display -->
    <div v-else class="results-content">
      <!-- Default Widget -->
      <DefaultWidget v-if="result.defaultWidget" :widget="result.defaultWidget" :score="result.defaultScore" :widget-scores="result.widgetScores" />

      <!-- Score List -->
      <ScoreList :widget-scores="result.widgetScores" />

      <!-- Step Visualization -->
      <div v-if="result.executionSteps && result.executionSteps.length > 0" class="steps-section">
        <h3>Execution Steps</h3>
        <StepVisualization :steps="result.executionSteps" :current-step="currentStep" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ScoringResult } from '@/types/scoring'
import DefaultWidget from './DefaultWidget.vue'
import ScoreList from './ScoreList.vue'
import StepVisualization from './StepVisualization.vue'

interface Props {
  result: ScoringResult | null
  isRunning?: boolean
  isError?: boolean
  errorMessage?: string
  currentStep?: number
  isInitializing?: boolean
}

interface Emits {
  (e: 'clear'): void
}

withDefaults(defineProps<Props>(), {
  isRunning: false,
  isError: false,
  errorMessage: '',
  currentStep: -1,
  isInitializing: false,
})

defineEmits<Emits>()
</script>

<style scoped>
.results-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: #1e1e1e;
  color: #cccccc;
  padding: 16px;
  overflow-y: auto;
}

.results-loading,
.results-error,
.results-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #3e3e42;
  border-top-color: #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.results-error {
  color: #f48771;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.results-error h3 {
  margin: 0 0 12px 0;
  color: #f48771;
}

.results-error pre {
  background: #252526;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  text-align: left;
  margin: 0 0 16px 0;
  font-size: 12px;
}

.btn-close {
  padding: 8px 16px;
  background: #6f42c1;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-close:hover {
  background: #7d4fc4;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.steps-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #3e3e42;
}

.steps-section h3 {
  margin: 0 0 12px 0;
  color: #ffffff;
  font-size: 14px;
}
</style>
