<template>
  <div class="question-list">
    <div class="top">
      <el-form ref="formRef" :inline="true" :model="filterForm" class="searchform">
        <el-form-item label="知识点" prop="knowledge">
          <el-input v-model="filterForm.knowledge" placeholder="请输入知识点" clearable class="!w-[180px]" />
        </el-form-item>
        <el-form-item label="状态：" prop="type">
          <el-select v-model="filterForm.type" placeholder="请选择" clearable class="!w-[180px]">
            <el-option label="判断题" value="判断题"></el-option>
            <el-option label="单选题" value="单选题"></el-option>
            <el-option label="简答题" value="简答题"></el-option>
            <el-option label="编程题" value="编程题"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="useRenderIcon('ri:search-line')" :loading="loading" @click="onSearch"> 搜索 </el-button>
          <el-button :icon="useRenderIcon('ri:refresh-line')" @click="resetForm(formRef)"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container">
      <el-card v-for="item in questions" :key="item.id" class="question-card">
        <template #header>
          <div>
            <strong>题型：</strong>{{ item.type }}
            <el-divider direction="vertical" />
            <strong>知识点：</strong>{{ item.knowledge }}
          </div>
        </template>
        <div><strong>题目：</strong>{{ item.question }}</div>

        <!-- 单选题显示选项 -->
        <div v-if="item.type === '单选题' && item.option" style="margin-top: 10px">
          <p v-if="item.option.opt_a">A. {{ item.option.opt_a }}</p>
          <p v-if="item.option.opt_b">B. {{ item.option.opt_b }}</p>
          <p v-if="item.option.opt_c">C. {{ item.option.opt_c }}</p>
          <p v-if="item.option.opt_d">D. {{ item.option.opt_d }}</p>
        </div>

        <template #footer>
          <div v-if="item.type === '判断题' || item.type === '单选题'">
            <el-tag>答案：{{ item.answer }}</el-tag>
            <el-divider direction="vertical" />
            <strong>解析：</strong>{{ item.analysis }}
          </div>
          <div v-else>
            <strong>参考答案：</strong>{{ item.answer }}
            <el-divider />
            <strong>解析：</strong>{{ item.analysis }}
          </div>
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ref, reactive, onMounted } from "vue";
import { getExamList } from "@/api/chat";

interface Option {
  opt_a?: string;
  opt_b?: string;
  opt_c?: string;
  opt_d?: string;
  correct_answer?: string;
}

interface Question {
  id: number;
  type: string;
  knowledge: string;
  question: string;
  answer: string;
  analysis: string;
  option?: Option;
}
const loading = ref(false);
const formRef = ref(null);

const filterForm = reactive({
  type: "",
  knowledge: ""
});

const questions = ref<Question[]>([]);

const resetForm = formEl => {
  if (!formEl) return;
  formEl.resetFields();
  onSearch();
};

async function onSearch() {
  loading.value = true;
  await getExamList(filterForm).then(res => {
    questions.value = res.data;
    loading.value = false;
  });
}

onMounted(() => {
  onSearch();
});
</script>

<style scoped>
.card-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}
.question-card {
  margin-bottom: 10px;
}

.searchform {
  background-color: var(--el-bg-color);
  /* padding: 10px; */
  .el-form-item {
    margin: 10px;
  }
}
</style>
