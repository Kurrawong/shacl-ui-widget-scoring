

## Example

SHACL Renderer UI widget shapes:

## Named graph: `shui:dataGraphShapes`

This graph contains shapes for the SHACL data graph.

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shui: <http://www.w3.org/ns/shui#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

shui:isBoolean a sh:NodeShape ;
    sh:datatype xsd:boolean ;
.

shui:isDate a sh:NodeShape ;
    sh:datatype xsd:date ;
.

shui:isNotLiteral a sh:NodeShape ;
    sh:nodeKind (sh:BlankNode sh:IRI sh:TripleTerm) ;
.
```

## Named graph: `shui:shapesGraphShapes`

This graph contains the shapes for the SHACL shapes graph.

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shui: <http://www.w3.org/ns/shui#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

shui:hasDatatype a sh:NodeShape ;
    sh:property [
      sh:path sh:datatype ;
      sh:minCount 1
    ] ;
.

shui:hasDateDatatype a sh:NodeShape ;
    sh:property [
      sh:path sh:datatype ;
      sh:in (xsd:date)
    ] ;
.
  
shui:literalNoDatatypeSpecified a sh:NodeShape ;
    # The shape must have a sh:nodeKind constraint with the sh:Literal value.
    # This is perhaps too strict?
    sh:property [
      sh:path sh:nodeKind ;
      sh:hasValue sh:Literal ;
    ] ;
    
    # The shape must not have the sh:datatype constraint.
    sh:property [
      sh:path sh:datatype ;
      sh:maxCount 0
    ] ;
.
```

## Named graph: `shui:widgetScores`

This graph contains the widget scores used by the widget scoring algorithm.

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shui: <http://www.w3.org/ns/shui#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

#
# shui:BooleanSelectEditor
#
shui:booleanSelectEditorScore10 a shui:Score ;
    shui:dataGraphShape shui:isBoolean ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 10 ;
.

shui:booleanSelectEditorScore0 a shui:Score ;
    shui:dataGraphShape shui:isNotLiteral ;
    shui:shapesGraphShape shui:hasDatatype ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 0 ;
.
  
shui:booleanSelectEditorScoreNull a shui:Score ;
    shui:shapesGraphShape shui:literalNoDatatypeSpecified ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score -1 ;
.
  
#
# shui:DatePickerEditor
#
shui:datePickerEditorScore10 a shui:Score ;
    shui:dataGraphShape shui:isDate ;
    shui:widget shui:DatePickerEditor ;
    shui:score 10 ;
.

shui:datePickerEditorScore5 a shui:Score ;
    shui:shapesGraphShape shui:hasDateDatatype ;
    shui:widget shui:DatePickerEditor ;
    shui:score 5 ;
.
```

## Example 1 with a data graph

The following data graph describes a person who is an admin in the system.

```turtle
PREFIX ex: <https://example.com/>
PREFIX schema: <https://schema.org/>

ex:user-a a schema:Person ;
    ex:isAdmin true ;
.
```

With the data graph and no shapes graph, A SHACL Renderer iterates through the `shui:Score` instances in the `shui:widgetScores` graph and returns a list of applicable widgets ordered by `shui:score`.

Result:

```json
[
  "shui:booleanSelectEditorScore10": {
    "shui:widget": "shui:BooleanSelectEditor",
    "shui:score": 10
  },
  "shui:booleanSelectEditorScoreNull": {
    "shui:widget": "shui:BooleanSelectEditor",
    "shui:score": -1
  }
]
```

### Example 2 with a data graph and shapes graph

Here's an example where the data graph is the same but a shapes graph is provided and constrains the value to a non-literal.

Shapes graph:

```turtle
PREFIX ex: <https://example.com/>
PREFIX sh: <http://www.w3.org/ns/shacl#>

ex:Person-isAdmin a sh:NodeShape ;
  sh:targetClass schema:Person ;
  sh:property [
    sh:path ex:isAdmin ;
    sh:nodeKind (sh:BlankNode sh:IRI sh:TripleTerm)
  ]
.
```
Results:

```json
[
  "shui:booleanSelectEditorScore10": {
    "shui:widget": "shui:BooleanSelectEditor",
    "shui:score": 10
  },
  "shui:booleanSelectEditorScore0": {
    "shui:widget": "shui:BooleanSelectEditor",
    "shui:score": 0
  }
]
```

### Example 3 with a data graph and a shapes graph

Here, the data graph remains the same but the shapes graph contains a shape that only allows literal date values.

Shapes graph:

```turtle
PREFIX ex: <https://example.com/>
PREFIX sh: <http://www.w3.org/ns/shacl#>

ex:Person-isAdmin a sh:NodeShape ;
  sh:targetClass schema:Person ;
  sh:property [
    sh:path ex:isAdmin ;
    sh:datatype xsd:date
  ]
.
```

Result:

```json
[
  "shui:booleanSelectEditorScore10": {
    "shui:widget": "shui:BooleanSelectEditor",
    "shui:score": 10
  },
  "shui:datePickerEditorScore5": {
    "shui:widget": "shui:DatePickerEditor",
    "shui:score": 5
  }
]
```

### Question 1
Do we need to differentiate `shui:Score` instances between OR and AND? For example, `shui:booleanSelectEditorScore0` should be an OR since it should return the score of 0 when either the `shui:scoreDataShape` or `shui:scoreGraphShape` matches.

From the original DASH widget description of the 0 case: _"0 for non-literals or if there is a `sh:datatype` constraint"_.

Will we need score classes like `shui:ScoreAND` and `shui:ScoreOR`?

#### Answer
A `shui:Score` is valid if all linked shapes raise no violations. If a disjunction is required, separate the two shapes into two separate `shui:Score` instances.

### Alternate Syntax Proposal

```turtle
shui:booleanSelectEditorScore0 a shui:Score ;
    shui:shape [
        shui:graph shui:DataGraph ;
        shui:shape shui:isNotLiteral
    ], [
        shui:graph shui:ShapesGraph ;
        shui:shape shui:hasDatatype
    ]
    shui:widget shui:BooleanSelectEditor ;
    shui:score 0 ;
.
```

```turtle
shui:booleanSelectEditorScore0 a shui:Score ;
    shui:shape shui:isNotLiteral {| shui:graph shui:DataGraph |} ;
    shui:shape shui:hasDatatype {| shui:graph shui:ShapesGraph |} ;
    shui:widget shui:BooleanSelectEditor ;
    shui:score 0 ;
.
```