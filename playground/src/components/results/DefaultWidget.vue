<template>
  <div class="default-widget">
    <div class="widget-card">
      <div class="widget-icon">🎯</div>
      <div class="widget-info">
        <h2>Recommended Widget</h2>
        <p class="widget-name">{{ widgetName }}</p>
        <p class="widget-score">Score: <strong>{{ score }}</strong></p>
        <p v-if="scoreInstance?.scoreUri" class="widget-score-uri">
          <span class="label">Score Instance:</span>
          <span class="uri">{{ getInstanceName(scoreInstance.scoreUri) }}</span>
        </p>
        <p v-if="scoreInstance?.dataGraphShape || scoreInstance?.shapesGraphShape" class="widget-shapes">
          <span class="label">Shapes:</span>
          <span class="shapes-list">
            <span v-if="scoreInstance?.dataGraphShape" class="shape-tag">{{ getShapeName(scoreInstance.dataGraphShape) }}</span>
            <span v-if="scoreInstance?.shapesGraphShape" class="shape-tag">{{ getShapeName(scoreInstance.shapesGraphShape) }}</span>
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { WidgetScore } from '@/types/scoring'

interface Props {
  widget: string
  score: number | null
  widgetScores?: WidgetScore[]
}

const props = withDefaults(defineProps<Props>(), {
  score: 0,
  widgetScores: () => []
})

const widgetName = computed(() => {
  if (props.widget) {
    return props.widget.split('/').pop() || props.widget
  }
  return 'Unknown'
})

const scoreInstance = computed(() => {
  if (!props.widget || !props.widgetScores) return null
  return props.widgetScores.find((ws) => ws.widget === props.widget)
})

function getInstanceName(uri: string): string {
  return uri.split('/').pop() || uri
}

function getShapeName(shape: string): string {
  return shape.split('#').pop()?.split('/').pop() || shape
}
</script>

<style scoped>
.default-widget {
  width: 100%;
}

.widget-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px;
  background: linear-gradient(135deg, #007acc 0%, #005a9e 100%);
  border-radius: 12px;
  color: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 122, 204, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  overflow: hidden;
}

.widget-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(78, 201, 176, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

.widget-icon {
  font-size: 56px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
  animation: pulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.widget-info {
  flex: 1;
  z-index: 1;
}

.widget-info h2 {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  opacity: 0.85;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.widget-name {
  margin: 10px 0 6px 0;
  font-size: 28px;
  font-weight: 700;
  word-break: break-word;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  line-height: 1.2;
}

.widget-score {
  margin: 0;
  font-size: 15px;
  opacity: 0.95;
  font-weight: 500;
}

.widget-score strong {
  font-size: 20px;
  font-weight: 700;
  color: #4ec9b0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.widget-score-uri {
  margin: 10px 0 0 0;
  font-size: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  opacity: 0.9;
}

.widget-score-uri .label {
  font-weight: 600;
  opacity: 0.95;
}

.widget-score-uri .uri {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.15);
  padding: 3px 7px;
  border-radius: 4px;
}

.widget-shapes {
  margin: 8px 0 0 0;
  font-size: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  opacity: 0.9;
}

.widget-shapes .label {
  font-weight: 600;
  opacity: 0.95;
}

.shapes-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.shape-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
