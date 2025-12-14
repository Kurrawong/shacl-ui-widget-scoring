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
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #007acc 0%, #004b7a 100%);
  border-radius: 8px;
  color: #ffffff;
}

.widget-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.widget-info {
  flex: 1;
}

.widget-info h2 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.widget-name {
  margin: 8px 0 4px 0;
  font-size: 24px;
  font-weight: bold;
  word-break: break-word;
}

.widget-score {
  margin: 0;
  font-size: 14px;
  opacity: 0.95;
}

.widget-score strong {
  font-size: 18px;
  font-weight: 700;
}

.widget-score-uri {
  margin: 8px 0 0 0;
  font-size: 12px;
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
  opacity: 0.85;
}

.widget-score-uri .label {
  font-weight: 600;
  opacity: 0.95;
}

.widget-score-uri .uri {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
}

.widget-shapes {
  margin: 6px 0 0 0;
  font-size: 12px;
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
  opacity: 0.85;
}

.widget-shapes .label {
  font-weight: 600;
  opacity: 0.95;
}

.shapes-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.shape-tag {
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 10px;
}
</style>
