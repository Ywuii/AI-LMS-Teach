<template>
  <div class="agent-list-container">
    <div class="header">
      <h3>多功能教学咨询助手</h3>
      <el-button type="success" @click="fetchAgents">刷新列表</el-button>
    </div>
    <div class="agent-grid">
      <el-card v-for="agent in agents_student" :key="agent.id" class="agent-card" shadow="hover">
        <div class="card-content">
          <div class="agent-icon">
            <img src="@/assets/login/logo_mini.png" style="height: 36px" />
          </div>
          <div class="agent-info">
            <h3>{{ agent.name }}</h3>
            <p class="description">{{ agent.description }}</p>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="openDialog(agent)"> 运行智能体 </el-button>
          </div>
        </div>
      </el-card>
    </div>
    <el-divider></el-divider>
    <div class="header">
      <h3>AI助教专家</h3>
    </div>

    <div class="agent-grid">
      <el-card v-for="agent in agents_teacher" :key="agent.id" class="agent-card" shadow="hover">
        <div class="card-content">
          <div class="agent-icon">
            <img src="@/assets/login/logo_mini.png" style="height: 36px" />
          </div>
          <div class="agent-info">
            <h3>{{ agent.name }}</h3>
            <p class="description">{{ agent.description }}</p>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="openDialog(agent)"> 运行智能体 </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <div class="header">
      <h3>知识库管理</h3>
    </div>

    <div class="agent-grid">
      <el-card class="agent-card" shadow="hover">
        <div class="card-content">
          <div class="agent-icon">
            <img src="@/assets/login/logo_mini.png" style="height: 36px" />
          </div>
          <div class="agent-info">
            <h3>测试题知识库</h3>
            <p class="description">管理与维护用于自动生成测试题的教学知识点与文档资源</p>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="goKnowledgeBase"> 进入知识库 </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 对话对话框 -->
    <el-dialog v-model="dialogVisible" :title="currentAgent?.name" width="60%" top="5vh" destroy-on-close>
      <ExamWorkFlow v-if="dialogVisible" :agent="currentAgent!" @close="dialogVisible = false" />
    </el-dialog>
  </div>
</template>
<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { getAgents } from "@/api/agent";
import type { Agent } from "@/types/agent";
import ExamWorkFlow from "./exam/index.vue";
import { useRouter } from "vue-router";
const router = useRouter();

const agents_student = ref<Agent[]>([]);
const agents_teacher = ref<Agent[]>([]);
const dialogVisible = ref(false);
const currentAgent = ref<Agent | null>(null);
const agentList_student = [
  {
    id: "agent1",
    name: "知识问答助手",
    icon: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    description: "根据《C语言程序设计》知识库进行多功能问答。",
    prompt: "你是一个测试题在线学习助手，能根据提出的专业问题进行解答",
    apiKey: "app-OodhYEvNsE0GBjv2vkxncF5F",
    endpoint: "/ai/qa"
  }
];
const agentList_teacher = [
  {
    id: "agent3",
    name: "测试题生成专家",
    icon: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    description: "根据《C语言程序设计》的知识点生成测试题。",
    prompt: "你是一个测试题自动生成专家，能根据知识点生成不同题型测试题",
    apiKey: "app-OodhYEvNsE0GBjv2vkxncF5F",
    endpoint: "/ai/exam"
  },
  {
    id: "agent4",
    name: "课程教案设计专家",
    icon: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    description: "根据《C语言程序设计》大纲设计教学方案。",
    prompt: "你是一个课程教案设计专家，能依据知识库内容辅助教师设计课程教案。",
    apiKey: "app-OodhYEvNsE0GBjv2vkxncF5F",
    endpoint: "/ai/plan"
  },
  {
    id: "agent5",
    name: "代码评测专家",
    icon: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    description: "根据《C语言程序设计》要求对代码进行评测。",
    prompt: "你是一个实践报告评阅专家，能依据实践大纲评阅学生实践报告。",
    apiKey: "app-OodhYEvNsE0GBjv2vkxncF5F",
    endpoint: "/ai/evaluation"
  }
];
const fetchAgents = async () => {
  try {
    // const response = await getAgents();
    // agents.value = response.data;
    agents_student.value = agentList_student;
    agents_teacher.value = agentList_teacher;
  } catch (error) {
    console.error("获取智能体列表失败:", error);
  }
};

const openDialog = (agent: Agent) => {
  // currentAgent.value = agent;
  // dialogVisible.value = true;
  router.push(agent.endpoint);
};

onMounted(() => {
  fetchAgents();
});
</script>
<style lang="scss" scoped>
.agent-list-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    margin-top: 20px;
  }

  .agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .agent-card {
    height: 100%;
    transition: transform 0.3s;

    &:hover {
      transform: translateY(-5px);
    }

    .card-content {
      display: flex;
      flex-direction: column;
      height: 100%;

      .agent-icon {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
      }

      .agent-info {
        flex: 1;

        h3 {
          margin: 0 0 10px 0;
          font-size: 18px;
          text-align: center;
        }

        .description {
          margin: 0;
          color: #666;
          font-size: 14px;
          line-height: 1.5;
        }
      }

      .card-footer {
        display: flex;
        justify-content: center;
        margin-top: 15px;
      }
    }
  }
}
</style>
