<template>
  <div class="editor-panel">
    <InputFields
      :focus-node="focusNode"
      :constraint-shape="constraintShape"
      @update:focus-node="(value) => $emit('update:focusNode', value)"
      @update:constraint-shape="(value) => $emit('update:constraintShape', value)"
    />

    <div class="editor-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
        :aria-label="`Switch to ${tab.label}`"
        :aria-selected="activeTab === tab.id"
        role="tab"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <div class="editor-content">
      <!-- Widget Scoring Graph -->
      <div v-show="activeTab === 'widget-scoring'" class="editor-view">
        <div class="editor-header">
          <h3>Widget Scoring Graph</h3>
          <p class="editor-description">SHUI Score instances for widget recommendations</p>
        </div>
        <TurtleEditor
          :model-value="widgetScoringGraph"
          height="500px"
          :visible="activeTab === 'widget-scoring'"
          @update:model-value="(value) => $emit('update:widgetScoringGraph', value)"
        />
      </div>

      <!-- Data Graph Shapes -->
      <div v-show="activeTab === 'data-graph-shapes'" class="editor-view">
        <div class="editor-header">
          <h3>Data Graph Shapes</h3>
          <p class="editor-description">Shapes for validating data graph value nodes</p>
        </div>
        <TurtleEditor
          :model-value="dataGraphShapes"
          height="500px"
          :visible="activeTab === 'data-graph-shapes'"
          @update:model-value="(value) => $emit('update:dataGraphShapes', value)"
        />
      </div>

      <!-- Shapes Graph Shapes -->
      <div v-show="activeTab === 'shapes-graph-shapes'" class="editor-view">
        <div class="editor-header">
          <h3>Shapes Graph Shapes</h3>
          <p class="editor-description">Shapes for validating constraint shapes</p>
        </div>
        <TurtleEditor
          :model-value="shapesGraphShapes"
          height="500px"
          :visible="activeTab === 'shapes-graph-shapes'"
          @update:model-value="(value) => $emit('update:shapesGraphShapes', value)"
        />
      </div>

      <!-- Data Graph -->
      <div v-show="activeTab === 'data-graph'" class="editor-view">
        <div class="editor-header">
          <h3>Data Graph</h3>
          <p class="editor-description">RDF data graph containing the value node</p>
        </div>
        <TurtleEditor
          :model-value="dataGraph"
          height="500px"
          :visible="activeTab === 'data-graph'"
          @update:model-value="(value) => $emit('update:dataGraph', value)"
        />
      </div>

      <!-- Shapes Graph -->
      <div v-show="activeTab === 'shapes-graph'" class="editor-view">
        <div class="editor-header">
          <h3>Shapes Graph</h3>
          <p class="editor-description">SHACL shape constraints (optional)</p>
        </div>
        <TurtleEditor
          :model-value="shapesGraph"
          height="500px"
          :visible="activeTab === 'shapes-graph'"
          @update:model-value="(value) => $emit('update:shapesGraph', value)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FocusNode } from '@/types/focusNode'
import TurtleEditor from './TurtleEditor.vue'
import InputFields from './InputFields.vue'

interface Props {
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
  dataGraph: string
  shapesGraph: string
  focusNode: FocusNode
  constraintShape: string | null
}

interface Emits {
  (e: 'update:widgetScoringGraph', value: string): void
  (e: 'update:dataGraphShapes', value: string): void
  (e: 'update:shapesGraphShapes', value: string): void
  (e: 'update:dataGraph', value: string): void
  (e: 'update:shapesGraph', value: string): void
  (e: 'update:focusNode', value: FocusNode): void
  (e: 'update:constraintShape', value: string | null): void
}

defineProps<Props>()
defineEmits<Emits>()

const activeTab = ref('data-graph')

const tabs = [
  { id: 'widget-scoring', label: 'Widget Scoring', icon: '🎯' },
  { id: 'data-graph-shapes', label: 'Data Graph Shapes', icon: '📋' },
  { id: 'shapes-graph-shapes', label: 'Shapes Graph Shapes', icon: '📐' },
  { id: 'data-graph', label: 'Data Graph', icon: '📊' },
  { id: 'shapes-graph', label: 'Shapes Graph', icon: '🔷' },
]
</script>

<style scoped>
.editor-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;
}

.editor-tabs {
  display: flex;
  gap: 4px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  overflow-x: auto;
  padding: 4px 8px 0 8px;
}

.tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: none;
  background: transparent;
  color: #858585;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  border-radius: 6px 6px 0 0;
  position: relative;
}

.tab-icon {
  font-size: 14px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.tab-label {
  font-weight: 500;
}

.tab:hover {
  background: #2d2d30;
  color: #cccccc;
}

.tab:hover .tab-icon {
  opacity: 1;
}

.tab.active {
  background: #1e1e1e;
  color: #ffffff;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #007acc 0%, #4ec9b0 100%);
}

.tab.active .tab-icon {
  opacity: 1;
}

.tab:focus-visible {
  outline: 2px solid #007acc;
  outline-offset: -2px;
}

.editor-content {
  flex: 1;
  overflow: hidden;
}

.editor-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.editor-header {
  padding: 12px 16px;
  border-bottom: 1px solid #3e3e42;
  background: #252526;
}

.editor-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.editor-description {
  margin: 4px 0 0 0;
  color: #858585;
  font-size: 12px;
}
</style>
