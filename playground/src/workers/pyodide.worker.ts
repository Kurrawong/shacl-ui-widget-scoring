/// <reference lib="webworker" />

import type { ScoringRequest, ScoringResult } from "@/types/scoring";
import { focusNodeToRDFLibPython, focusNodeToN3String } from "@/lib/focusNode";

let pyodide: any = null;
let isInitialized = false;

// Initialize Pyodide
async function initPyodide() {
  if (isInitialized) return;

  try {
    // Import Pyodide
    const PyodideModule = await import("pyodide");
    pyodide = await PyodideModule.loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.29.0/full/",
    });

    // Install necessary packages
    await pyodide.loadPackage(["micropip"]);
    const micropip = pyodide.pyimport("micropip");

    // Install rdflib and pyshacl
    await micropip.install(["rdflib", "pyshacl"]);

    // Install the wheel from public folder
    // Note: Adjust the path based on your deployment setup
    await micropip.install("/pyodide/shui_widget_score-0.1.0-py3-none-any.whl");

    isInitialized = true;
    self.postMessage({ type: "initialized" });
  } catch (error) {
    self.postMessage({
      type: "error",
      error: `Failed to initialize Pyodide: ${error}`,
    });
  }
}

// Score widgets function
async function scoreWidgets(request: ScoringRequest): Promise<ScoringResult> {
  if (!pyodide || !isInitialized) {
    throw new Error("Pyodide not initialized");
  }

  // Create Python code to execute
  const pythonCode = `
from rdflib import Graph, Literal, URIRef, Namespace
from shui_widget_scoring import score_widgets

# Create graphs
widget_scoring_graph = Graph()
widget_scoring_graph.parse(data="""${
    request.widgetScoringGraph
  }""", format="turtle")

data_graph_shapes = Graph()
data_graph_shapes.parse(data="""${request.dataGraphShapes}""", format="turtle")

shapes_graph_shapes = Graph()
shapes_graph_shapes.parse(data="""${
    request.shapesGraphShapes
  }""", format="turtle")

# Parse focus node
focus_node = ${focusNodeToRDFLibPython(request.focusNode)}

# Prepare kwargs
kwargs = {
    'focus_node': focus_node,
    'widget_scoring_graph': widget_scoring_graph,
    'data_graph_shapes_graph': data_graph_shapes,
    'shapes_graph_shapes_graph': shapes_graph_shapes,
}

# Add optional parameters
${
  request.dataGraph
    ? `
data_graph = Graph()
data_graph.parse(data="""${request.dataGraph}""", format="turtle")
kwargs['data_graph'] = data_graph
`
    : ""
}

${
  request.shapesGraph
    ? `
shapes_graph = Graph()
shapes_graph.parse(data="""${request.shapesGraph}""", format="turtle")
kwargs['shapes_graph'] = shapes_graph
`
    : ""
}

${
  request.constraintShape
    ? `
kwargs['constraint_shape'] = URIRef("""${request.constraintShape}""")
`
    : ""
}

# Call score_widgets
result = score_widgets(**kwargs)

# Format results for JavaScript
# Build detailed widget scores with Score instance information
widget_scores_detailed = []
SHUI = Namespace("http://www.w3.org/ns/shacl-ui#")

for ws in result.widget_scores:
    widget_uri = str(ws.widget)
    score_value = int(ws.score)

    # Find the corresponding Score instance in the widget_scoring_graph
    score_instance_uri = None
    data_graph_shape = None
    shapes_graph_shape = None

    # Query for Score instances with matching widget and score
    for score_inst in widget_scoring_graph.subjects(SHUI.widget, URIRef(widget_uri)):
        score_obj = widget_scoring_graph.value(score_inst, SHUI.score)
        if score_obj and int(score_obj) == score_value:
            score_instance_uri = str(score_inst)
            # Get optional shapes
            dg_shape = widget_scoring_graph.value(score_inst, SHUI.dataGraphShape)
            if dg_shape:
                data_graph_shape = str(dg_shape)
            sg_shape = widget_scoring_graph.value(score_inst, SHUI.shapesGraphShape)
            if sg_shape:
                shapes_graph_shape = str(sg_shape)
            break

    score_entry = {
        'widget': widget_uri,
        'score': score_value,
        'scoreUri': score_instance_uri,
    }
    if data_graph_shape:
        score_entry['dataGraphShape'] = data_graph_shape
    if shapes_graph_shape:
        score_entry['shapesGraphShape'] = shapes_graph_shape

    widget_scores_detailed.append(score_entry)

output = {
    'widgetScores': widget_scores_detailed,
    'defaultWidget': str(result.default_widget) if result.default_widget else None,
    'defaultScore': int(result.default_score) if result.default_score else None,
    'executionSteps': [],
    'focusNode': """${focusNodeToN3String(request.focusNode)}""",
    'constraintShape': """${request.constraintShape || ""}""" or None,
}

output
`;

  try {
    const result = await pyodide.runPythonAsync(pythonCode);
    return result.toJs() as ScoringResult;
  } catch (error) {
    throw new Error(`Python execution error: ${error}`);
  }
}

// Message handler
self.onmessage = async (event: MessageEvent) => {
  const { type, payload } = event.data;

  try {
    if (type === "init") {
      await initPyodide();
    } else if (type === "score") {
      const result = await scoreWidgets(payload as ScoringRequest);
      self.postMessage({ type: "result", payload: result });
    }
  } catch (error) {
    self.postMessage({
      type: "error",
      error: String(error),
    });
  }
};

// Handle errors
self.onerror = (error) => {
  self.postMessage({
    type: "error",
    error: error.message,
  });
};
