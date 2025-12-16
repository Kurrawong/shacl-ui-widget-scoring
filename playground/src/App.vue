<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { usePlaygroundStore } from '@/stores/playground'
import { useScoringStore } from '@/stores/scoring'
import { useExamples } from '@/composables/useExamples'
import { usePyodide } from '@/composables/usePyodide'
import Header from '@/components/layout/Header.vue'
import Toolbar from '@/components/layout/Toolbar.vue'
import SplitPane from '@/components/layout/SplitPane.vue'
import EditorPanel from '@/components/editors/EditorPanel.vue'
import ResultsPanel from '@/components/results/ResultsPanel.vue'
import Footer from '@/components/layout/Footer.vue'

const playgroundStore = usePlaygroundStore()
const scoringStore = useScoringStore()
const { examples, sharedGraphs, loadExamples } = useExamples()
const { scoreWidgets, isInitializing, error: pyodideError } = usePyodide()

const currentExampleId = ref('example1')

// Initialize on mount
onMounted(async () => {
  try {
    await loadExamples()
    if (examples.value.length > 0) {
      loadExample(examples.value[0].id)
    }
  } catch (err) {
    console.error('Failed to load examples:', err)
  }
})

// Load example into stores
function loadExample(exampleId: string) {
  const example = examples.value.find((ex) => ex.id === exampleId)
  if (example && sharedGraphs.value) {
    playgroundStore.loadExample(example, sharedGraphs.value)
    currentExampleId.value = exampleId
  }
}

// Run scoring
async function runScoring() {
  if (scoringStore.isRunning) return

  scoringStore.setRunning(true)

  // Watch for initialization state changes
  watch(isInitializing, (val) => {
    scoringStore.setInitializingPyodide(val)
  }, { immediate: true })

  try {
    // Parse focus node based on datatype
    const focusNode = playgroundStore.focusNode
    const focusNodeDatatype = playgroundStore.focusNodeDatatype

    const result = await scoreWidgets({
      focusNode,
      focusNodeDatatype,
      widgetScoringGraph: playgroundStore.widgetScoringGraph,
      dataGraphShapes: playgroundStore.dataGraphShapes,
      shapesGraphShapes: playgroundStore.shapesGraphShapes,
      dataGraph: playgroundStore.dataGraph || undefined,
      shapesGraph: playgroundStore.shapesGraph || undefined,
      constraintShape: playgroundStore.constraintShape || undefined,
    })

    scoringStore.setResult(result)
  } catch (err) {
    scoringStore.setError(String(err))
  } finally {
    scoringStore.setRunning(false)
    scoringStore.setInitializingPyodide(false)
  }
}

// Clear results
function clearResults() {
  scoringStore.clear()
}

// Clear all inputs
function clearInputs() {
  playgroundStore.clear()
}

// Watch for example changes
watch(currentExampleId, (newId) => {
  loadExample(newId)
})
</script>

<template>
  <div class="app">
    <Header />

    <Toolbar
      :current-example="currentExampleId"
      :examples="examples.map((ex) => ({ id: ex.id, name: ex.name }))"
      :is-running="scoringStore.isRunning"
      @update:current-example="loadExample"
      @run="runScoring"
      @clear="clearResults"
      @clear-inputs="clearInputs"
    />

    <div class="main-container">
      <SplitPane>
        <template #left>
          <EditorPanel
            :widget-scoring-graph="playgroundStore.widgetScoringGraph"
            :data-graph-shapes="playgroundStore.dataGraphShapes"
            :shapes-graph-shapes="playgroundStore.shapesGraphShapes"
            :data-graph="playgroundStore.dataGraph"
            :shapes-graph="playgroundStore.shapesGraph"
            @update:widget-scoring-graph="(value) => playgroundStore.setWidgetScoringGraph(value)"
            @update:data-graph-shapes="(value) => playgroundStore.setDataGraphShapes(value)"
            @update:shapes-graph-shapes="(value) => playgroundStore.setShapesGraphShapes(value)"
            @update:data-graph="(value) => playgroundStore.setDataGraph(value)"
            @update:shapes-graph="(value) => playgroundStore.setShapesGraph(value)"
          />
        </template>

        <template #right>
          <ResultsPanel
            :result="scoringStore.result"
            :is-running="scoringStore.isRunning"
            :is-error="scoringStore.isError"
            :error-message="scoringStore.errorMessage"
            :current-step="scoringStore.currentStep"
            :is-initializing="scoringStore.isInitializingPyodide"
            @clear="clearResults"
          />
        </template>
      </SplitPane>
    </div>

    <Footer />
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background: #1e1e1e;
  color: #cccccc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
    Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  font-size: 13px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  background: #1e1e1e;
  overflow: hidden;
}

.main-container {
  flex: 1;
  overflow: hidden;
}
</style>
