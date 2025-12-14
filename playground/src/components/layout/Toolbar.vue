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
  padding: 12px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background: #0e639c;
  color: #ffffff;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:hover:not(:disabled) {
  background: #1177bb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6f42c1;
}

.btn-secondary:hover:not(:disabled) {
  background: #7d4fc4;
}

.btn-primary {
  font-weight: 600;
}
</style>
