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
  margin: 0 0 18px 0;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-list h3::before {
  content: '📊';
  font-size: 18px;
}

.scores-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #252526;
  border-radius: 8px;
  border-left: 4px solid #3e3e42;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.score-item:hover {
  background: #2d2d30;
  border-left-color: #007acc;
  transform: translateX(2px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.score-item.highest {
  border-left-color: #4ec9b0;
  background: linear-gradient(135deg, rgba(78, 201, 176, 0.12) 0%, rgba(78, 201, 176, 0.05) 100%);
  box-shadow: 0 2px 8px rgba(78, 201, 176, 0.2);
}

.score-item.highest:hover {
  background: linear-gradient(135deg, rgba(78, 201, 176, 0.18) 0%, rgba(78, 201, 176, 0.08) 100%);
}

.score-rank {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3e3e42;
  border-radius: 6px;
  color: #cccccc;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.score-item.highest .score-rank {
  background: linear-gradient(135deg, #4ec9b0 0%, #3eb8a0 100%);
  color: #1e1e1e;
  box-shadow: 0 2px 8px rgba(78, 201, 176, 0.4);
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 150px;
}

.score-widget {
  margin: 0;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  word-break: break-word;
}

.score-value {
  margin: 0;
  color: #9cdcfe;
  font-size: 12px;
  font-weight: 500;
}

.score-instance {
  margin: 6px 0 0 0;
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
  background: rgba(156, 220, 254, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
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
  gap: 5px;
  flex-wrap: wrap;
}

.shape-tag {
  background: rgba(156, 220, 254, 0.15);
  color: #9cdcfe;
  padding: 3px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 10px;
  font-weight: 500;
  border: 1px solid rgba(156, 220, 254, 0.2);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #3e3e42;
  border-radius: 4px;
  overflow: hidden;
  min-width: 100px;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #007acc 0%, #4ec9b0 100%);
  border-radius: 4px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 8px rgba(78, 201, 176, 0.4);
}
</style>
