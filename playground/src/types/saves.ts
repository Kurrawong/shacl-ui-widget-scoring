/**
 * TypeScript types for Save System
 */

import type { FocusNode } from './focusNode'

export interface SavedConfiguration {
  id: string
  name: string
  timestamp: number
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
  dataGraph: string
  shapesGraph: string | null
  focusNode: FocusNode
  constraintShape: string | null
}

export interface SavesData {
  version: string
  saves: SavedConfiguration[]
}
