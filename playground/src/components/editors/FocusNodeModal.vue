<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div class="modal-container">
          <div class="modal-header">
            <h2 class="modal-title">Edit Focus Node</h2>
            <button class="modal-close" @click="close" aria-label="Close">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Node Type</label>
              <select v-model="nodeType" class="form-select">
                <option value="IRI">IRI</option>
                <option value="LITERAL">Literal</option>
              </select>
            </div>

            <div v-if="nodeType === 'IRI'" class="form-group">
              <label class="form-label">
                IRI Value
                <span class="field-required">*</span>
              </label>
              <input
                v-model="iriValue"
                type="text"
                class="form-input"
                placeholder="e.g., http://example.org/resource"
                @keydown.enter="handleSave"
                ref="iriInput"
              />
            </div>

            <div v-if="nodeType === 'LITERAL'" class="literal-fields">
              <div class="form-group">
                <label class="form-label">
                  Value
                  <span class="field-required">*</span>
                </label>
                <input
                  v-model="literalValue"
                  type="text"
                  class="form-input"
                  placeholder="e.g., Hello World"
                  @keydown.enter="handleSave"
                  ref="literalInput"
                />
              </div>

              <div class="form-group">
                <label class="form-label">
                  Datatype
                  <span class="field-optional">(optional)</span>
                </label>
                <input
                  v-model="datatype"
                  type="text"
                  class="form-input"
                  :disabled="!!language"
                  placeholder="e.g., http://www.w3.org/2001/XMLSchema#string"
                />
                <p v-if="language" class="field-hint">
                  Datatype is automatically set to rdf:langString when language tag is present
                </p>
              </div>

              <div class="form-group">
                <label class="form-label">
                  Language Tag
                  <span class="field-optional">(optional)</span>
                </label>
                <input
                  v-model="language"
                  type="text"
                  class="form-input"
                  placeholder="e.g., en, fr, de"
                />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="close">Cancel</button>
            <button class="btn btn-primary" @click="handleSave" :disabled="!canSave">
              Save
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { FocusNode } from '@/types/focusNode'
import { isFocusNodeIRI } from '@/types/focusNode'

interface Props {
  isOpen: boolean
  initialValue: FocusNode
}

interface Emits {
  (e: 'close'): void
  (e: 'save', value: FocusNode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const nodeType = ref<'IRI' | 'LITERAL'>('IRI')
const iriValue = ref('')
const literalValue = ref('')
const datatype = ref('')
const language = ref('')

const iriInput = ref<HTMLInputElement | null>(null)
const literalInput = ref<HTMLInputElement | null>(null)

const canSave = computed(() => {
  if (nodeType.value === 'IRI') {
    return iriValue.value.trim().length > 0
  }
  return literalValue.value.trim().length > 0
})

const handleSave = () => {
  if (!canSave.value) return

  let result: FocusNode

  if (nodeType.value === 'IRI') {
    result = {
      type: 'IRI',
      value: iriValue.value.trim(),
    }
  } else {
    result = {
      type: 'LITERAL',
      value: literalValue.value.trim(),
    }

    if (language.value.trim()) {
      result.language = language.value.trim()
    } else if (datatype.value.trim()) {
      result.datatype = datatype.value.trim()
    }
  }

  emit('save', result)
  close()
}

const close = () => {
  emit('close')
}

const initializeForm = () => {
  if (isFocusNodeIRI(props.initialValue)) {
    nodeType.value = 'IRI'
    iriValue.value = props.initialValue.value
    literalValue.value = ''
    datatype.value = ''
    language.value = ''
  } else {
    nodeType.value = 'LITERAL'
    iriValue.value = ''
    literalValue.value = props.initialValue.value
    datatype.value = props.initialValue.datatype || ''
    language.value = props.initialValue.language || ''
  }
}

// Watch for language changes to auto-set datatype
watch(language, (newLanguage) => {
  if (newLanguage.trim()) {
    datatype.value = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'
  } else if (datatype.value === 'http://www.w3.org/1999/02/22-rdf-syntax-ns#langString') {
    datatype.value = ''
  }
})

// Watch for modal open to initialize form and focus input
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      initializeForm()
      nextTick(() => {
        if (nodeType.value === 'IRI') {
          iriInput.value?.focus()
        } else {
          literalInput.value?.focus()
        }
      })
    }
  }
)

// Watch for node type changes to focus appropriate input
watch(nodeType, (newType) => {
  nextTick(() => {
    if (newType === 'IRI') {
      iriInput.value?.focus()
    } else {
      literalInput.value?.focus()
    }
  })
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal-container {
  background: #252526;
  border: 1px solid #3e3e42;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #3e3e42;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #cccccc;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #3e3e42;
  color: #ffffff;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #cccccc;
  margin-bottom: 8px;
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

.form-select {
  width: 100%;
  padding: 10px 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  transition: border-color 0.2s;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #007acc;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #007acc;
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #1a1a1a;
}

.form-input::placeholder {
  color: #858585;
}

.field-hint {
  margin: 6px 0 0 0;
  font-size: 11px;
  color: #858585;
  line-height: 1.4;
}

.literal-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #3e3e42;
}

.btn {
  padding: 9px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #007acc 0%, #005a9e 100%);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1177bb 0%, #006bb0 100%);
}

.btn-secondary {
  background: #3e3e42;
  color: #cccccc;
}

.btn-secondary:hover:not(:disabled) {
  background: #4e4e52;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container {
  transform: scale(0.95);
}

.modal-leave-to .modal-container {
  transform: scale(0.95);
}

.w-5 {
  width: 1.25rem;
}

.h-5 {
  height: 1.25rem;
}
</style>
