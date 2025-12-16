<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div class="modal-container">
          <div class="modal-header">
            <h2 class="modal-title">Save Configuration</h2>
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
              <label class="form-label">Save Name</label>
              <input
                v-model="saveName"
                type="text"
                class="form-input"
                placeholder="Enter a name for this configuration"
                @keydown.enter="handleSave"
                ref="nameInput"
              />
              <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
            </div>

            <div v-if="existingSaves.length > 0" class="existing-saves">
              <p class="existing-saves-label">Or overwrite an existing save:</p>
              <div class="saves-list">
                <button
                  v-for="save in existingSaves"
                  :key="save.id"
                  :class="['save-item', { selected: selectedSaveId === save.id }]"
                  @click="selectSave(save.id, save.name)"
                >
                  <div class="save-item-content">
                    <span class="save-name">{{ save.name }}</span>
                    <span class="save-date">{{ formatDate(save.timestamp) }}</span>
                  </div>
                  <svg
                    v-if="selectedSaveId === save.id"
                    class="w-5 h-5 text-[#007acc]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="close">Cancel</button>
            <button class="btn btn-primary" @click="handleSave" :disabled="!canSave">
              {{ saveButtonText }}
            </button>
          </div>
        </div>

        <!-- Overwrite confirmation dialog -->
        <Transition name="modal">
          <div v-if="showConfirmation" class="modal-overlay" @click.self="cancelOverwrite">
            <div class="confirmation-dialog">
              <h3 class="confirmation-title">Overwrite Save?</h3>
              <p class="confirmation-message">
                Are you sure you want to overwrite "{{ saveName }}"? This action cannot be undone.
              </p>
              <div class="confirmation-actions">
                <button class="btn btn-secondary" @click="cancelOverwrite">Cancel</button>
                <button class="btn btn-danger" @click="confirmOverwrite">Overwrite</button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { SavedConfiguration } from '@/types/saves'

interface Props {
  isOpen: boolean
  existingSaves: SavedConfiguration[]
}

interface Emits {
  (e: 'close'): void
  (e: 'save', name: string, overwriteId?: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const saveName = ref('')
const selectedSaveId = ref<string | null>(null)
const errorMessage = ref('')
const showConfirmation = ref(false)
const nameInput = ref<HTMLInputElement | null>(null)

const canSave = computed(() => saveName.value.trim().length > 0)

const saveButtonText = computed(() => {
  if (selectedSaveId.value) {
    return 'Overwrite'
  }
  return 'Save'
})

const selectSave = (id: string, name: string) => {
  selectedSaveId.value = selectedSaveId.value === id ? null : id
  saveName.value = name
  errorMessage.value = ''
}

const handleSave = () => {
  errorMessage.value = ''

  if (!saveName.value.trim()) {
    errorMessage.value = 'Please enter a save name'
    return
  }

  // Check if overwriting an existing save
  if (selectedSaveId.value) {
    showConfirmation.value = true
    return
  }

  // Check if name already exists
  const existingWithName = props.existingSaves.find(
    (s) => s.name.toLowerCase() === saveName.value.trim().toLowerCase()
  )

  if (existingWithName) {
    selectedSaveId.value = existingWithName.id
    showConfirmation.value = true
    return
  }

  // Create new save
  emit('save', saveName.value.trim())
  close()
}

const confirmOverwrite = () => {
  if (selectedSaveId.value) {
    emit('save', saveName.value.trim(), selectedSaveId.value)
  }
  showConfirmation.value = false
  close()
}

const cancelOverwrite = () => {
  showConfirmation.value = false
}

const close = () => {
  if (!showConfirmation.value) {
    emit('close')
    resetForm()
  }
}

const resetForm = () => {
  saveName.value = ''
  selectedSaveId.value = null
  errorMessage.value = ''
}

const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMs = now.getTime() - date.getTime()
  const diffInMinutes = Math.floor(diffInMs / 60000)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)

  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInHours < 24) return `${diffInHours}h ago`
  if (diffInDays < 7) return `${diffInDays}d ago`

  return date.toLocaleDateString()
}

// Focus input when modal opens
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      nextTick(() => {
        nameInput.value?.focus()
      })
    }
  }
)
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
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #cccccc;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #007acc;
}

.form-input::placeholder {
  color: #858585;
}

.error-message {
  margin-top: 6px;
  font-size: 12px;
  color: #f48771;
}

.existing-saves {
  margin-top: 24px;
}

.existing-saves-label {
  font-size: 13px;
  color: #858585;
  margin-bottom: 12px;
}

.saves-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.save-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}

.save-item:hover {
  background: #2d2d30;
  border-color: #007acc;
}

.save-item.selected {
  background: #2d2d30;
  border-color: #007acc;
}

.save-item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.save-name {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

.save-date {
  font-size: 12px;
  color: #858585;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #3e3e42;
}

.confirmation-dialog {
  background: #252526;
  border: 1px solid #3e3e42;
  border-radius: 8px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

.confirmation-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 12px 0;
}

.confirmation-message {
  font-size: 14px;
  color: #cccccc;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.confirmation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

.btn-danger {
  background: linear-gradient(135deg, #f48771 0%, #d9534f 100%);
  color: #ffffff;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #ff9682 0%, #e76460 100%);
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
.modal-enter-active .confirmation-dialog,
.modal-leave-active .modal-container,
.modal-leave-active .confirmation-dialog {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-enter-from .confirmation-dialog {
  transform: scale(0.95);
}

.modal-leave-to .modal-container,
.modal-leave-to .confirmation-dialog {
  transform: scale(0.95);
}
</style>
