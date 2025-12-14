# SHUI Widget Scoring Playground

A modern, interactive client-side Vue.js SPA for learning and experimenting with the SHACL UI Widget Scoring specification.

## Overview

The SHUI Widget Scoring Playground provides an educational interface to understand how the widget scoring algorithm selects appropriate UI widgets based on:

- **Data Graph Values**: RDF data containing the value node to be edited
- **SHACL Constraints**: Shape constraints that validate the value node and its context
- **Widget Scoring Rules**: SHUI Score instances that recommend widgets based on validation results

The playground runs the scoring algorithm entirely in your browser using Pyodide (Python runtime for WebAssembly).

## Features

- **Monaco Editor** for Turtle RDF editing with syntax highlighting
- **Split-pane Layout** with resizable panels for editors and results
- **3 Pre-loaded Examples** from the specification
- **Real-time Scoring** using Pyodide web worker
- **Execution Tracing** with step-by-step visualization
- **Dark Mode UI** inspired by VS Code
- **Responsive Design** that works on desktop and tablet

## Technology Stack

- **Vue 3** (Composition API) with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **Pinia** for state management
- **Monaco Editor** for RDF editing
- **Pyodide 0.29.0** for running Python in the browser
- **shadcn-vue** components (via Radix Vue)

## Project Structure

```
shui-playground/
├── src/
│   ├── components/
│   │   ├── editors/           # Monaco editor components
│   │   ├── layout/            # Main layout components
│   │   └── results/           # Results display components
│   ├── composables/           # Vue composables
│   ├── stores/                # Pinia stores
│   ├── types/                 # TypeScript type definitions
│   ├── workers/               # Web workers
│   ├── App.vue                # Root component
│   ├── main.ts                # Application entry point
│   └── style.css              # Global styles
├── public/
│   ├── examples.json          # Pre-loaded examples
│   └── pyodide/               # Python wheel package
├── scripts/
│   └── extract_examples.py    # Script to generate examples.json
└── package.json
```

## Getting Started

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

## Usage Guide

### 1. Load an Example
- Use the **Example** dropdown in the toolbar to select one of three built-in examples
- The editor panels automatically populate with the example data

### 2. Review Input Graphs
The editor panel contains five tabs:
- **Widget Scoring**: Read-only SHUI Score instances
- **Data Graph Shapes**: Read-only shapes for validating data graph values
- **Shapes Graph Shapes**: Read-only shapes for validating constraint shapes
- **Data Graph**: Editable RDF data
- **Shapes Graph**: Editable SHACL constraints

### 3. Run Scoring
Click the **Run Scoring** button to execute the algorithm. The results panel shows:
- **Recommended Widget**: The top-scoring widget with its score
- **All Widget Scores**: All evaluated widgets sorted by score
- **Execution Steps**: Step-by-step breakdown

### 4. Explore Results
Click on execution steps to see validation details and scoring explanations.

## Browser Compatibility

- Chrome/Chromium 90+
- Firefox 87+
- Safari 15+
- Edge 90+

## Troubleshooting

### Pyodide initialization timeout
- The runtime loading can be slow on slower connections
- Try clicking "Init Pyodide" explicitly
- Check browser console for detailed error messages

### TypeError: package not found
- Ensure the wheel file exists at `/public/pyodide/shui_widget_score-*.whl`
- Check browser Network tab for failed package loads

### Results not appearing
- Check the Error panel for Python execution errors
- Verify input Turtle syntax is valid
- Check browser console for JavaScript errors

## Resources

- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [Turtle RDF Format](https://www.w3.org/TR/turtle/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pyodide Documentation](https://pyodide.org/)
