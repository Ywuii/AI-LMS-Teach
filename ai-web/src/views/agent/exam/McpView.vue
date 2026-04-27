<template>
  <div class="mcp-view">
    <!-- 按钮组 -->
    <div class="action-buttons">
      <el-button type="primary" @click="persistData">持久化到数据库</el-button>
      <el-button type="success" @click="startOnlineExam">在线考试</el-button>
      <el-button type="warning" @click="exportToPDF">导出试卷</el-button>
    </div>

    <!-- PDF 内容容器 -->
    <div id="pdf-content" style="display: none">
      <h1>练习题报告</h1>
      <div v-for="(q, index) in shuffledQuestions" :key="index" class="pdf-question">
        <h3>题目 {{ index + 1 }}：{{ q.question }}</h3>

        <!-- 选择题 -->
        <div v-if="q.options && q.options.length > 0">
          <p><strong>选项：</strong></p>
          <ul>
            <li v-for="(opt, i) in q.options" :key="i">{{ String.fromCharCode(65 + i) }}. {{ opt.value }}</li>
          </ul>
        </div>
        <p><strong>你的回答：</strong> {{ userAnswers[index] || "未作答" }}</p>
        <p><strong>正确答案：</strong> {{ getOriginalAnswer(q.answer, q.options) }}</p>
        <p><strong>解析：</strong> {{ q.analysis }}</p>
        <hr />
      </div>
    </div>

    <!-- 在线考试对话框 -->
    <OnlineExerciseDialog v-model="showExerciseDialog" :questions="mockQuestions" @submit="handleSubmitAnswers" />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, computed } from "vue";
import { ElMessage, ElButton } from "element-plus";
import html2pdf from "html2pdf.js";
import OnlineExerciseDialog from "./OnlineExerciseDialog.vue";
import type { Question, ShuffledQuestion, Option, Exam } from "./types";
import { postExamQuestions } from "@/api/chat";
import { log } from "console";
const props = defineProps<{
  questions: Question[];
  questionType: string;
  knowledge: string;
}>();
const mockQuestions = computed(() => props.questions);
const qtype = computed(() => props.questionType);
const knowledge_select = computed(() => props.knowledge);
// 状态管理
const showExerciseDialog = ref(false);
const userAnswers = ref<Record<number, string>>({});
const shuffledQuestions = ref([]);
const correctCount = ref<number>(0);
const questions = ref<Exam[]>([]);

// 持久化到数据库
const persistData = async () => {
  if (mockQuestions.value.length === 0) {
    ElMessage.warning("没有可保存的数据");
    return;
  }
  questions.value = mockQuestions.value.map(question => ({
    type: qtype.value,
    knowledge: knowledge_select.value,
    question: question.question,
    answer: question.answer,
    options: question.options,
    analysis: question.analysis
  }));
  try {
    const res = await postExamQuestions({
      questions: questions.value
    });
    ElMessage.success("保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

// 构建 PDF 内容
function buildPdfContent() {
  const container = document.createElement("div");
  container.style.padding = "10px";
  container.style.fontFamily = "Arial, sans-serif";

  if (!shuffledQuestions.value || !Array.isArray(shuffledQuestions.value)) {
    ElMessage.warning("没有可用的试题数据");
    return container;
  }

  if (Object.keys(userAnswers.value).length === 0) {
    ElMessage.warning("尚未答题，无法导出答题记录");
    return container;
  }

  shuffledQuestions.value.forEach((q, index) => {
    const questionDiv = document.createElement("div");
    questionDiv.innerHTML = `
      <h3 style="color: #2c3e50;">题目 ${index + 1}：${q.question}</h3>
      <ul style="list-style: none; padding-left: 0;">
        ${(Array.isArray(q.options) ? q.options.map((opt, i) => `<li>${String.fromCharCode(65 + i)}. ${opt.value}</li>`) : []).join("")}
      </ul>
      <p><strong>你的回答：</strong> ${userAnswers.value[index] || "未作答"}</p>
      <p><strong>正确答案：</strong> ${getOriginalAnswer(q.answer, q.options)}</p>
      <p><strong>解析：</strong> ${q.analysis}</p>
      <hr style="border: 0.5px solid #ccc;" />
    `;
    container.appendChild(questionDiv);
  });

  return container;
}

// 导出 PDF
async function exportToPDF() {
  if (!shuffledQuestions.value || shuffledQuestions.value.length === 0) {
    // ElMessage.warning("只有单选题可以导出试卷");
    return;
  }

  if (Object.keys(userAnswers.value).length === 0) {
    ElMessage.warning("尚未进行答题，无法导出答题记录");
    return;
  }

  const element = buildPdfContent();
  document.body.appendChild(element); // 临时插入 DOM

  const opt = {
    margin: 1,
    filename: "练习题报告.pdf",
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      ignoreElements: el => el.tagName === "STYLE" || el.tagName === "LINK"
    },
    jsPDF: { unit: "mm", format: "a4" },
    enableLegacyRendering: true
  };

  await html2pdf().set(opt).from(element).save();
  document.body.removeChild(element); // 清理
}

// 启动在线考试
function startOnlineExam() {
  if (qtype.value === "单选题" || qtype.value === "判断题") {
    showExerciseDialog.value = true;
  } else {
    ElMessage.warning("当前题型不支持在线考试");
  }
}

// 处理提交事件
function handleSubmitAnswers(data: { answers: Record<number, string>; correctCount: number; questions: ShuffledQuestion[] }) {
  userAnswers.value = data.answers;
  shuffledQuestions.value = data.questions; // 保留打乱后的题目用于导出
  console.log("打乱的问题:", shuffledQuestions.value);
  correctCount.value = data.correctCount;
}

// 获取原始答案对应的打乱后字母
function getOriginalAnswer(answerLetter: string, options: ShuffledQuestion["options"]) {
  // 如果是选择题且有选项
  if (options && options.length > 0) {
    const answerIndex = answerLetter.charCodeAt(0) - 65;
    const originalOption = options.find(opt => opt.originalIndex === answerIndex);
    return originalOption ? String.fromCharCode(options.indexOf(originalOption) + 65) : "未知";
  }
  // 其他题型直接返回答案
  return answerLetter;
}
</script>

<style scoped>
.mcp-view {
  max-height: 600px;
  overflow-y: auto;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.exercise-container {
  max-height: 500px;
  overflow-y: auto;
}

.question-card {
  margin-bottom: 16px;
}

.options-list {
  list-style-type: none;
  padding-left: 0;
}

.options-list li {
  margin-bottom: 8px;
}

.answer-feedback p {
  margin: 4px 0;
}

.correct {
  color: green;
  font-weight: bold;
}

.wrong {
  color: red;
  font-weight: bold;
}

.dialog-footer {
  text-align: right;
}

.pdf-question {
  page-break-inside: avoid;
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #eee;
  background-color: #fff;
}

.pdf-question h3 {
  color: #333;
}

.pdf-question ul {
  list-style-type: none;
  padding-left: 0;
}

.pdf-question li {
  margin-bottom: 5px;
}
</style>
