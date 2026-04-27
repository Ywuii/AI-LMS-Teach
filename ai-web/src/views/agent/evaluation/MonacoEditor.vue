<!-- components/MonacoEditor.vue -->
<template>
  <div ref="container" style="height: 100%"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import * as monaco from "monaco-editor";

const props = defineProps<{
  value: string;
  language?: string;
  theme?: string;
  height?: string;
}>();

const emit = defineEmits(["update:value"]);
const container = ref<HTMLElement>();

let editor: monaco.editor.IStandaloneCodeEditor;

onMounted(() => {
  editor = monaco.editor.create(container.value!, {
    value: props.value,
    language: props.language || "c",
    theme: props.theme || "vs-dark",
    automaticLayout: true
  });

  editor.onDidChangeModelContent(() => {
    emit("update:value", editor.getValue());
  });
});

watch(
  () => props.value,
  val => {
    if (val !== editor.getValue()) {
      editor.setValue(val);
    }
  }
);
</script>
