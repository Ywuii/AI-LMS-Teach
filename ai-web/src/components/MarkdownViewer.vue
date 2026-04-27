<template>
  <div class="markdown-viewer" v-html="renderedContent" />
</template>

<script lang="ts" setup>
import { computed } from "vue";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
import DOMPurify from "dompurify";
// 引入样式
import "highlight.js/styles/github.css"; // 可以选择其他主题

// 引入高亮语言
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import python from "highlight.js/lib/languages/python";
import java from "highlight.js/lib/languages/java";
import bash from "highlight.js/lib/languages/bash";

// 注册语言
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("css", css);
hljs.registerLanguage("xml", xml);

hljs.registerLanguage("python", python);
hljs.registerLanguage("java", java);
hljs.registerLanguage("bash", bash);

const props = defineProps<{
  content: string;
}>();

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre><code class="hljs ${lang}">${
          hljs.highlight(str, {
            language: lang,
            ignoreIllegals: true
          }).value
        }</code></pre>`;
      } catch (__) {}
    }
    return "";
  }
});

const renderedContent = computed(() => {
  return DOMPurify.sanitize(md.render(props.content));
});
</script>

<style lang="scss" scoped>
.markdown-viewer {
  :deep() {
    p {
      margin: 0 0 10px 0;
    }

    ul,
    ol {
      padding-left: 20px;
      margin: 10px 0;
    }

    pre {
      background-color: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }

    code {
      font-family: monospace;
      background-color: #f5f5f5;
      padding: 2px 4px;
      border-radius: 3px;
    }

    blockquote {
      border-left: 4px solid #ddd;
      padding-left: 15px;
      margin: 10px 0;
      color: #666;
    }

    a {
      color: #409eff;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>
