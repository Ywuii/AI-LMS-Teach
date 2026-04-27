<template>
  <div class="agent-chat-container">
    <div class="chat-header">
      <el-tag type="info" size="large">{{ agent.description }}</el-tag>
      <el-button type="danger" size="small" :disabled="isLoading" @click="clearMessages"> 清空对话 </el-button>
    </div>

    <div ref="messagesContainer" class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" class="message-item" :class="message.role">
        <div v-if="message.role === 'assistant'" class="message-avatar">
          <el-avatar :size="40" :src="agent.icon" />
        </div>
        <div class="message-content" :class="message.role">
          <div class="message-role">
            {{ message.role === "user" ? "你" : agent.name }}
          </div>
          <div class="message-text">
            <MarkdownViewer :content="message.content" />
          </div>
        </div>
        <div v-if="message.role === 'user'" class="message-avatar">
          <el-avatar :size="40" :src="userAvatar" />
        </div>
      </div>

      <div v-if="isLoading" class="message-item assistant">
        <div class="message-avatar">
          <el-avatar :size="40" :src="agent.icon" />
        </div>
        <div class="message-content assistant">
          <div class="message-role">{{ agent.name }}</div>
          <div class="message-text">
            <div class="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <el-input v-model="inputMessage" type="textarea" :rows="3" placeholder="请输入您的问题..." :disabled="isLoading" @keyup.enter="handleSendMessage" />
      <div class="input-actions">
        <el-button type="primary" :loading="isLoading" @click="handleSendMessage"> 发送 </el-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { chatWithAgent } from "@/api/agent";
import type { Agent, Message } from "@/types/agent";
import MarkdownViewer from "@/components/MarkdownViewer.vue";

const props = defineProps<{
  agent: Agent;
}>();

const emit = defineEmits(["close"]);

const messagesContainer = ref<HTMLElement | null>(null);
const inputMessage = ref("");
const isLoading = ref(false);
const messages = ref<Message[]>([]);
const userAvatar = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";

// 初始化对话
const initConversation = () => {
  messages.value = [
    {
      role: "assistant",
      content: `我是${props.agent.name}。${props.agent.description}。欢迎提问！`,
      timestamp: Date.now()
    }
  ];
};

// 发送消息
const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userMessage = {
    role: "user" as const,
    content: inputMessage.value,
    timestamp: Date.now()
  };

  messages.value.push(userMessage);
  inputMessage.value = "";

  isLoading.value = true;

  try {
    const response = await chatWithAgent(
      {
        agentId: props.agent.id,
        messages: [
          {
            role: "system",
            content: props.agent.prompt
          },
          ...messages.value.map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        ],
        apiKey: props.agent.apiKey,
        endpoint: props.agent.endpoint
      },
      {
        onMessage: content => {
          // 查找或创建助手消息
          let assistantMessage = messages.value.findLast(msg => msg.role === "assistant" && msg.timestamp > userMessage.timestamp);

          if (!assistantMessage) {
            assistantMessage = {
              role: "assistant",
              content: "",
              timestamp: Date.now()
            };
            messages.value.push(assistantMessage);
          }

          assistantMessage.content += content;
          scrollToBottom();
        }
      }
    );

    // 确保最后一条消息是助手消息
    if (messages.value[messages.value.length - 1].role !== "assistant") {
      messages.value.push({
        role: "assistant",
        content: "",
        timestamp: Date.now()
      });
    }
  } catch (error) {
    console.error("对话出错:", error);
    ElMessage.error("对话出错，请稍后再试");
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

// 清空对话
const clearMessages = () => {
  messages.value = [];
  initConversation();
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 监听消息变化，自动滚动
watch(messages, scrollToBottom, { deep: true });

onMounted(() => {
  initConversation();
});
</script>

<style lang="scss" scoped>
.agent-chat-container {
  display: flex;
  flex-direction: column;
  height: 70vh;

  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin-bottom: 15px;

    .message-item {
      display: flex;
      margin-bottom: 20px;

      &.user {
        justify-content: flex-end;
      }

      .message-avatar {
        margin: 0 15px;
      }

      .message-content {
        max-width: 80%;

        .message-role {
          font-weight: bold;
          margin-bottom: 5px;
          color: #333;
        }

        .message-text {
          padding: 10px 15px;
          border-radius: 8px;
          line-height: 1.6;
          word-break: break-word;
        }

        &.user {
          .message-text {
            background-color: #e1f5fe;
          }
        }

        &.assistant {
          .message-text {
            background-color: #f5f5f5;
          }
        }
      }
    }

    .typing-indicator {
      display: flex;
      align-items: center;
      height: 20px;

      span {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #999;
        margin-right: 5px;
        animation: bounce 1.4s infinite ease-in-out;

        &:nth-child(1) {
          animation-delay: 0s;
        }

        &:nth-child(2) {
          animation-delay: 0.2s;
        }

        &:nth-child(3) {
          animation-delay: 0.4s;
        }
      }
    }
  }

  .chat-input {
    .input-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 10px;
    }
  }
}

@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}
</style>
