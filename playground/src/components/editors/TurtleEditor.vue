<template>
  <MonacoEditor
    :model-value="modelValue"
    language="turtle"
    :read-only="readOnly"
    :height="height"
    :theme="theme"
    @update:model-value="(value) => $emit('update:modelValue', value)"
  />
</template>

<script setup lang="ts">
import MonacoEditor from './MonacoEditor.vue'

interface Props {
  modelValue: string
  readOnly?: boolean
  height?: string
  theme?: 'light' | 'dark'
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

withDefaults(defineProps<Props>(), {
  readOnly: false,
  height: '400px',
  theme: 'dark',
})

defineEmits<Emits>()
</script>
