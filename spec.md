# SHACL UI Widget Scoring

## Abstract

This document defines the SHACL UI Widget Scoring ontology and algorithm. It provides a mechanism to associate UI widgets with SHACL shapes and data values based on a scoring system, enabling dynamic selection of the most appropriate widget for a given user interface context.

## Status of This Document

This document is a draft specification for the SHACL UI Community Group.

## 1. Introduction

When automatically generating user interfaces from data models, it is often necessary to determine the most suitable user interface "widget" (e.g., a text input, a date picker, a checkbox) for a given value or constraint. SHACL (Shapes Constraint Language) provides a powerful way to describe data constraints. This specification extends the SHACL ecosystem by defining a scoring mechanism to select widgets based on both the data being edited and the SHACL shapes constraining that data.

The goal is to allow developers to define rules such as:
*   "Use a DatePicker if the value is a date."
*   "Use a BooleanSelect if the value is a boolean."
*   "Prefer a specific editor if a specific SHACL facet (like `sh:in`) is present."

## 2. Terminology

The keywords **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC2119].

<dl>
  <dt>Data Graph</dt>
  <dd>The RDF graph containing the data being viewed or edited.</dd>
  <dt>Shapes Graph</dt>
  <dd>The RDF graph containing the SHACL shapes that constrain the Data Graph.</dd>
  <dt>Widget Scoring Graph</dt>
  <dd>An RDF graph containing <code>shui:Score</code> instances that define the mapping rules.</dd>
  <dt>Value Node</dt>
  <dd>A node in the Data Graph being validated. In SHACL, a value node can also serve as a focus node for validation purposes.</dd>
  <dt>Constraint Shape</dt>
  <dd>A SHACL shape node (<code>sh:NodeShape</code> or <code>sh:PropertyShape</code>) in the Shapes Graph that constrains the Value Node. Both node shapes and property shapes are valid constraint shapes.</dd>
</dl>

## 3. The Widget Scoring Model

The Widget Scoring Model relies on instances of the class `shui:Score` to define rules for scoring widgets.

### 3.1. Namespace

The namespace for this ontology is `http://www.w3.org/ns/shui#`. The prefix `shui` is used throughout this document.

### 3.2. Class: shui:Score

A `shui:Score` instance represents a rule that assigns a numeric score to a specific widget type if certain conditions are met.

### 3.3. Properties

The following properties are used to define a `shui:Score` instance.

#### 3.3.1. shui:widget

*   **Domain**: `shui:Score`
*   **Range**: `rdfs:Class` (or a specific Widget class)
*   **Multiplicity**: Exactly one (1).

Reference to the identifier of the widget (e.g., `shui:BooleanSelectEditor`).

#### 3.3.2. shui:score

*   **Domain**: `shui:Score`
*   **Range**: `xsd:decimal` or `xsd:integer`
*   **Multiplicity**: Exactly one (1).

The numeric score assigned to the widget if the conditions are met. Scores MUST be positive, zero, or negative decimals/integers. The widget with the highest positive score is the default selection. Positive scores indicate selectable widget choices. A score of zero indicates the widget is not selectable at all. Negative scores are valid but will almost never be selected as the default widget.

Score comparisons SHOULD use the precision provided in the RDF literal. Implementations MUST use consistent decimal comparison (not floating-point approximation).

#### 3.3.3. shui:dataGraphShape

*   **Domain**: `shui:Score`
*   **Range**: `sh:Shape`
*   **Multiplicity**: Zero or more.

Links to a SHACL shape that validates the **Value Node** in the **Data Graph**. If the Value Node conforms to this shape, the condition is satisfied.

#### 3.3.4. shui:shapesGraphShape

*   **Domain**: `shui:Score`
*   **Range**: `sh:Shape`
*   **Multiplicity**: Zero or more.

Links to a SHACL shape that validates the **Constraint Shape** in the **Shapes Graph**. This allows scoring based on the definition of the shape itself (e.g., "does the shape have a `sh:datatype` constraint?").

### 3.4. SHACL Feature Support

The shapes referenced by `shui:dataGraphShape` and `shui:shapesGraphShape` MAY use any SHACL Core features, including sh:and, sh:or, sh:not, and nested shapes. Support for SHACL-SPARQL constraints is OPTIONAL and implementation-dependent.

Recursive or circular shape references are handled according to the SHACL validator's specification. Implementations MUST NOT enter infinite loops.

## 4. Scoring Algorithm

The input to the scoring algorithm is:
1.  **Value Node**: The node in the Data Graph being validated.
2.  **Constraint Shape** (Optional): The shape node in the Shapes Graph that constrains the Value Node.
3.  **Widget Scoring Graph**: The graph containing `shui:Score` instances.

The output is a list of widgets with their calculated scores.

The scoring algorithm validates the **Value Node** against `dataGraphShape` constraints and validates the **Constraint Shape** against `shapesGraphShape` constraints.

**Note**: If a Value Node conforms to multiple Property Shapes, the algorithm SHOULD be invoked separately for each Property Shape to determine the appropriate widget for each property.

### Prerequisites

The Value Node MUST exist in the Data Graph. If the Value Node is undefined or malformed, the algorithm returns an empty list.

### Algorithm Steps

1.  Initialize an empty list `Results`.
2.  For each instance `S` of type `shui:Score` in the Widget Scoring Graph:
    a.  Initialize `valid` = true
    b.  For each value `DGS` of `S.shui:dataGraphShape`:
        i.  Validate the **Value Node** against the SHACL shape `DGS`
        ii. If validation produces violations, set `valid` = false and break
    c.  For each value `SGS` of `S.shui:shapesGraphShape`:
        i.  Validate the **Constraint Shape** (as the focus node) against the SHACL shape `SGS` (using the Shapes Graph as data)
        ii. If validation produces violations, set `valid` = false and break
    d.  If `valid` is true (including when S has zero shape constraints), record `(S.shui:widget, S.shui:score)` in `Results`
3.  Return `Results` sorted by score in descending order. When scores are equal, widgets SHOULD be sorted lexicographically by widget IRI for deterministic ordering.

**Note:** A Score is valid if no linked shapes produce violations. An S may have zero or more `dataGraphShape` or `shapesGraphShape` values. The widget with the highest score is the default widget selection. If multiple `shui:Score` instances reference the same widget, the maximum score for that widget determines its position in the sorted results. Implementations MUST return the highest-scoring widget as the default, but MAY also provide other widgets with valid scores (including zero or negative) as alternative options.

### 4.1. Error Handling

If SHACL validation of a shape fails due to a malformed shape (not non-conformance), the implementation SHOULD log a warning and treat the Score instance as not applicable. Shape validation errors SHOULD NOT cause the entire algorithm to fail.

If a `shui:Score` instance violates the multiplicity constraints (e.g., multiple `shui:widget` or `shui:score` values, or zero values), the implementation MUST throw an error. Malformed Score instances indicate a configuration problem that must be corrected.

## 5. Examples

The following examples illustrate the usage of the scoring model.

### 5.1. Definitions

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shui: <http://www.w3.org/ns/shui#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# A shape that matches boolean values in the data graph
shui:isBoolean a sh:NodeShape ;
    sh:datatype xsd:boolean .

# A shape that matches date values in the data graph
shui:isDate a sh:NodeShape ;
    sh:datatype xsd:date .

# A shape that matches date datatype constraints in the shapes graph
shui:hasDateDatatype a sh:NodeShape ;
    sh:property [
      sh:path sh:datatype ;
      sh:in (xsd:date)
    ] .
```

### 5.2. Score Instances

```turtle
# Assign score 10 to BooleanSelectEditor if data is boolean
shui:booleanSelectEditorScore10 a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 .

# Assign score 5 to DatePickerEditor if the constraint shape specifies xsd:date
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

### 6.2. Negative Scores

Negative scores are valid and can be used to deprioritize widgets:

```turtle
# Use TextEditor for literals, but deprioritize it for dates
shui:textEditorNegativeForDate a shui:Score ;
    shui:dataGraphShape shui:isDate ;
    shui:widget shui:TextEditor ;
    shui:score -5 .
```

Negative scores will appear in the results but will almost never be selected as the default (unless all scores are negative).

### 6.3. Zero Scores

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

### 6.4. Multiple Scores for Same Widget

When multiple Score instances reference the same widget, the maximum score determines precedence:

```turtle
# Score 10 if value is boolean
shui:booleanScore10 a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 .

# Score 5 if shape has boolean datatype
shui:booleanScore5 a shui:Score ;
    shui:shapesGraphShape shui:hasBooleanDatatype ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 5 .
```

If both conditions are met, `BooleanSelectEditor` appears with both scores in `Results`, but the implementation uses the maximum (10) for determining the default widget.

### 6.5. Missing Constraint Shape with shapesGraphShape

If a Score has `shapesGraphShape` values but no Constraint Shape is provided to the algorithm, the validation cannot be performed:

```turtle
# This score requires checking the constraint shape
shui:datePickerForDateConstraint a shui:Score ;
    shui:shapesGraphShape shui:hasDateDatatype ;
    shui:widget shui:DatePickerEditor ;
    shui:score 5 .
```

If the algorithm is invoked without a Constraint Shape, attempting to validate against `shapesGraphShape` will fail because there is no Constraint Shape node to validate. Implementations SHOULD handle this gracefully (e.g., treat as a validation failure, making the Score not applicable).
