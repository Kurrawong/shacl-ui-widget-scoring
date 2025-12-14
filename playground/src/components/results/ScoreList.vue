<template>
  <div class="score-list">
    <h3>All Widget Scores</h3>
    <div class="scores-container">
      <div
        v-for="(ws, index) in sortedScores"
        :key="index"
        class="score-item"
        :class="{ highest: index === 0 }"
      >
        <div class="score-rank">{{ index + 1 }}</div>
        <div class="score-info">
          <p class="score-widget">{{ getWidgetName(ws.widget) }}</p>
          <p class="score-value">Score: {{ ws.score }}</p>
          <p class="score-instance" v-if="ws.scoreUri">
            <span class="label">Score Instance:</span>
            <span class="uri">{{ getInstanceName(ws.scoreUri) }}</span>
          </p>
          <p class="score-shapes" v-if="ws.dataGraphShape || ws.shapesGraphShape">
            <span class="label">Shapes:</span>
            <span class="shapes-list">
              <span v-if="ws.dataGraphShape" class="shape-tag">{{ getShapeName(ws.dataGraphShape) }}</span>
              <span v-if="ws.shapesGraphShape" class="shape-tag">{{ getShapeName(ws.shapesGraphShape) }}</span>
            </span>
          </p>
        </div>
        <div class="score-bar">
          <div class="score-fill" :style="{ width: getScorePercentage(ws.score) + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { WidgetScore } from '@/types/scoring'

interface Props {
  widgetScores: WidgetScore[]
}

const props = defineProps<Props>()

const sortedScores = computed(() => {
  return [...props.widgetScores].sort((a, b) => b.score - a.score)
})

function getWidgetName(widget: string): string {
  return widget.split('/').pop() || widget
}

function getInstanceName(uri: string): string {
  return uri.split('/').pop() || uri
}

function getShapeName(shape: string): string {
  return shape.split('#').pop()?.split('/').pop() || shape
}

function getScorePercentage(score: number): number {
  const minScore = Math.min(...props.widgetScores.map((ws) => ws.score))
  const maxScore = Math.max(...props.widgetScores.map((ws) => ws.score))
  if (maxScore === minScore) return 50
  return ((score - minScore) / (maxScore - minScore)) * 100
}
</script>

<style scoped>
.score-list {
  width: 100%;
}

.score-list h3 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 14px;
}

.scores-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #252526;
  border-radius: 4px;
  border-left: 3px solid #3e3e42;
  transition: all 0.2s;
}

.score-item:hover {
  background: #2d2d30;
  border-left-color: #007acc;
}

.score-item.highest {
  border-left-color: #4ec9b0;
  background: rgba(78, 201, 176, 0.1);
}

.score-rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3e3e42;
  border-radius: 4px;
  color: #cccccc;
  font-weight: 600;
  flex-shrink: 0;
}

.score-item.highest .score-rank {
  background: #4ec9b0;
  color: #1e1e1e;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 150px;
}

.score-widget {
  margin: 0;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  word-break: break-word;
}

.score-value {
  margin: 0;
  color: #858585;
  font-size: 12px;
}

.score-instance {
  margin: 4px 0 0 0;
  color: #858585;
  font-size: 11px;
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.score-instance .label {
  color: #6a9fb5;
  font-weight: 600;
}

.score-instance .uri {
  color: #9cdcfe;
  font-family: 'Monaco', 'Menlo', monospace;
  word-break: break-word;
}

.score-shapes {
  margin: 4px 0 0 0;
  color: #858585;
  font-size: 11px;
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.score-shapes .label {
  color: #6a9fb5;
  font-weight: 600;
}

.shapes-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.shape-tag {
  background: rgba(156, 220, 254, 0.15);
  color: #9cdcfe;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 10px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #3e3e42;
  border-radius: 3px;
  overflow: hidden;
  min-width: 100px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #007acc 0%, #4ec9b0 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}
</style>
