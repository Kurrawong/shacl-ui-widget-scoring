<template>
  <div class="editor-panel">
    <div class="editor-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
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
import TurtleEditor from './TurtleEditor.vue'

interface Props {
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
  dataGraph: string
  shapesGraph: string
}

interface Emits {
  (e: 'update:widgetScoringGraph', value: string): void
  (e: 'update:dataGraphShapes', value: string): void
  (e: 'update:shapesGraphShapes', value: string): void
  (e: 'update:dataGraph', value: string): void
  (e: 'update:shapesGraph', value: string): void
}

defineProps<Props>()
defineEmits<Emits>()

const activeTab = ref('data-graph')

const tabs = [
  { id: 'widget-scoring', label: 'Widget Scoring' },
  { id: 'data-graph-shapes', label: 'Data Graph Shapes' },
  { id: 'shapes-graph-shapes', label: 'Shapes Graph Shapes' },
  { id: 'data-graph', label: 'Data Graph' },
  { id: 'shapes-graph', label: 'Shapes Graph' },
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
  gap: 0;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  overflow-x: auto;
}

.tab {
  flex-shrink: 0;
  padding: 10px 16px;
  border: none;
  background: #252526;
  color: #cccccc;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab:hover {
  background: #2d2d30;
  color: #eeeeee;
}

.tab.active {
  background: #1e1e1e;
  color: #ffffff;
  border-bottom: 2px solid #007acc;
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
