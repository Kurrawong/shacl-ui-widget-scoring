# SHACL UI Widget Scoring

## Abstract

This document defines the SHACL UI Widget Scoring ontology and algorithm. It provides a mechanism to associate UI widgets with SHACL shapes and data values based on a scoring system, enabling dynamic selection of the most appropriate widget for a given user interface context.

## Status of This Document

This document is a draft specification for the SHACL UI Task Force.

## 1. Introduction

When automatically generating user interfaces from data models, it is often necessary to determine the most suitable user interface "widget" (e.g., a text input, a date picker, a checkbox) for a given value or constraint. SHACL (Shapes Constraint Language) provides a powerful way to describe data constraints. This specification extends the SHACL ecosystem by defining a scoring mechanism to select widgets based on both the data being edited and the SHACL shapes constraining that data.

The goal is to allow developers to define rules such as:

- "Use a DatePicker if the value is a date."
- "Use a BooleanSelect if the value is a boolean."
- "Prefer a specific editor if a specific SHACL facet (like `sh:in`) is present."

## 2. Terminology

The keywords **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC2119].

<dl>
  <dt>Data Graph</dt>
  <dd>The RDF graph containing the data being viewed or edited. This is provided as an input to the scoring algorithm.</dd>
  <dt>Shapes Graph</dt>
  <dd>The RDF graph containing the SHACL shapes that constrain the Data Graph. This is provided as an input to the scoring algorithm.</dd>
  <dt>Widget Scoring Graph</dt>
  <dd>An RDF graph containing <code>shui:Score</code> instances that define the widget scoring rules.</dd>
  <dt>Data Graph Shapes Graph</dt>
  <dd>An RDF graph containing SHACL shapes referenced by <code>shui:dataGraphShape</code> properties. These shapes validate the Focus Node during widget scoring.</dd>
  <dt>Shapes Graph Shapes Graph</dt>
  <dd>An RDF graph containing SHACL shapes referenced by <code>shui:shapesGraphShape</code> properties. These shapes validate the Constraint Shape during widget scoring.</dd>
  <dt>Focus Node</dt>
  <dd>A node from the Data Graph that serves as the focus node for validation against shapes referenced by <code>shui:dataGraphShape</code>.</dd>
  <dt>Constraint Shape</dt>
  <dd>A SHACL shape node (<code>sh:NodeShape</code> or <code>sh:PropertyShape</code>) from the Shapes Graph that serves as the focus node for validation against shapes referenced by <code>shui:shapesGraphShape</code>. Both node shapes and property shapes are valid constraint shapes.</dd>
</dl>

## 3. The Widget Scoring Model

The Widget Scoring Model relies on instances of the class `shui:Score` to define rules for scoring widgets.

### 3.1. Namespace

The namespace for this ontology is `http://www.w3.org/ns/shacl-ui#`. The prefix `shui` is used throughout this document.

### 3.2. Class: shui:Score

A `shui:Score` instance represents a rule that assigns a numeric score to a specific widget type if certain conditions are met.

### 3.3. Properties

The following properties are used to define a `shui:Score` instance.

#### 3.3.1. shui:widget

- **Domain**: `shui:Score`
- **Range**: `rdfs:Class` (or a specific Widget class)
- **Multiplicity**: Exactly one (1).

Reference to the identifier of the widget (e.g., `shui:BooleanSelectEditor`).

#### 3.3.2. shui:score

- **Domain**: `shui:Score`
- **Range**: `xsd:decimal` or `xsd:integer`
- **Multiplicity**: Exactly one (1).

The numeric score assigned to the widget if the conditions are met. Scores MUST be positive, zero, or negative decimals/integers. The widget with the highest positive score is the default selection. Positive scores indicate selectable widget choices. A score of zero indicates the widget is not selectable at all. Negative scores are valid but will almost never be selected as the default widget.

Score comparisons SHOULD use the precision provided in the RDF literal. Implementations MUST use consistent decimal comparison (not floating-point approximation).

#### 3.3.3. shui:dataGraphShape

- **Domain**: `shui:Score`
- **Range**: `sh:Shape`
- **Multiplicity**: Zero or more.

Links to a SHACL shape defined in the **Data Graph Shapes Graph** that validates the **Focus Node**. If the Focus Node conforms to this shape, the condition is satisfied. If the Focus Node does not exist in the Data Graph, the condition fails and the score is not applicable.

#### 3.3.4. shui:shapesGraphShape

- **Domain**: `shui:Score`
- **Range**: `sh:Shape`
- **Multiplicity**: Zero or more.

Links to a SHACL shape defined in the **Shapes Graph Shapes Graph** that validates the **Constraint Shape**. This allows scoring based on the definition of the shape itself (e.g., "does the shape have a `sh:datatype` constraint?"). If the Constraint Shape does not exist in the Shapes Graph, the condition fails and the score is not applicable.

### 3.4. SHACL Feature Support

The shapes referenced by `shui:dataGraphShape` and `shui:shapesGraphShape` MAY use any SHACL Core features, including sh:and, sh:or, sh:not, and nested shapes. Support for SHACL-SPARQL constraints is OPTIONAL and implementation-dependent.

Recursive or circular shape references are handled according to the SHACL validator's specification. Implementations MUST NOT enter infinite loops.

Here's the rewritten Section 4 with a helper function for the symmetric validation logic:

---

## 4. Scoring Algorithm

The input to the scoring algorithm is:

1.  **Focus Node**: A node from the Data Graph. This is a REQUIRED input.
2.  **Data Graph** (Optional): The graph containing the Focus Node.
3.  **Constraint Shape** (Optional): A shape node from the Shapes Graph.
4.  **Shapes Graph** (Optional): The graph containing the Constraint Shape.
5.  **Widget Scoring Graph**: The graph containing `shui:Score` instances.
6.  **Data Graph Shapes Graph**: The graph containing shapes referenced by `shui:dataGraphShape`.
7.  **Shapes Graph Shapes Graph**: The graph containing shapes referenced by `shui:shapesGraphShape`.

The output is a list of widgets with their calculated scores.

**Note**: If a Focus Node conforms to multiple Property Shapes, the algorithm SHOULD be invoked separately for each Property Shape to determine the appropriate widget for each property.

### Prerequisites

If the **Focus Node** is not provided, the implementation MUST raise an error and terminate the algorithm. The algorithm cannot proceed without a Focus Node.

### 4.1. Validation Function

The following function performs the symmetric validation logic used by the scoring algorithm.

**Function: ValidateAgainstShapes**

**Inputs:**

- `focusNode`: The node to validate (serves as the SHACL focus node)
- `targetGraph`: The RDF graph containing the focus node
- `shapes`: A list of SHACL shape IRIs to validate against
- `shapesGraph`: The RDF graph containing the shape definitions

**Output:**

- Returns `true` if all validations pass, `false` otherwise

**Logic:**

1. If `shapes` is empty, return `true`
2. For each shape IRI `S` in `shapes`:
   a. If `focusNode` does not exist in `targetGraph`, return `false`
   b. Validate `focusNode` (as SHACL focus node) against shape `S` (from `shapesGraph`) using `targetGraph` as the data graph
   c. If validation produces violations, return `false`
3. Return `true`

### 4.2. Algorithm Steps

1.  Initialize an empty list `Results`.
2.  For each instance `S` of type `shui:Score` in the Widget Scoring Graph:
    a. Let `dataGraphShapes` = list of values from `S.shui:dataGraphShape`
    b. Let `shapesGraphShapes` = list of values from `S.shui:shapesGraphShape`
    c. Let `dataValid` = ValidateAgainstShapes(**Focus Node**, **Data Graph**, `dataGraphShapes`, **Data Graph Shapes Graph**)
    d. Let `shapesValid` = ValidateAgainstShapes(**Constraint Shape**, **Shapes Graph**, `shapesGraphShapes`, **Shapes Graph Shapes Graph**)
    e. If both `dataValid` and `shapesValid` are true, record `(S.shui:widget, S.shui:score)` in `Results`
3.  Return `Results` sorted by score in descending order. When scores are equal, widgets SHOULD be sorted lexicographically by widget IRI for deterministic ordering.

**Note:** A Score is valid if both validation calls return true. When a Score has no `dataGraphShape` or `shapesGraphShape` values, the respective validation function returns true (empty shape list). The widget with the highest score is the default widget selection. If multiple `shui:Score` instances reference the same widget, ALL matching score instances are returned in `Results`. The implementation determines the default widget by selecting the widget with the highest score overall, but multiple score instances for the same widget may exist in the results.

### 4.3. Error Handling

If SHACL validation of a shape fails due to a malformed shape (not non-conformance), the implementation SHOULD log a warning and have the validation function return `false`. Shape validation errors SHOULD NOT cause the entire algorithm to fail.

If a `shui:Score` instance violates the multiplicity constraints (e.g., multiple `shui:widget` or `shui:score` values, or zero values), the implementation MUST throw an error. Malformed Score instances indicate a configuration problem that must be corrected.

## 5. Examples

The following examples illustrate the usage of the scoring model.

### 5.1. Definitions

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shui: <http://www.w3.org/ns/shacl-ui#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# A shape that matches boolean values
shui:isBoolean a sh:NodeShape ;
    sh:datatype xsd:boolean .

# A shape that matches date values
shui:isDate a sh:NodeShape ;
    sh:datatype xsd:date .

# A shape that matches date datatype constraints in shapes
shui:hasDateDatatype a sh:NodeShape ;
    sh:property [
      sh:path sh:datatype ;
      sh:in (xsd:date)
    ] .
```

### 5.2. Score Instances

```turtle
# Assign score 10 to BooleanSelectEditor if Focus Node is boolean
shui:booleanSelectEditorScore10 a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 .

# Assign score 5 to DatePickerEditor if the Constraint Shape specifies xsd:date
# This score will NOT be applicable if no Constraint Shape is provided
shui:datePickerEditorScore5 a shui:Score ;
    shui:shapesGraphShape shui:hasDateDatatype ;
    shui:widget shui:DatePickerEditor ;
    shui:score 5 .
```

## 6. Edge Cases and Special Scenarios

This section illustrates how the scoring algorithm handles various edge cases.

### 6.1. Empty Score Conditions

A `shui:Score` with no `dataGraphShape` or `shapesGraphShape` values is always valid:

```turtle
# This score is always applicable (no conditions)
shui:defaultTextEditorScore a shui:Score ;
    shui:widget shui:TextEditor ;
    shui:score 1 .
```

When validating this Score instance, step 2.b and 2.c have zero iterations, so `valid` remains `true`. The score is recorded in `Results`.

### 6.2. Missing Focus Nodes

If a Score references `shui:dataGraphShape` but the Focus Node doesn't exist in the Data Graph, that score is not applicable:

```turtle
# Will only apply if Focus Node exists and is boolean
shui:booleanScore a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 .
```

Similarly, if a Score references `shui:shapesGraphShape` but no Constraint Shape is provided (or doesn't exist in the Shapes Graph), that score is not applicable. This addresses the case where shapes graph context is unavailable.

### 6.3. Negative Scores

Negative scores are valid and can be used to deprioritize widgets:

```turtle
# Use TextEditor for literals, but deprioritize it for dates
shui:textEditorNegativeForDate a shui:Score ;
    shui:dataGraphShape shui:isDate ;
    shui:widget shui:TextEditor ;
    shui:score -5 .
```

Negative scores will appear in the results but will almost never be selected as the default (unless all scores are negative).

### 6.4. Zero Scores

A score of zero indicates a widget is not selectable:

```turtle
# BooleanSelectEditor is not selectable for non-literal values with datatype constraints
shui:booleanSelectEditorNotSelectable a shui:Score ;
    shui:dataGraphShape shui:isNotLiteral ;
    shui:shapesGraphShape shui:hasDatatype ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 0 .
```

Zero-scored widgets appear in results but are not selectable for use.

### 6.5. Multiple Scores for Same Widget

When multiple Score instances reference the same widget, ALL matching scores are returned in `Results`:

```turtle
# Score 10 if Focus Node is boolean
shui:booleanScore10 a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 .

# Score 5 if Constraint Shape has boolean datatype
shui:booleanScore5 a shui:Score ;
    shui:shapesGraphShape shui:hasBooleanDatatype ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 5 .
```

If both conditions are met, `BooleanSelectEditor` appears with both scores (10 and 5) in `Results`. The implementation determines the default widget by selecting the widget with the highest score (10 in this case). The UI implementation may choose how to handle multiple score instances for the same widget (e.g., display all scores, aggregate them, or use only the maximum).
