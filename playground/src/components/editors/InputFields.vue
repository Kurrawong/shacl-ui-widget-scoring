<template>
  <div class="input-fields">
    <div class="fields-header">
      <h3 class="fields-title">Input Parameters</h3>
      <p class="fields-description">Configure the focus node and its properties</p>
    </div>

    <div class="fields-grid">
      <div class="field-group">
        <label class="field-label" for="focus-node">
          Focus Node
          <span class="field-required">*</span>
        </label>
        <div
          class="field-input field-input-clickable"
          @click="showModal = true"
          role="button"
          tabindex="0"
          @keydown.enter="showModal = true"
          @keydown.space.prevent="showModal = true"
        >
          {{ displayValue }}
        </div>
        <p class="field-hint">Click to edit the RDF value node (IRI or literal)</p>
      </div>

      <div class="field-group">
        <label class="field-label" for="constraint-shape">
          Constraint Shape
          <span class="field-optional">(optional)</span>
        </label>
        <input
          id="constraint-shape"
          type="text"
          class="field-input"
          :value="constraintShape ?? ''"
          @input="
            $emit(
              'update:constraintShape',
              ($event.target as HTMLInputElement).value || null
            )
          "
          placeholder="e.g., ex:PersonShape"
        />
        <p class="field-hint">Optional SHACL shape URI to validate the focus node against</p>
      </div>
    </div>

    <FocusNodeModal
      :is-open="showModal"
      :initial-value="focusNode"
      @close="showModal = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FocusNode } from '@/types/focusNode'
import { focusNodeToN3String } from '@/lib/focusNode'
import FocusNodeModal from './FocusNodeModal.vue'

interface Props {
  focusNode: FocusNode
  constraintShape: string | null
}

interface Emits {
  (e: 'update:focusNode', value: FocusNode): void
  (e: 'update:constraintShape', value: string | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showModal = ref(false)

const displayValue = computed(() => focusNodeToN3String(props.focusNode))

const handleSave = (value: FocusNode) => {
  emit('update:focusNode', value)
  showModal.value = false
}
</script>

<style scoped>
.input-fields {
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  padding: 16px 20px;
}

.fields-header {
  margin-bottom: 16px;
}

.fields-title {
  margin: 0;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.fields-description {
  margin: 4px 0 0 0;
  color: #858585;
  font-size: 12px;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #cccccc;
}

.field-required {
  color: #f48771;
  font-size: 12px;
}

.field-optional {
  color: #858585;
  font-size: 11px;
  font-weight: 400;
}

.field-input {
  width: 100%;
  padding: 8px 10px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #ffffff;
  font-size: 13px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #007acc;
}

.field-input::placeholder {
  color: #858585;
}

.field-input-clickable {
  cursor: pointer;
  user-select: none;
}

.field-input-clickable:hover {
  border-color: #007acc;
  background: #252526;
}

.field-input-clickable:focus {
  outline: 2px solid #007acc;
  outline-offset: 2px;
}

.field-hint {
  margin: 0;
  font-size: 11px;
  color: #858585;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
