<template>
  <el-dialog v-model="visible" title="在线考试" width="600px">
    <p style="font-size: 24px; text-align: center">{{ timer }} 秒</p>

    <!-- 当前题目 -->
    <div class="exercise-container" v-if="shuffledQuestions.length > 0 && !submitted">
      <el-card shadow="hover" class="question-card">
        <template #header>
          <span>题目 {{ currentPage + 1 }} / {{ shuffledQuestions.length }}</span>
        </template>
        <p><strong>问题：</strong>{{ currentQuestion.question }}</p>

        <div v-if="currentQuestion.options && currentQuestion.options.length > 0">
          <p><strong>选项：</strong></p>
          <el-radio-group v-model="userAnswers[currentPage]">
            <ul class="options-list">
              <li v-for="(opt, i) in currentQuestion.options" :key="i">
                <el-radio :value="String.fromCharCode(65 + i)">
                  {{ opt.value }}
                </el-radio>
              </li>
            </ul>
          </el-radio-group>
        </div>

        <!-- 判断题 -->
        <div v-else-if="isTrueFalseQuestion(currentQuestion)">
          <el-radio-group v-model="userAnswers[currentPage]">
            <el-radio value="正确">正确</el-radio>
            <el-radio value="错误">错误</el-radio>
          </el-radio-group>
        </div>

        <!-- 简答题/编程题 -->
        <div v-else>
          <el-input v-model="userAnswers[currentPage]" :rows="4" type="textarea" placeholder="请输入你的答案" />
        </div>
      </el-card>

      <!-- 分页控制 -->
      <div class="pagination-controls">
        <el-button @click="prevQuestion" :disabled="currentPage === 0">上一题</el-button>
        <el-button @click="nextQuestion" :disabled="currentPage === shuffledQuestions.length - 1">下一题</el-button>
        <el-button v-if="currentPage === shuffledQuestions.length - 1" type="danger" @click="submitAnswers">提交答案</el-button>
      </div>
    </div>

    <!-- 提交后的结果反馈 -->
    <div v-if="submitted" class="submission-result">
      <h3>答题完成</h3>
      <p>共 {{ shuffledQuestions.length }} 道题，答对 {{ correctCount }} 道</p>
      <div v-for="(q, index) in shuffledQuestions" :key="index" class="answer-feedback">
        <p>
          <strong>题目 {{ index + 1 }}：{{ q.question }}</strong>
        </p>
        <p>
          <strong>你的回答：</strong>
          <span :class="{ correct: isCorrect(index), wrong: !isCorrect(index) }">
            {{ userAnswers[index] || "未作答" }}
          </span>
        </p>
        <p><strong>正确答案：</strong>{{ originalAnswer(q.answer, q.options) }}</p>
        <p><strong>解析：</strong>{{ q.analysis }}</p>
      </div>
      <br />
      <el-button type="primary" @click="resetExercise">重新练习</el-button>
    </div>

    <p v-if="shuffledQuestions.length === 0">暂无可用试题，请先在结果页面生成测试题。</p>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { Question, ShuffledQuestion, Option } from "./types";

const props = defineProps<{
  modelValue: boolean;
  questions: Question[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "submit", payload: { answers: Record<number, string>; correctCount: number }): void;
}>();

// 控制 dialog 显示
const visible = ref(false);

// 倒计时
const timer = ref<number>(300);
let intervalId: number | null = null;

// 打乱后的问题列表
const shuffledQuestions = ref<ShuffledQuestion[]>([]);

// 用户作答记录
const userAnswers = ref<Record<number, string>>({});

// 是否已提交答案
const submitted = ref<boolean>(false);

// 正确题数
const correctCount = ref<number>(0);

// 当前页码（从0开始）
const currentPage = ref<number>(0);

// 当前题目
const currentQuestion = ref<ShuffledQuestion>({
  question: "",
  answer: "",
  analysis: "",
  options: []
});

// 初始化当前题目
function initCurrentQuestion() {
  if (shuffledQuestions.value.length > 0) {
    currentQuestion.value = shuffledQuestions.value[currentPage.value];
  }
}

// 判断是否是判断题
function isTrueFalseQuestion(question: ShuffledQuestion): boolean {
  return !question.options || question.options.length === 0;
}

// 上一题
function prevQuestion() {
  if (currentPage.value > 0) {
    currentPage.value--;
    initCurrentQuestion();
  }
}

// 下一题
function nextQuestion() {
  if (currentPage.value < shuffledQuestions.value.length - 1) {
    currentPage.value++;
    initCurrentQuestion();
  }
}

// 打乱数组并保留原始索引
function shuffleArray(array: string[]): Option[] {
  const indexed = array.map((val, idx) => ({ value: val, originalIndex: idx }));
  for (let i = indexed.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [indexed[i], indexed[j]] = [indexed[j], indexed[i]];
  }
  return indexed;
}

// 初始化打乱后的问题列表
function initShuffledQuestions() {
  shuffledQuestions.value = props.questions.map(q => ({
    ...q,
    options: shuffleArray([...q.options])
  }));
  currentPage.value = 0;
  initCurrentQuestion();
}

// 开始倒计时
function startTimer() {
  if (intervalId) clearInterval(intervalId);
  timer.value = 300;
  intervalId = window.setInterval(() => {
    timer.value--;
    if (timer.value <= 0 && intervalId) {
      clearInterval(intervalId);
      submitAnswers(); // 时间到自动提交
    }
  }, 1000);
}

// 判断是否答对
function isCorrect(index: number): boolean {
  const selectedLetter = userAnswers.value[index]; // 如 'B'
  if (!selectedLetter) return false;

  const questionType = getQuestionType(shuffledQuestions.value[index]);

  // 选择题
  if (questionType === "multiple-choice") {
    const selectedIndex = selectedLetter.charCodeAt(0) - 65; // B -> 1
    const selectedOption = shuffledQuestions.value[index]?.options[selectedIndex];

    if (!selectedOption) return false;

    const correctAnswerIndex = shuffledQuestions.value[index].answer.charCodeAt(0) - 65; // B -> 1
    const correctOriginalIndex = props.questions[index].options.findIndex((_, i) => i === correctAnswerIndex);

    return selectedOption.originalIndex === correctOriginalIndex;
  } else {
    return selectedLetter === originalAnswer(shuffledQuestions.value[index].answer, shuffledQuestions.value[index].options);
  }
}

// 获取题型
function getQuestionType(question: ShuffledQuestion): string {
  if (question.options && question.options.length === 0) {
    return "true-false"; // 判断题
  } else if (question.options && question.options.length > 0) {
    return "multiple-choice"; // 选择题
  } else {
    return "open-ended"; // 简答题/编程题
  }
}

// 获取原始答案字母
function originalAnswer(answer: string, options: Option[]): string {
  // 如果是选择题且有选项
  if (options && options.length > 0) {
    const correctIndex = answer.charCodeAt(0) - 65;
    return String.fromCharCode(65 + options.findIndex(opt => opt.originalIndex === correctIndex));
  }
  // 其他题型直接返回答案
  return answer;
}

// 提交答案并反馈
async function submitAnswers() {
  try {
    await ElMessageBox.confirm("确定要提交吗？", "提示");
  } catch {
    return;
  }

  let count = 0;
  for (let i = 0; i < shuffledQuestions.value.length; i++) {
    if (isCorrect(i)) count++;
  }

  correctCount.value = count;
  submitted.value = true;

  emit("submit", {
    answers: userAnswers.value,
    correctCount: correctCount.value,
    questions: shuffledQuestions.value
  });

  ElMessage.success(`答题完成，共答对 ${count} 题`);
}

// 重置状态
function resetState() {
  userAnswers.value = {};
  submitted.value = false;
  correctCount.value = 0;
  currentPage.value = 0;
}

// 重新开始考试
function resetExercise() {
  resetState();
  initShuffledQuestions();
  startTimer();
  initCurrentQuestion();
}

// 控制显示状态
watch(
  () => props.modelValue,
  newVal => {
    visible.value = newVal;
    if (newVal) {
      initShuffledQuestions();
      startTimer();
      initCurrentQuestion();
    }
  }
);

// 关闭 Dialog 时通知父组件
watch(
  () => visible.value,
  newVal => {
    emit("update:modelValue", newVal);
  }
);
</script>

<style scoped>
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

.pagination-controls {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.submission-result {
  text-align: left;
  font-size: 16px;
  line-height: 1.6;
}

.answer-feedback {
  margin-top: 10px;
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.correct {
  color: green;
  font-weight: bold;
}

.wrong {
  color: red;
  font-weight: bold;
}
</style>
