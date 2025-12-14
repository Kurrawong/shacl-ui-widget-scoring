<template>
  <div class="split-pane" :style="{ flexDirection: direction }">
    <div
      class="pane left-pane"
      :style="{ flexBasis: `${leftSize}%`, minWidth: '200px' }"
    >
      <slot name="left" />
    </div>

    <div class="divider" :class="{ horizontal: direction === 'row' }" @mousedown="startDrag" />

    <div
      class="pane right-pane"
      :style="{ flexBasis: `${100 - leftSize}%`, minWidth: '200px' }"
    >
      <slot name="right" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  direction?: 'row' | 'column'
  initialSplit?: number
}

withDefaults(defineProps<Props>(), {
  direction: 'row',
  initialSplit: 50,
})

const leftSize = ref(50)
let isDragging = false

function startDrag() {
  isDragging = true
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function stopDrag() {
  isDragging = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

function onDrag(e: MouseEvent) {
  if (!isDragging) return

  const container = document.querySelector('.split-pane') as HTMLElement
  if (!container) return

  const containerRect = container.getBoundingClientRect()
  const newSize = ((e.clientX - containerRect.left) / containerRect.width) * 100

  if (newSize > 20 && newSize < 80) {
    leftSize.value = newSize
  }
}

onMounted(() => {
  leftSize.value = 50
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.split-pane {
  display: flex;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.pane {
  flex: 1;
  overflow: auto;
}

.divider {
  width: 4px;
  background: #3e3e42;
  cursor: col-resize;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.divider:hover {
  background: #007acc;
}

.divider.horizontal {
  width: auto;
  height: 4px;
  cursor: row-resize;
}
</style>
