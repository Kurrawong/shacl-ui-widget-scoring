export interface FocusNodeIRI {
  type: 'IRI'
  value: string
}

export interface FocusNodeLiteral {
  type: 'LITERAL'
  value: string
  datatype?: string
  language?: string
}

export type FocusNode = FocusNodeIRI | FocusNodeLiteral

export function isFocusNodeIRI(node: FocusNode): node is FocusNodeIRI {
  return node.type === 'IRI'
}

export function isFocusNodeLiteral(node: FocusNode): node is FocusNodeLiteral {
  return node.type === 'LITERAL'
}
