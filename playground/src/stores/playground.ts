import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FocusNode } from '@/types/focusNode'

export const usePlaygroundStore = defineStore('playground', () => {
  // State
  const currentExample = ref<string>('example1')
  const widgetScoringGraph = ref<string>('')
  const dataGraphShapes = ref<string>('')
  const shapesGraphShapes = ref<string>('')
  const dataGraph = ref<string>('')
  const shapesGraph = ref<string>('')
  const focusNode = ref<FocusNode>({
    termType: 'NamedNode',
    value: 'http://example.org/resource',
  })
  const constraintShape = ref<string | null>(null)

  // Actions
  function setCurrentExample(exampleId: string) {
    currentExample.value = exampleId
  }

  function setWidgetScoringGraph(turtle: string) {
    widgetScoringGraph.value = turtle
  }

  function setDataGraphShapes(turtle: string) {
    dataGraphShapes.value = turtle
  }

  function setShapesGraphShapes(turtle: string) {
    shapesGraphShapes.value = turtle
  }

  function setDataGraph(turtle: string) {
    dataGraph.value = turtle
  }

  function setShapesGraph(turtle: string) {
    shapesGraph.value = turtle
  }

  function setFocusNode(value: FocusNode) {
    focusNode.value = value
  }

  function setConstraintShape(shape: string | null) {
    constraintShape.value = shape
  }

  function loadExample(
    example: {
      dataGraph: string
      focusNode: FocusNode
      shapesGraph: string | null
      constraintShape: string | null
    },
    sharedGraphs: {
      widgetScoringGraph: string
      dataGraphShapes: string
      shapesGraphShapes: string
    }
  ) {
    setDataGraph(example.dataGraph)
    setFocusNode(example.focusNode)
    setShapesGraph(example.shapesGraph || '')
    setConstraintShape(example.constraintShape)
    setWidgetScoringGraph(sharedGraphs.widgetScoringGraph)
    setDataGraphShapes(sharedGraphs.dataGraphShapes)
    setShapesGraphShapes(sharedGraphs.shapesGraphShapes)
  }

  function clear() {
    widgetScoringGraph.value = ''
    dataGraphShapes.value = ''
    shapesGraphShapes.value = ''
    dataGraph.value = ''
    shapesGraph.value = ''
    focusNode.value = {
      termType: 'NamedNode',
      value: 'http://example.org/resource',
    }
    constraintShape.value = null
  }

  return {
    // State
    currentExample,
    widgetScoringGraph,
    dataGraphShapes,
    shapesGraphShapes,
    dataGraph,
    shapesGraph,
    focusNode,
    constraintShape,
    // Actions
    setCurrentExample,
    setWidgetScoringGraph,
    setDataGraphShapes,
    setShapesGraphShapes,
    setDataGraph,
    setShapesGraph,
    setFocusNode,
    setConstraintShape,
    loadExample,
    clear,
  }
})
