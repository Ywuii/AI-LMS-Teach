<template>
  <div class="chat-wrapper">
    <div class="session-sidebar">
      <div class="sidebar-header">
        <strong>会话列表</strong>
        <el-button size="small" @click="createSession">＋</el-button>
      </div>

      <ul>
        <li v-for="s in sessions" :key="s.session_id" :class="{ active: s.session_id === currentSessionId }" @click="selectSession(s.session_id)">
          <span>{{ s.title || "无标题" }}</span>
          <span class="time">{{ formatTime(s.updated_at) }}</span>
        </li>
      </ul>
    </div>
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
            <el-button :disabled="!inputMessage" @click="sendStreamMessage">发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElScrollbar, ElMessage } from "element-plus";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
import DOMPurify from "dompurify";
import { useNav } from "@/layout/hooks/useNav";
const { username } = useNav();
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
import Cookies from "js-cookie";
import { getToken } from "@/utils/auth";

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

const sessions = ref<any[]>([]);
const currentSessionId = ref<string | null>(null);

// 初始化问候语
function initGreetingMessage() {
  addMessage({ content: "您好, 我是《C语言程序设计》课程知识问答AI助手。欢迎提出问题!", isUser: false });
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
  const token = Cookies.get("authorized-token");
  const userMsg = inputMessage.value.trim();
  if (!userMsg) return;

  addMessage({ content: userMsg, isUser: true });
  inputMessage.value = "";

  addMessage({ content: "", isUser: false });
  const aiMsgIndex = messages.length - 1;

  const url = "http://localhost:8000/api/chat/stream/"; // 替换为你的 API 地址
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      question: userMsg,
      username: username.value,
      session_id: currentSessionId.value!
    })
  });

  if (!response.ok || !response.body) {
    console.error("请求失败");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE 以 \n\n 结尾
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const event of events) {
        if (!event.startsWith("data:")) continue;

        const payload = event.replace(/^data:\s*/, "");

        // ✅ 结束标志
        if (payload === "[DONE]") {
          console.log("流式响应结束");
          return;
        }

        try {
          const data = JSON.parse(payload);

          if (data.type === "token") {
            messages[aiMsgIndex].content += data.token;
          }

          if (data.type === "error") {
            console.error("后端错误:", data.content);
          }
        } catch (e) {
          console.warn("JSON 解析失败:", payload);
        }
      }
    }
  } catch (err) {
    console.error("流读取失败:", err);
  }
}

function parseAndAppend(chunk: string, aiMsgIndex: number) {
  // 简单解析 SSE 格式：data: {...}
  const lines = chunk.split("\n");
  for (const line of lines) {
    if (line.startsWith("data:")) {
      try {
        const jsonStr = line.slice(5).trim();
        if (!jsonStr) continue;
        const data = JSON.parse(jsonStr);
        if (data.token) {
          messages[aiMsgIndex].content += data.token;
          throttleScroll();
        }
      } catch (e) {
        console.error("JSON 解析失败:", e);
      }
    }
  }
}

onMounted(() => {
  fetchSessions();
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

async function fetchSessions() {
  const token = Cookies.get("authorized-token");
  const res = await fetch("/api/chat/session/", {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await res.json();
  sessions.value = data.sessions;
}

async function createSession() {
  const token = Cookies.get("authorized-token");
  const res = await fetch("/api/chat/session/create/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ title: "" })
  });
  const data = await res.json();

  sessions.value.unshift({
    session_id: data.session_id,
    title: data.title,
    updated_at: new Date().toISOString()
  });

  currentSessionId.value = data.session_id;
}

function selectSession(id: string) {
  currentSessionId.value = id;
  messages.splice(0);
  const token = getToken();
  fetch(`/api/chat/history/${id}/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(({ messages }) => {
      for (const m of messages) {
        addMessage({
          content: m.content.content ?? m.content,
          isUser: m.role === "user"
        });
      }
    });
}

function formatTime(t: string) {
  return new Date(t).toLocaleString();
}
</script>

<style scoped>
.chat-wrapper {
  display: flex;
  height: 82vh;
}

.session-sidebar {
  width: 260px;
  border-right: 1px solid #ddd;
  padding: 12px;
  background: #f7f9fb;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.session-sidebar ul {
  list-style: none;
  padding: 0;
}

.session-sidebar li {
  padding: 8px;
  cursor: pointer;
  border-radius: 6px;
}

.session-sidebar li.active {
  background-color: #e6f7ff;
}

.session-sidebar .time {
  font-size: 12px;
  color: #888;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 82vh;
  /* margin: 0 auto; */
  /* border: 1px solid #e4e4e4; */
  border-radius: 3px;
  overflow: hidden;
  --theme-color: #409eff;
  /* --bg-color: #f9f9f9; */
  background-color: var(--el-bg-color);
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
