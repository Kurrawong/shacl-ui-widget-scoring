/**
 * TypeScript types for SHUI Widget Scoring
 */

export interface WidgetScore {
  widget: string
  score: number
  scoreUri?: string
  dataGraphShape?: string
  shapesGraphShape?: string
}

export interface ValidationResult {
  valid: boolean
  shape: string
  details?: string
}

export interface ExecutionStep {
  stepIndex: number
  scoreUri: string
  widget: string
  score: number
  dataGraphValidation: ValidationResult[]
  shapesGraphValidation: ValidationResult[]
  explanation: string
}

export interface ScoringResult {
  widgetScores: WidgetScore[]
  defaultWidget: string | null
  defaultScore: number | null
  executionSteps: ExecutionStep[]
  focusNode: string
  constraintShape?: string | null
}

export interface ScoreInstance {
  uri: string
  widget: string
  score: number
  dataGraphShape?: string
  shapesGraphShape?: string
}

export interface PyodideMessage {
  type: 'init' | 'score' | 'error'
  payload?: unknown
}

export interface ScoringRequest {
  focusNode: string
  focusNodeDatatype: string
  widgetScoringGraph: string
  dataGraphShapes: string
  shapesGraphShapes: string
  dataGraph?: string
  shapesGraph?: string
  constraintShape?: string
}
