import MarkdownIt from "markdown-it";
import hljs from "highlight.js";

// 按需引入你需要的语言支持
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import python from "highlight.js/lib/languages/python";
import java from "highlight.js/lib/languages/java";
import bash from "highlight.js/lib/languages/bash";

// 引入样式
import "highlight.js/styles/github.css"; // 可以选择其他主题

// 注册语言
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("css", css);
hljs.registerLanguage("xml", xml);

hljs.registerLanguage("python", python);
hljs.registerLanguage("java", java);
hljs.registerLanguage("bash", bash);

export const renderMarkdown = (content: string) => {
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    highlight: (str, lang) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(str, {
            language: lang,
            ignoreIllegals: true
          }).value;
        } catch (_) {}
      }
      return "";
    }
  });

  // 安全处理和光标移除
  return md
    .render(content)
    .replace(/<a href=/g, '<a target="_blank" rel="noopener noreferrer" href=')
    .replace(/▌/g, ""); // 移除残留光标
};
