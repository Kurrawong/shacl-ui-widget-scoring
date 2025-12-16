export interface FocusNodeNamedNode {
  termType: 'NamedNode'
  value: string
}

export interface FocusNodeLiteral {
  termType: 'Literal'
  value: string
  datatype?: string
  language?: string
}

export type FocusNode = FocusNodeNamedNode | FocusNodeLiteral

export function isFocusNodeNamedNode(node: FocusNode): node is FocusNodeNamedNode {
  return node.termType === 'NamedNode'
}

export function isFocusNodeLiteral(node: FocusNode): node is FocusNodeLiteral {
  return node.termType === 'Literal'
}
