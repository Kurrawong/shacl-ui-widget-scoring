<template>
  <div>
    <!-- Mobile overlay -->
    <Transition name="overlay">
      <div
        v-if="isOpen && isMobile"
        class="mobile-overlay"
        @click="$emit('update:isOpen', false)"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <aside :class="['sidebar', { 'sidebar-collapsed': !isOpen, 'sidebar-mobile': isMobile }]">
      <!-- Header -->
      <div class="sidebar-header">
        <h2 v-if="isOpen" class="sidebar-title">Saved Configurations</h2>
        <button
          class="collapse-button"
          @click="$emit('update:isOpen', !isOpen)"
          :aria-label="isOpen ? 'Collapse sidebar' : 'Expand sidebar'"
        >
          <svg
            v-if="isOpen"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>

      <!-- Saves list -->
      <div v-if="isOpen" class="saves-container">
        <div v-if="saves.length === 0" class="empty-state">
          <svg
            class="w-12 h-12 text-[#858585] mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
            />
          </svg>
          <p class="empty-state-text">No saved configurations yet</p>
          <p class="empty-state-hint">Click "Save" to save your current configuration</p>
        </div>

        <div v-else class="saves-list">
          <div
            v-for="save in saves"
            :key="save.id"
            :class="['save-card', { 'save-card-active': save.id === activeSaveId }]"
            @click="$emit('load', save.id)"
          >
            <div class="save-card-content">
              <h3 class="save-card-title">{{ save.name }}</h3>
              <p class="save-card-date">{{ formatDate(save.timestamp) }}</p>
            </div>
            <button
              class="delete-button"
              @click.stop="$emit('delete', save.id)"
              aria-label="Delete save"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { SavedConfiguration } from '@/types/saves'
import { Trash2 } from 'lucide-vue-next'

interface Props {
  saves: SavedConfiguration[]
  activeSaveId: string | null
  isOpen: boolean
}

interface Emits {
  (e: 'update:isOpen', value: boolean): void
  (e: 'load', id: string): void
  (e: 'delete', id: string): void
}

defineProps<Props>()
defineEmits<Emits>()

const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

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
</script>

<style scoped>
.sidebar {
  position: relative;
  height: 100%;
  background: #252526;
  border-right: 1px solid #3e3e42;
  display: flex;
  flex-direction: column;
  width: 250px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.sidebar-collapsed {
  width: 48px;
}

.sidebar-mobile {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 50;
  transform: translateX(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-mobile.sidebar-collapsed {
  transform: translateX(-100%);
  width: 250px;
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 40;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #3e3e42;
  min-height: 64px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-button {
  background: none;
  border: none;
  color: #cccccc;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapse-button:hover {
  background: #3e3e42;
  color: #ffffff;
}

.saves-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
  height: 100%;
}

.empty-state-text {
  font-size: 14px;
  font-weight: 500;
  color: #cccccc;
  margin: 0 0 8px 0;
}

.empty-state-hint {
  font-size: 12px;
  color: #858585;
  margin: 0;
  line-height: 1.4;
}

.saves-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.save-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
  gap: 8px;
  user-select: none;
}

.save-card:hover {
  background: #2d2d30;
  border-color: #007acc;
  transform: translateX(2px);
}

.save-card-active {
  background: #2d2d30;
  border-color: #007acc;
  box-shadow: 0 0 0 1px #007acc inset;
}

.save-card-active .save-card-title {
  color: #007acc;
}

.save-card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.save-card-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}

.save-card-date {
  font-size: 12px;
  color: #858585;
  margin: 0;
}

.delete-button {
  background: none;
  border: none;
  color: #cccccc;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.delete-button:hover {
  background: #3e3e42;
  color: #f48771;
}

.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

/* Scrollbar styling */
.saves-container::-webkit-scrollbar {
  width: 8px;
}

.saves-container::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.saves-container::-webkit-scrollbar-thumb {
  background: #3e3e42;
  border-radius: 4px;
}

.saves-container::-webkit-scrollbar-thumb:hover {
  background: #4e4e52;
}
</style>
