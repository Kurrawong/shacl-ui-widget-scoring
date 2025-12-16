/**
 * TypeScript types for Save System
 */

export interface SavedConfiguration {
  id: string
  name: string
  timestamp: number
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
  dataGraph: string
  shapesGraph: string | null
  focusNode: string
  focusNodeDatatype: string
  constraintShape: string | null
}

export interface SavesData {
  version: string
  saves: SavedConfiguration[]
}
