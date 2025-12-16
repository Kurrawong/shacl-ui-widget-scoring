<template>
  <div class="toolbar">
    <div class="toolbar-left">
      <ExampleSelector
        :current-example="currentExample"
        :examples="examples"
        @update:current-example="(id) => $emit('update:currentExample', id)"
      />
      <button
        class="btn btn-secondary"
        :disabled="isRunning"
        @click="$emit('clearInputs')"
      >
        Clear Inputs
      </button>
    </div>

    <div class="toolbar-right">
      <button
        class="btn btn-primary"
        :disabled="isRunning"
        @click="$emit('run')"
      >
        <span v-if="!isRunning">▶ Run Scoring</span>
        <span v-else>⏸ Running...</span>
      </button>

      <button
        class="btn btn-secondary"
        :disabled="isRunning"
        @click="$emit('clear')"
      >
        Clear Results
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import ExampleSelector from './ExampleSelector.vue'

interface Props {
  currentExample: string
  examples: Array<{ id: string; name: string }>
  isRunning?: boolean
}

interface Emits {
  (e: 'update:currentExample', id: string): void
  (e: 'run'): void
  (e: 'clear'): void
  (e: 'clearInputs'): void
}

withDefaults(defineProps<Props>(), {
  isRunning: false,
})

defineEmits<Emits>()
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn {
  padding: 9px 16px;
  border: none;
  border-radius: 5px;
  background: #007acc;
  color: #ffffff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.btn:hover:not(:disabled) {
  background: #1177bb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #3e3e42;
  color: #cccccc;
}

.btn-secondary:hover:not(:disabled) {
  background: #4e4e52;
}

.btn-primary {
  font-weight: 600;
  background: linear-gradient(135deg, #007acc 0%, #005a9e 100%);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1177bb 0%, #006bb0 100%);
}

.btn-primary:focus-visible {
  outline: 2px solid #007acc;
  outline-offset: 2px;
}
</style>
