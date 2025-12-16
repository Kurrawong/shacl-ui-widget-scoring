<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { usePlaygroundStore } from '@/stores/playground'
import { useScoringStore } from '@/stores/scoring'
import { useExamples } from '@/composables/useExamples'
import { usePyodide } from '@/composables/usePyodide'
import { useSaves } from '@/composables/useSaves'
import { useToast } from '@/composables/useToast'
import Header from '@/components/layout/Header.vue'
import Toolbar from '@/components/layout/Toolbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import SaveModal from '@/components/layout/SaveModal.vue'
import { Toaster } from '@/components/ui/sonner'
import SplitPane from '@/components/layout/SplitPane.vue'
import EditorPanel from '@/components/editors/EditorPanel.vue'
import ResultsPanel from '@/components/results/ResultsPanel.vue'
import Footer from '@/components/layout/Footer.vue'
import 'vue-sonner/style.css'

const playgroundStore = usePlaygroundStore()
const scoringStore = useScoringStore()
const { examples, sharedGraphs, loadExamples } = useExamples()
const { scoreWidgets, isInitializing, error: pyodideError } = usePyodide()
const { saves, activeSaveId, hasSaves, createSave, updateSave, deleteSave, getSave } = useSaves()
const { success, error: showError } = useToast()

const sidebarOpen = ref(true)
const saveModalOpen = ref(false)

// Initialize on mount
onMounted(async () => {
  try {
    await loadExamples()

    // Pre-populate localStorage with examples if no saves exist
    if (!hasSaves.value && examples.value.length > 0 && sharedGraphs.value) {
      examples.value.forEach((example) => {
        createSave(example.name, {
          widgetScoringGraph: sharedGraphs.value!.widgetScoringGraph,
          dataGraphShapes: sharedGraphs.value!.dataGraphShapes,
          shapesGraphShapes: sharedGraphs.value!.shapesGraphShapes,
          dataGraph: example.dataGraph,
          shapesGraph: example.shapesGraph || '',
          focusNode: example.focusNode,
          focusNodeDatatype: example.focusNodeDatatype,
          constraintShape: example.constraintShape,
        })
      })
    }

    // Load the first save if available
    if (saves.value.length > 0) {
      loadSave(saves.value[0].id)
    }
  } catch (err) {
    console.error('Failed to initialize:', err)
  }
})

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
  activeSaveId.value = null
}

// Load a saved configuration
function loadSave(saveId: string) {
  const save = getSave(saveId)
  if (save) {
    playgroundStore.setWidgetScoringGraph(save.widgetScoringGraph)
    playgroundStore.setDataGraphShapes(save.dataGraphShapes)
    playgroundStore.setShapesGraphShapes(save.shapesGraphShapes)
    playgroundStore.setDataGraph(save.dataGraph)
    playgroundStore.setShapesGraph(save.shapesGraph || '')
    playgroundStore.setFocusNode(save.focusNode)
    playgroundStore.setFocusNodeDatatype(save.focusNodeDatatype)
    playgroundStore.setConstraintShape(save.constraintShape)
    activeSaveId.value = saveId
    success(`Loaded: ${save.name}`)
  }
}

// Open save modal
function openSaveModal() {
  saveModalOpen.value = true
}

// Handle save from modal
function handleSave(name: string, overwriteId?: string) {
  try {
    const config = {
      widgetScoringGraph: playgroundStore.widgetScoringGraph,
      dataGraphShapes: playgroundStore.dataGraphShapes,
      shapesGraphShapes: playgroundStore.shapesGraphShapes,
      dataGraph: playgroundStore.dataGraph,
      shapesGraph: playgroundStore.shapesGraph,
      focusNode: playgroundStore.focusNode,
      focusNodeDatatype: playgroundStore.focusNodeDatatype,
      constraintShape: playgroundStore.constraintShape,
    }

    if (overwriteId) {
      updateSave(overwriteId, config)
      activeSaveId.value = overwriteId
      success(`Updated: ${name}`)
    } else {
      const newSave = createSave(name, config)
      activeSaveId.value = newSave.id
      success(`Saved: ${name}`)
    }

    saveModalOpen.value = false
  } catch (err) {
    showError(`Failed to save: ${err}`)
  }
}

// Handle delete save
function handleDeleteSave(saveId: string) {
  const save = getSave(saveId)
  if (save && confirm(`Delete "${save.name}"? This cannot be undone.`)) {
    deleteSave(saveId)
    success(`Deleted: ${save.name}`)
  }
}
</script>

<template>
  <div class="app">
    <Header />

    <Toolbar
      :is-running="scoringStore.isRunning"
      @run="runScoring"
      @clear="clearResults"
      @clear-inputs="clearInputs"
      @save="openSaveModal"
    />

    <div class="main-container">
      <Sidebar
        v-model:is-open="sidebarOpen"
        :saves="saves"
        :active-save-id="activeSaveId"
        @load="loadSave"
        @delete="handleDeleteSave"
      />

      <div class="content-area">
        <SplitPane>
          <template #left>
            <EditorPanel
              :widget-scoring-graph="playgroundStore.widgetScoringGraph"
              :data-graph-shapes="playgroundStore.dataGraphShapes"
              :shapes-graph-shapes="playgroundStore.shapesGraphShapes"
              :data-graph="playgroundStore.dataGraph"
              :shapes-graph="playgroundStore.shapesGraph"
              :focus-node="playgroundStore.focusNode"
              :focus-node-datatype="playgroundStore.focusNodeDatatype"
              :constraint-shape="playgroundStore.constraintShape"
              @update:widget-scoring-graph="(value) => playgroundStore.setWidgetScoringGraph(value)"
              @update:data-graph-shapes="(value) => playgroundStore.setDataGraphShapes(value)"
              @update:shapes-graph-shapes="(value) => playgroundStore.setShapesGraphShapes(value)"
              @update:data-graph="(value) => playgroundStore.setDataGraph(value)"
              @update:shapes-graph="(value) => playgroundStore.setShapesGraph(value)"
              @update:focus-node="(value) => playgroundStore.setFocusNode(value)"
              @update:focus-node-datatype="(value) => playgroundStore.setFocusNodeDatatype(value)"
              @update:constraint-shape="(value) => playgroundStore.setConstraintShape(value)"
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
    </div>

    <Footer />

    <SaveModal
      :is-open="saveModalOpen"
      :existing-saves="saves"
      @close="saveModalOpen = false"
      @save="handleSave"
    />

    <Toaster />
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
  display: flex;
  overflow: hidden;
}

.content-area {
  flex: 1;
  overflow: hidden;
}
</style>
