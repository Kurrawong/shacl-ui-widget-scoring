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
  gap: 10px;
}

label {
  color: #cccccc;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

select {
  padding: 8px 12px;
  border: 1px solid #3e3e42;
  background: #3c3c3c;
  color: #ffffff;
  border-radius: 5px;
  font-size: 13px;
  cursor: pointer;
  min-width: 220px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
}

select:hover {
  border-color: #007acc;
  background: #454545;
}

select:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.25);
  background: #454545;
}

option {
  background: #3c3c3c;
  color: #ffffff;
  padding: 8px;
}
</style>
