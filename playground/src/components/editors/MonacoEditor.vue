<template>
  <div class="monaco-editor-container" :style="containerStyle">
    <div ref="editorContainer" class="editor-root"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useMonaco } from "@/composables/useMonaco";
import type { Monaco } from "@monaco-editor/loader";

interface Props {
  modelValue?: string;
  language?: string;
  readOnly?: boolean;
  height?: string;
  theme?: "light" | "dark";
}

interface Emits {
  (e: "update:modelValue", value: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: "",
  language: "turtle",
  readOnly: false,
  height: "400px",
  theme: "dark",
});

const emit = defineEmits<Emits>();

const editorContainer = ref<HTMLElement | null>(null);
let editor: any = null;
let monaco: Monaco | null = null;
const containerStyle = computed(() => ({ height: props.height }));

onMounted(async () => {
  const { monaco: monacoInstance } = await useMonaco();
  monaco = monacoInstance;

  if (!editorContainer.value || !monaco) return;

  const theme = props.theme === "light" ? "turtle-light" : "turtle-dark";

  editor = monaco.editor.create(editorContainer.value, {
    value: props.modelValue ?? "",
    language: props.language,
    theme,
    readOnly: props.readOnly,
    wordWrap: "on",
    fontSize: 13,
    automaticLayout: true,
  });

  // Listen to changes
  editor.onDidChangeModelContent(() => {
    emit("update:modelValue", editor.getValue());
  });
});

watch(
  () => props.modelValue,
  (newValue) => {
    if (editor && newValue !== editor.getValue()) {
      editor.setValue(newValue ?? "");
    }
  }
);

watch(
  () => props.theme,
  (newTheme) => {
    if (editor && monaco) {
      monaco.editor.setTheme(
        newTheme === "light" ? "turtle-light" : "turtle-dark"
      );
    }
  }
);

watch(
  () => props.language,
  (newLanguage) => {
    if (editor && monaco && editor.getModel()) {
      monaco.editor.setModelLanguage(editor.getModel(), newLanguage);
    }
  }
);

watch(
  () => props.readOnly,
  (isReadOnly) => {
    if (editor) {
      editor.updateOptions({ readOnly: isReadOnly });
    }
  }
);
</script>

<style scoped>
.monaco-editor-container {
  width: 100%;
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
}

.editor-root {
  width: 100%;
  height: 100%;
}
</style>
