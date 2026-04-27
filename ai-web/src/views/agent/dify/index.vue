<template>
  <div class="chat-container">
    <!-- 顶部标题栏 -->
    <div class="header">
      <img src="@/assets/login/logo_mini.png" alt="logo" style="height: 36px" />
    </div>

    <!-- 消息区域 -->
    <el-scrollbar ref="scrollbarRef" class="message-container">
      <div class="message-list">
        <div v-for="(message, index) in messages" :key="index" :class="['message-item', message.isUser ? 'user-message' : 'ai-message']">
          <div class="avatar" @click="copyMessage(message.content)">
            {{ message.isUser ? "👤" : "🤖" }}
          </div>
          <div class="content">
            <div v-html="renderMarkdown(message.content)" @click="copyMessage(message.content)"></div>
          </div>
        </div>
      </div>
    </el-scrollbar>

    <!-- 输入区域 -->
    <div class="input-container">
      <el-input v-model="inputMessage" placeholder="输入消息..." :disabled="loading" style="height: 50px" @keyup.enter="sendStreamMessage">
        <template #append>
          <el-button :disabled="!inputMessage || loading" @click="sendStreamMessage">发送</el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElScrollbar, ElMessage } from "element-plus";
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

// 消息类型定义
interface Message {
  content: string;
  isUser: boolean;
}

// 配置常量
const MAX_MESSAGES = 50;

// 响应式数据
const messages = reactive<Message[]>([]);
const inputMessage = ref("");
const loading = ref(false);
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>();
let conversationId = "";
let scrollTimeout: number | null = null;

// 初始化问候语
function initGreetingMessage() {
  addMessage({ content: "您好！我是您的AI助手，请问有什么可以帮您？", isUser: false });
}

// 添加消息（自动清理旧消息）
function addMessage(message: Message) {
  messages.push(message);
  if (messages.length > MAX_MESSAGES) {
    messages.shift(); // 删除最早的消息
  }
}

// 安全渲染 Markdown
function renderMarkdown(content: string): string {
  return DOMPurify.sanitize(md.render(content));
}

// 平滑滚动到底部
function scrollToBottomSmooth() {
  if (!scrollbarRef.value) return;
  nextTick(() => {
    const wrap = scrollbarRef.value.$el.querySelector(".el-scrollbar__wrap");
    if (wrap) {
      wrap.scrollTop = wrap.scrollHeight;
    }
  });
}

// 节流滚动
function throttleScroll() {
  if (scrollTimeout) return;
  scrollTimeout = setTimeout(() => {
    scrollToBottomSmooth();
    scrollTimeout = null;
  }, 50);
}

// 发送流式消息
async function sendStreamMessage() {
  const userMsg = inputMessage.value.trim();
  if (!userMsg) return;

  addMessage({ content: userMsg, isUser: true });
  inputMessage.value = "";
  loading.value = true;

  addMessage({ content: "", isUser: false });
  const aiMsgIndex = messages.length - 1;
  let aiResponse = "";

  const url = "http://localhost/v1/chat-messages";
  const headers = {
    Authorization: "Bearer app-OodhYEvNsE0GBjv2vkxncF5F",
    "Content-Type": "application/json"
  };
  const body = JSON.stringify({
    inputs: {},
    query: userMsg,
    response_mode: "streaming",
    conversation_id: conversationId,
    user: "abc-123"
  });

  let buffer = "";

  try {
    const res = await fetch(url, { method: "POST", headers, body });
    const reader = res.body?.getReader();
    if (!reader) throw new Error("无法读取响应流");

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      let eventEnd;
      while ((eventEnd = buffer.indexOf("\n\n")) >= 0) {
        const event = buffer.slice(0, eventEnd);
        buffer = buffer.slice(eventEnd + 2);
        processEvent(event, aiMsgIndex);
      }
    }

    if (buffer.trim().length > 0) {
      processEvent(buffer, aiMsgIndex);
    }

    loading.value = false;
  } catch (error) {
    console.error("请求失败:", error);
    loading.value = false;
    ElMessage.error({
      message: "网络异常，请检查后重试。",
      duration: 0,
      type: "error",
      showClose: true
    });
  }
}

// 处理事件流
function processEvent(event: string, aiMsgIndex: number) {
  const lines = event.split("\n");
  let jsonStr = "";
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      jsonStr += line.substring(6).trim();
    }
  }

  if (!jsonStr) return;

  try {
    const data = JSON.parse(jsonStr);
    if (data.event === "message") {
      if (data.answer) {
        messages[aiMsgIndex].content += data.answer;
        throttleScroll();
      }
      if (data.conversation_id) {
        conversationId = data.conversation_id;
      }
    }
  } catch (e) {
    console.error("JSON 解析错误:", e.message, "内容:", jsonStr);
  }
}

onMounted(() => {
  initGreetingMessage();
});

// 复制文本到剪贴板
async function copyMessage(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success("已复制到剪贴板");
  } catch (err) {
    console.error("复制失败:", err);
    ElMessage.error("复制失败，请重试");
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 82vh;
  margin: 0 auto;
  border: 1px solid #e4e4e4;
  border-radius: 8px;
  overflow: hidden;
  --theme-color: #409eff;
  --bg-color: #f9f9f9;
}

.header {
  padding: 5px;
  background: #f5f7fa;
  text-align: right;
  border-bottom: 1px solid #e4e4e4;
}

.message-container {
  flex: 1;
  padding: 16px;
  background: var(--bg-color);
  scroll-behavior: smooth;
}

.el-scrollbar__wrap {
  overflow-y: auto !important;
  height: 100%;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
  align-items: start;
  gap: 12px;
}

.message-item.user-message {
  flex-direction: row-reverse;
}

.message-item .avatar {
  width: 32px;
  height: 32px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item .content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.8;
  word-wrap: break-word;
  transition: opacity 0.3s ease-in-out;
}

.message-item.user-message .content {
  background: var(--theme-color);
  color: white;
  border-radius: 18px 4px 18px 18px;
}

.message-item.ai-message .content {
  background: #ffffff;
  border-radius: 4px 18px 18px 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.input-container {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e4e4e4;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 10px;
}

/* Markdown 样式 */
.message-item .content :deep(pre) {
  background-color: #fafbfd;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

.message-item .content :deep(p) {
  margin-bottom: 1em;
}

.message-item .content :deep(code) {
  font-family: "Courier New", Courier, monospace;
  background-color: transparent !important;
  padding: 0.2em 0.4em;
  font-size: 100%;
}

.message-item .content :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  color: #6a737d;
  padding: 0 1em;
  margin: 0 0 16px 0;
}

.message-item .content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.message-item .content :deep(table th),
.message-item .content :deep(table td) {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.message-item .content :deep(table tr) {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.message-item .content :deep(table tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

.message-item.ai-message .content {
  position: relative;
}

.copy-button {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.8);
  transition: opacity 0.3s ease;
}

.copy-button:hover {
  color: #333;
  background-color: rgba(255, 255, 255, 1);
}
</style>
