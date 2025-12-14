import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlaygroundStore = defineStore('playground', () => {
  // State
  const currentExample = ref<string>('example1')
  const widgetScoringGraph = ref<string>('')
  const dataGraphShapes = ref<string>('')
  const shapesGraphShapes = ref<string>('')
  const dataGraph = ref<string>('')
  const shapesGraph = ref<string>('')
  const valueNode = ref<string>('true')
  const valueNodeDatatype = ref<string>('http://www.w3.org/2001/XMLSchema#boolean')
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

  function setValueNode(value: string) {
    valueNode.value = value
  }

  function setValueNodeDatatype(datatype: string) {
    valueNodeDatatype.value = datatype
  }

  function setConstraintShape(shape: string | null) {
    constraintShape.value = shape
  }

  function loadExample(
    example: {
      dataGraph: string
      valueNode: string
      valueNodeDatatype: string
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
    setValueNode(example.valueNode)
    setValueNodeDatatype(example.valueNodeDatatype)
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
    valueNode.value = 'true'
    valueNodeDatatype.value = 'http://www.w3.org/2001/XMLSchema#boolean'
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
    valueNode,
    valueNodeDatatype,
    constraintShape,
    // Actions
    setCurrentExample,
    setWidgetScoringGraph,
    setDataGraphShapes,
    setShapesGraphShapes,
    setDataGraph,
    setShapesGraph,
    setValueNode,
    setValueNodeDatatype,
    setConstraintShape,
    loadExample,
    clear,
  }
})
