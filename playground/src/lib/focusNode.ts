import type { FocusNode, FocusNodeNamedNode, FocusNodeLiteral } from '@/types/focusNode'
import { isFocusNodeNamedNode } from '@/types/focusNode'

export function focusNodeToN3String(node: FocusNode): string {
  if (isFocusNodeNamedNode(node)) {
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
  if (isFocusNodeNamedNode(node)) {
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
  // Create a plain object copy to ensure it's serializable for postMessage
  return JSON.parse(JSON.stringify(node))
}

export function deserializeFocusNode(serialized: FocusNode): FocusNode {
  // The FocusNode type is already a plain object structure, so we just return it
  return serialized
}

export function createDefaultFocusNode(): FocusNodeNamedNode {
  return {
    termType: 'NamedNode',
    value: 'http://example.org/resource',
  }
}
