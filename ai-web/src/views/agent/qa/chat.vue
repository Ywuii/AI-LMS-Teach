<template>
  <div class="chat-container">
    <!-- 顶部标题栏 -->
    <div class="header">
      <img src="@/assets/login/logo.png" alt="logo" style="height: 36px" />
    </div>

    <!-- 消息区域 -->
    <el-scrollbar ref="scrollbarRef" class="message-container">
      <div class="message-list">
        <div v-for="(message, index) in messages" :key="index" :class="['message-item', message.isUser ? 'user-message' : 'ai-message']">
          <div class="avatar">
            {{ message.isUser ? "👤" : "🤖" }}
          </div>
          <div class="content">
            <div v-if="message.type === 'text'">
              <MarkdownViewer :content="message.content" />
            </div>
            <!-- <p v-if="message.type === 'text'">{{ message.content }}</p> -->
            <!-- 可扩展其他消息类型 -->
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">
          <el-icon :loading="true" size="20">
            <Loading />
          </el-icon>
        </div>
      </div>
    </el-scrollbar>

    <!-- 输入区域 -->
    <div class="input-container">
      <el-input v-model="inputMessage" placeholder="输入消息..." :disabled="loading" style="height: 50px" @keyup.enter="sendMessage">
        <template #append>
          <el-button :disabled="!inputMessage || loading" @click="sendMessage"> 发送 </el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watchEffect } from "vue";
import { chatWithAgent, AgentRequest, postQuestion } from "@/api/chat.ts";
import { ElScrollbar } from "element-plus";
import { Loading } from "@element-plus/icons-vue";
import MarkdownViewer from "@/components/MarkdownViewer.vue";
defineOptions({
  name: "AgentKnowledgeQA"
});

// 消息类型定义
interface Message {
  content: string;
  isUser: boolean;
  type: "text" | "image" | "audio";
}

// 响应式数据
const inputMessage = ref("");
const loading = ref(false);
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>();

const messages = reactive<Message[]>([
  {
    content: "您好, 我是《C语言程序设计》课程知识问答AI助手。欢迎提出问题!",
    isUser: false,
    type: "text"
  },
  {
    content: "什么是指针？",
    isUser: true,
    type: "text"
  },
  {
    content:
      `**指针（Pointer）** 是 C 语言中非常重要的概念，它用于存储变量的**内存地址**。

### 📌 指针的核心要点

| 概念 | 说明 |
|----|----|
| 指针本质 | 存储地址的变量 |
| 定义方式 | \`int *p;\` |
| 取地址 | \`&\` |
| 解引用 | \`*\` |

### ✅ 简单示例

下面是一个最基本的指针使用示例：

` +
      "```c" +
      `
#include <stdio.h>

int main() {
    int a = 10;
    int *p = &a;   // p 指向 a

    printf("a 的值：%d\\n", a);
    printf("p 指向的值：%d\\n", *p);

    return 0;
}
` +
      "```" +
      `

💡 **小贴士**：  
- \`p\` 存的是地址  
- \`*p\` 才是地址里的值  

如果你愿意，我也可以帮你讲 **指针与数组、指针与函数** 的关系。`,
    isUser: false,
    type: "text"
  }
]);

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    scrollbarRef.value?.handleScroll({ scrollTop: document.body.scrollHeight });
  });
};

// 去除思考模式输出
const drop_think = (text: string) => {
  return text.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return;

  // 添加用户消息
  const userMessage = {
    content: inputMessage.value,
    isUser: true,
    type: "text" as const
  };
  messages.push(userMessage);
  inputMessage.value = "";
  scrollToBottom();

  // 显示加载状态
  loading.value = true;

  // 获取AI回复
  try {
    const data: object = {
      question: userMessage.content
    };
    const response = await postQuestion(data);
    console.log(response);
    const reply = response.data;
    messages.push({
      content: reply,
      isUser: false,
      type: "text" as const
    });
  } catch (error) {
    console.error("Error:", error);
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};
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
  overflow-y: auto;
  background: #f9f9f9;
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

.message-item.user-message .avatar {
  order: 2;
}

.message-item .avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-item .content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-item.user-message .content {
  background: #409eff;
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
</style>
