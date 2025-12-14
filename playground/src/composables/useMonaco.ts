import loader from '@monaco-editor/loader'
import type { Monaco } from '@monaco-editor/loader'

let monaco: Monaco | null = null

export async function useMonaco() {
  if (!monaco) {
    monaco = await loader.init()
  }

  // Define Turtle language
  if (monaco && !monaco.languages.getEncodedLanguageId('turtle')) {
    monaco.languages.register({ id: 'turtle' })
    monaco.languages.setMonarchTokensProvider('turtle', getTurtleTokens())
    monaco.editor.defineTheme('turtle-light', getTurtleLightTheme())
    monaco.editor.defineTheme('turtle-dark', getTurtleDarkTheme())
  }

  return { monaco }
}

function getTurtleTokens() {
  return {
    tokenizer: {
      root: [
        [/^@(prefix|base)/, 'keyword', '@prefix'],
        [/[a-zA-Z_][a-zA-Z0-9_]*(?=\s*:)/, 'variable'],
        [/<[^>]*>/, 'string'],
        [/"(?:\\.|[^"\\])*"/, 'string'],
        [/'(?:\\.|[^'\\])*'/, 'string'],
        [/#.*$/, 'comment'],
        [/\b(true|false)\b/, 'keyword'],
        [/[0-9]+(?:\.[0-9]+)?/, 'number'],
        [/[a-zA-Z][a-zA-Z0-9_.-]*:[a-zA-Z0-9_.-]*/, 'variable.name'],
        [/[{}()\[\];,.]/, 'delimiter'],
        [/\s+/, 'whitespace'],
      ],
    },
  }
}

function getTurtleLightTheme() {
  return {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '0000FF' },
      { token: 'variable', foreground: '008000' },
      { token: 'string', foreground: 'A31515' },
      { token: 'comment', foreground: '008000', fontStyle: 'italic' },
      { token: 'number', foreground: '098658' },
      { token: 'variable.name', foreground: '008000', fontStyle: 'bold' },
    ],
  }
}

function getTurtleDarkTheme() {
  return {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '569CD6' },
      { token: 'variable', foreground: '4EC9B0' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'variable.name', foreground: '4EC9B0', fontStyle: 'bold' },
    ],
  }
}
