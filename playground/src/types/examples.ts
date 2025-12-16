/**
 * TypeScript types for Examples
 */

import type { FocusNode } from './focusNode'

export interface Example {
  id: string
  name: string
  description: string
  dataGraph: string
  focusNode: FocusNode
  shapesGraph: string | null
  constraintShape: string | null
}

export interface SharedGraphs {
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
}

export interface ExamplesData {
  version: string
  sharedGraphs: SharedGraphs
  examples: Example[]
}
