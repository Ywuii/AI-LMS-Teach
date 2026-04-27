<script setup lang="ts">
import { ref, onMounted } from "vue";
defineOptions({
  name: "ProjectIntroduction"
});
import TeamMemberCard from "@/components/TeamMemberCard.vue";

// 功能亮点数据
const features = [
  { title: "大语言模型", description: "QWen3-4B模型、DeepSeek R1" },
  { title: "词嵌入模型", description: "text2vec-base-chinese、BGE-M3" },
  { title: "RAG工作流编排", description: "LangChain及工具箱家族、Dify" },
  { title: "知识图谱", description: "SpaCy、zh_core_web_trf、Neo4j" },
  { title: "后端开发框架", description: "Django+DRF+Mysql+Redis" },
  { title: "前端开发框架", description: "Vue3+TypeScript+Element-Plus+axios" }
];

const img = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";
// 团队成员数据
const teamMembers = ref([
  { name: "黄圣祺", role: "队长 | 后端开发", avatar: img },
  { name: "林宇", role: "前端开发", avatar: img },
  { name: "邓翰宁", role: "系统测试", avatar: img },
  { name: "邓成剑", role: "指导老师", avatar: img }
]);

onMounted(() => {});
</script>

<template>
  <div>
    <el-row :gutter="20">
      <!-- 项目简介 -->
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>智慧学习管理系统 AI-LMS</h2>
            </div>
          </template>
          <p>2025年第14届软件杯 ｜ A7赛道-基于开源AI大模型的教学实训智能体软件 ｜ 华南农业大学 参赛作品</p>
          <p>本系统为基于开源AI大模型RAG+知识图谱教学实训智能体，采用Django+Langchain+Vue3开发</p>
          <!-- <p><strong>教师端: </strong>根据教学大纲和知识库自动生成教案、测试题等</p>
          <p><strong>学生端: </strong>专业知识问答, 根据练习情况生成练习题</p>
          <p><strong>管理端: </strong>课程资源管理, 学情统计, 大屏数据仪表盘</p> -->
        </el-card>
      </el-col>

      <!-- 功能亮点 -->
      <el-col :span="24" style="margin-top: 10px">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>开发技术栈</h2>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col v-for="(feature, index) in features" :key="index" :span="8">
              <el-card shadow="hover" style="margin-bottom: 10px">
                <strong>{{ feature.title }}</strong>
                <p>{{ feature.description }}</p>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 团队成员 -->
      <el-col :span="24" style="margin-top: 10px">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>团队成员</h2>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col v-for="member in teamMembers" :key="member.name" :span="6">
              <team-member-card :member="member" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<style scoped></style>
