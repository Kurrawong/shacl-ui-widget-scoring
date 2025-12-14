<template>
  <div class="step-visualization">
    <div v-if="steps.length === 0" class="no-steps">
      <p>No execution steps available</p>
    </div>

    <div v-else class="steps-container">
      <div class="steps-list">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step-item"
          :class="{ active: currentStep === index }"
          @click="$emit('select-step', index)"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <p class="step-widget">{{ getWidgetName(step.widget) }}</p>
            <p class="step-score">Score: {{ step.score }}</p>
          </div>
        </div>
      </div>

      <div v-if="currentStep >= 0 && steps[currentStep]" class="step-details">
        <h4>Step {{ currentStep + 1 }} Details</h4>
        <div class="details-content">
          <p><strong>Widget:</strong> {{ getWidgetName(steps[currentStep].widget) }}</p>
          <p><strong>Score:</strong> {{ steps[currentStep].score }}</p>
          <p><strong>Explanation:</strong> {{ steps[currentStep].explanation }}</p>

          <div v-if="steps[currentStep].dataGraphValidation.length > 0" class="validation-section">
            <h5>Data Graph Validation</h5>
            <div
              v-for="(validation, idx) in steps[currentStep].dataGraphValidation"
              :key="`dg-${idx}`"
              class="validation-item"
              :class="{ valid: validation.valid }"
            >
              <span class="validation-icon">{{ validation.valid ? '✓' : '✗' }}</span>
              <span class="validation-text">{{ validation.shape }}: {{ validation.details }}</span>
            </div>
          </div>

          <div v-if="steps[currentStep].shapesGraphValidation.length > 0" class="validation-section">
            <h5>Shapes Graph Validation</h5>
            <div
              v-for="(validation, idx) in steps[currentStep].shapesGraphValidation"
              :key="`sg-${idx}`"
              class="validation-item"
              :class="{ valid: validation.valid }"
            >
              <span class="validation-icon">{{ validation.valid ? '✓' : '✗' }}</span>
              <span class="validation-text">{{ validation.shape }}: {{ validation.details }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExecutionStep } from '@/types/scoring'

interface Props {
  steps: ExecutionStep[]
  currentStep?: number
}

interface Emits {
  (e: 'select-step', index: number): void
}

withDefaults(defineProps<Props>(), {
  currentStep: -1,
})

defineEmits<Emits>()

function getWidgetName(widget: string): string {
  return widget.split('/').pop() || widget
}
</script>

<style scoped>
.step-visualization {
  width: 100%;
}

.no-steps {
  text-align: center;
  padding: 24px;
  color: #858585;
}

.steps-container {
  display: flex;
  gap: 16px;
}

.steps-list {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
  background: #252526;
  padding: 12px;
  border-radius: 4px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #2d2d30;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.step-item:hover {
  background: #3e3e42;
}

.step-item.active {
  background: #007acc;
  border-left-color: #4ec9b0;
}

.step-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3e3e42;
  border-radius: 50%;
  color: #cccccc;
  font-weight: 600;
  flex-shrink: 0;
  font-size: 12px;
}

.step-item.active .step-number {
  background: #ffffff;
  color: #007acc;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-widget {
  margin: 0;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-score {
  margin: 2px 0 0 0;
  color: #858585;
  font-size: 11px;
}

.step-details {
  flex: 1;
  background: #252526;
  padding: 16px;
  border-radius: 4px;
  overflow-y: auto;
  max-height: 600px;
}

.step-details h4 {
  margin: 0 0 12px 0;
  color: #ffffff;
  font-size: 13px;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.details-content p {
  margin: 0;
  color: #cccccc;
  font-size: 12px;
  line-height: 1.5;
}

.details-content strong {
  color: #ffffff;
}

.validation-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #3e3e42;
}

.validation-section h5 {
  margin: 0 0 8px 0;
  color: #cccccc;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.validation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: #2d2d30;
  border-radius: 2px;
  border-left: 2px solid #f48771;
  font-size: 11px;
}

.validation-item.valid {
  border-left-color: #4ec9b0;
}

.validation-icon {
  flex-shrink: 0;
  font-weight: 600;
  color: #f48771;
  width: 20px;
}

.validation-item.valid .validation-icon {
  color: #4ec9b0;
}

.validation-text {
  color: #cccccc;
  line-height: 1.4;
  word-break: break-word;
}
</style>
