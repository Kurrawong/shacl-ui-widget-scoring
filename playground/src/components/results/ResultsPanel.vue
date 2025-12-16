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
  padding: 20px;
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
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.results-loading p {
  color: #9cdcfe;
  font-size: 14px;
  margin-top: 8px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #3e3e42;
  border-top-color: #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.results-error {
  color: #f48771;
  background: rgba(244, 135, 113, 0.05);
  border: 1px solid rgba(244, 135, 113, 0.2);
  border-radius: 8px;
  padding: 32px;
}

.error-icon {
  font-size: 56px;
  margin-bottom: 20px;
  filter: drop-shadow(0 2px 4px rgba(244, 135, 113, 0.3));
}

.results-error h3 {
  margin: 0 0 16px 0;
  color: #f48771;
  font-size: 18px;
  font-weight: 600;
}

.results-error pre {
  background: #252526;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  text-align: left;
  margin: 0 0 20px 0;
  font-size: 12px;
  border: 1px solid #3e3e42;
  max-width: 600px;
  font-family: 'Monaco', 'Menlo', monospace;
}

.btn-close {
  padding: 10px 20px;
  background: #3e3e42;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #4e4e52;
  transform: translateY(-1px);
}

.results-empty {
  color: #858585;
}

.results-empty p {
  font-size: 14px;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 28px;
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.steps-section {
  margin-top: 8px;
  padding-top: 28px;
  border-top: 2px solid #3e3e42;
}

.steps-section h3 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.steps-section h3::before {
  content: '📝';
  font-size: 18px;
}
</style>
