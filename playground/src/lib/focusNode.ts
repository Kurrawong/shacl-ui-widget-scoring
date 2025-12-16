import type { FocusNode, FocusNodeIRI, FocusNodeLiteral } from '@/types/focusNode'
import { isFocusNodeIRI } from '@/types/focusNode'

export function focusNodeToN3String(node: FocusNode): string {
  if (isFocusNodeIRI(node)) {
    return `<${node.value}>`
  }

  // Literal node
  let result = `"${node.value}"`

  if (node.language) {
    result += `@${node.language}`
  } else if (node.datatype) {
    result += `^^<${node.datatype}>`
  }

  return result
}

export function focusNodeToRDFLibPython(node: FocusNode): string {
  if (isFocusNodeIRI(node)) {
    return `URIRef("${node.value}")`
  }

  // Literal node
  if (node.language) {
    return `Literal("${node.value}", lang="${node.language}")`
  }

  if (node.datatype) {
    return `Literal("${node.value}", datatype=URIRef("${node.datatype}"))`
  }

  return `Literal("${node.value}")`
}

export function serializeFocusNode(node: FocusNode): FocusNode {
  // The FocusNode type is already a plain object structure, so we just return it
  return node
}

export function deserializeFocusNode(serialized: FocusNode): FocusNode {
  // The FocusNode type is already a plain object structure, so we just return it
  return serialized
}

export function createDefaultFocusNode(): FocusNodeIRI {
  return {
    type: 'IRI',
    value: 'http://example.org/resource',
  }
}
