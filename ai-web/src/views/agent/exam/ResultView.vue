<template>
  <div class="result-view">
    <!-- 按钮区域 -->
    <div class="action-buttons">
      <el-button type="primary" @click="showPromptDialog">查看提示词</el-button>
      <el-button type="success" @click="generateTestQuestions">生成测试题</el-button>
      <el-button type="warning" @click="viewThink">查看推理过程</el-button>
    </div>

    <!-- 提示词弹窗 -->
    <el-dialog v-model="promptVisible" title="当前提示词内容" width="35%">
      <pre class="prompt-content">{{ prompt }}</pre>
    </el-dialog>

    <!-- 推理过程弹窗 -->
    <el-dialog v-model="thinkVisible" title="推理过程" width="60%">
      <pre class="prompt-content">{{ think }}</pre>
    </el-dialog>

    <!-- 加载提示 -->

    <div v-if="questions.length === 0 && !loading" class="empty-result">暂无生成的测试题</div>
    <div v-if="loading" class="loading-message">正在AI推理生成，请耐心等待......</div>

    <div v-else v-for="(q, index) in questions" :key="index" class="question-card">
      <h4>题目 {{ index + 1 }}</h4>
      <p><strong>问题：</strong>{{ q.question }}</p>

      <div v-if="q.options.length > 0">
        <p><strong>选项：</strong></p>
        <ul>
          <li v-for="(opt, i) in q.options" :key="i">{{ opt }}</li>
        </ul>
      </div>

      <p v-if="q.answer"><strong>参考答案：</strong>{{ q.answer }}</p>
      <p v-if="q.analysis"><strong>解析：</strong>{{ q.analysis }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from "vue";
import { ElMessage, ElButton, ElDialog } from "element-plus";
import { postExam } from "@/api/chat.ts";
import type { Question, QuestionGenConfig } from "./types";
interface QuestionGenParams {
  chapter: string;
  knowledge_point: string;
  question_type: string;
  question_count: number;
  difficulty: string;
  use_kg: boolean;
  use_rag: boolean;
  include_answer: boolean;
  include_explanation: boolean;
  custom_key: string;
  custom_value: string;
}
const targetData = ref<QuestionGenConfig | null>(null);
const requirementData = ref<any>(null);

const resultParams = computed<QuestionGenParams | null>(() => {
  const t = targetData.value;
  const r = requirementData.value;

  if (!t || !r) return null;

  return {
    chapter: t.chapter?.label ?? "",
    knowledge_point: t.knowledge_point,
    question_type: t.question_type,
    question_count: t.question_count,
    difficulty: t.difficulty,

    use_kg: r.useKnowledgeGraph,
    use_rag: r.useRag,
    include_answer: r.includeAnswer,
    include_explanation: r.includeAnalysis,
    custom_key: r.customRequirementKey,
    custom_value: r.customRequirementValue
  };
});

const props = defineProps<{
  params: QuestionGenParams;
}>();

const emit = defineEmits<{
  (e: "update-questions", questions: Question[]): void;
}>();

// 控制提示词对话框显示
const promptVisible = ref(false);

// 测试题数据
const questions = ref<Question[]>([]);

const loading = ref(false);

// 测试题格式转换
function parseQuestions(text) {
  // 按照【题目】拆分原始文本为多个题块
  const blocks = text.trim().split("【题目】").filter(Boolean);

  return blocks.map(block => {
    // 提取题目
    const questionMatch = block.match(/^(.+?)\s*(?:【选项】|【答案】)/s);
    const question = questionMatch ? questionMatch[1].trim() : "";

    // 判断是否是选择题
    const isMultipleChoice = /【选项】/.test(block);

    let options = [];
    if (isMultipleChoice) {
      // 提取选项
      const optionsMatch = block.match(/【选项】([\s\S]+?)(?=【答案】)/);
      if (optionsMatch) {
        const optsText = optionsMatch[1];
        // 去掉编号，提取纯文本
        options = optsText
          .trim()
          .split(/\s*[A-D]\./)
          .slice(1); // 跳过第一个空项
      }
    }

    // 提取答案
    const answerMatch = block.match(/【答案】([^\n\r【】]*)/);
    const answer = answerMatch ? answerMatch[1].trim() : "";

    // 提取解析
    const analysisMatch = block.match(/【解析】([\s\S]+)/);
    const analysis = analysisMatch ? analysisMatch[1].trim() : "";

    return {
      question,
      options,
      answer,
      analysis
    };
  });
}

// 显示提示词弹窗
function showPromptDialog() {
  if (props.prompt.trim()) {
    promptVisible.value = true;
  } else {
    ElMessage.warning("当前提示词为空，请先填写任务目标和要求");
  }
}

const thinkVisible = ref(false);
const think = ref("");
// 显示推理过程弹窗
function viewThink() {
  if (props.prompt.trim()) {
    if (questions.value.length > 0) {
      thinkVisible.value = true;
    } else {
      ElMessage.warning("当前暂不支持查看推理过程, 请先生成测试题");
    }
  } else {
    ElMessage.warning("当前提示词为空，请先填写任务目标和要求");
  }
}

// 模拟生成测试题（可替换为真实 API 调用）
const generateTestQuestions = async () => {
  loading.value = true;
  questions.value = [];

  try {
    const response = await postExam(props.params);

    console.log("response:", response);

    // ✅ response 本身就是 ExamResponse
    const result = response;

    if (!result || !Array.isArray(result.questions)) {
      console.log("返回数据格式不正确");
      return;
    }

    questions.value = result.questions;
    console.log("✅ questions:", questions.value);

    emit("update-questions", result.questions);
  } catch (err) {
    console.error(err);
    ElMessage.error("生成测试题失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.result-view {
  max-height: 600px;
  overflow-y: auto;
}

.action-buttons {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.prompt-content {
  white-space: pre-wrap;
  word-break: break-word;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  font-family: monospace;
  color: #333;
}

.question-card {
  border: 1px solid #ebeef5;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 6px;
}

.empty-result {
  color: #999;
  text-align: center;
  font-size: 14px;
}

.loading-message {
  font-size: 16px;
  color: #b50909;
  margin-left: 10px;
  text-align: center;
  font-style: italic;
}
</style>
