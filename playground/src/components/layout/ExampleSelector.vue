<template>
  <div class="example-selector">
    <label for="example-select">Example:</label>
    <select
      id="example-select"
      :value="currentExample"
      @change="(e) => $emit('update:currentExample', (e.target as HTMLSelectElement).value)"
    >
      <option value="" disabled>Select an example...</option>
      <option v-for="ex in examples" :key="ex.id" :value="ex.id">
        {{ ex.name }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentExample: string
  examples: Array<{ id: string; name: string }>
}

interface Emits {
  (e: 'update:currentExample', id: string): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.example-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

label {
  color: #cccccc;
  font-size: 13px;
  white-space: nowrap;
}

select {
  padding: 6px 8px;
  border: 1px solid #3e3e42;
  background: #3c3c3c;
  color: #cccccc;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  min-width: 200px;
}

select:hover {
  border-color: #007acc;
}

select:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
}

option {
  background: #3c3c3c;
  color: #cccccc;
}
</style>
