<template>
  <div class="question-bank">
    <h2>试题库</h2>

    <!-- 搜索区 -->
    <el-form :inline="true" class="search-bar">
      <el-form-item label="章节">
        <el-input v-model="filters.chapter" placeholder="请输入章节" />
      </el-form-item>

      <el-form-item label="知识点">
        <el-input v-model="filters.knowledgePoint" placeholder="请输入知识点" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="filteredQuestions" border stripe style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="60" />

      <el-table-column prop="chapter" label="章节" width="180" />

      <el-table-column prop="knowledgePoint" label="知识点" width="140" />

      <el-table-column prop="type" label="题型" width="100">
        <template #default="{ row }">
          {{ formatType(row.type) }}
        </template>
      </el-table-column>

      <el-table-column prop="question" label="题目" min-width="260" />

      <el-table-column label="选项" min-width="220">
        <template #default="{ row }">
          <ul class="option-list">
            <li v-for="(opt, i) in row.options" :key="i">{{ String.fromCharCode(65 + i) }}. {{ opt }}</li>
          </ul>
        </template>
      </el-table-column>

      <el-table-column prop="answer" label="答案" width="80" />

      <el-table-column prop="analysis" label="解析" min-width="240" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from "vue";
import { staticQuestionBank } from "./questionBank";

const visible = ref(false);
const filters = reactive({
  chapter: "",
  knowledgePoint: ""
});

const filteredQuestions = computed(() => {
  return staticQuestionBank.filter(q => {
    const matchChapter = !filters.chapter || q.chapter.includes(filters.chapter);

    const matchKnowledge = !filters.knowledgePoint || q.knowledgePoint.includes(filters.knowledgePoint);

    return matchChapter && matchKnowledge;
  });
});

function handleSearch() {
  // 已通过计算属性自动过滤
}

function handleReset() {
  filters.chapter = "";
  filters.knowledgePoint = "";
}

function formatType(type: string) {
  return type === "single_choice" ? "单选题" : type;
}
</script>

<style scoped>
.question-bank {
  padding: 20px;
}

.search-bar {
  margin-bottom: 8px;
}

.option-list {
  padding-left: 16px;
  margin: 0;
}
</style>
