<template>
  <div class="agent-chat-container">
    <div class="chat-header">
      <el-tag type="info" size="large">{{ agent.description }}</el-tag>
      <el-button type="danger" size="small" :disabled="isCompleted" @click="viewThink"> 查看推理过程 </el-button>
    </div>

    <el-card style="max-width: 100%; height: 100%">
      <template #header>
        <div class="card-header">
          <el-steps style="max-width: 100%" :active="active" align-center finish-status="success">
            <el-step title="任务目标" />
            <el-step title="任务要求" />
            <el-step title="输出结果" />
            <el-step title="MCP操作" />
          </el-steps>
        </div>
      </template>
      <div class="card-body">
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
          <el-tab-pane label="任务目标" name="tab0">明确任务目标，如确定知识点范围、出题类型、数量等</el-tab-pane>
          <el-tab-pane label="任务要求" name="tab1">提出任务要求：比如判断题给出答案解析，回答要求编写代码等等、输出格式为json或markdown等</el-tab-pane>
          <el-tab-pane label="输出结果" name="tab2">输出结果：展示智能体推理结果</el-tab-pane>
          <el-tab-pane label="MCP操作" name="tab3">MCP操作：对输出结果进一步处理，如将测试题存入数据库、教案导出word等等</el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <div class="card-footer">
          <el-button style="margin-top: 12px" type="primary" @click="pre" :disabled="active === 0">上一步</el-button>
          <el-button style="margin-top: 12px" type="success" @click="next" :disabled="active === 3">下一步</el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { chatWithAgent } from "@/api/agent";
import type { Agent, Message } from "@/types/agent";
import MarkdownViewer from "@/components/MarkdownViewer.vue";
import type { TabsPaneContext } from "element-plus";
import TargetView from "./TargetView.vue";
import RequirementView from "./RequirementView.vue";
import ResultView from "./ResultView.vue";
import McpView from "./McpView.vue";

const props = defineProps<{
  agent: Agent;
}>();

const emit = defineEmits(["close"]);

const messagesContainer = ref<HTMLElement | null>(null);
const inputMessage = ref("");
const isCompleted = ref(true);
const messages = ref<Message[]>([]);
const userAvatar = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";

const active = ref(0);
const activeName = ref("tab0");
const next = () => {
  if (active.value++ > 3) active.value = 0;
  activeName.value = "tab" + active.value;
  if (active.value === 3) {
    isCompleted.value = false;
  }
};
const pre = () => {
  if (active.value-- < 0) active.value = 0;
  activeName.value = "tab" + active.value;
};

const handleClick = (tab: TabsPaneContext, event: Event) => {
  active.value = Number(tab.index);
};

const viewThink = () => {};
// 初始化对话
const initConversation = () => {
  messages.value = [
    {
      role: "assistant",
      content: `我是${props.agent.name}。我能${props.agent.description}，欢迎提问！`,
      timestamp: Date.now()
    }
  ];
};

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

  .card-body {
    height: calc(100vh - 550px);
  }

  .card-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  .demo-tabs > .el-tabs__content {
    padding: 32px;
    color: #6b778c;
    font-size: 32px;
    font-weight: 600;
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
